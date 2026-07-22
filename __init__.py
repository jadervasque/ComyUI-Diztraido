import hashlib
import json
import os
import re
import secrets

from PIL import ExifTags, Image

import folder_paths

try:
    import comfy.samplers

    SAMPLER_RETURN_TYPE = comfy.samplers.KSampler.SAMPLERS
    SCHEDULER_RETURN_TYPE = comfy.samplers.KSampler.SCHEDULERS
except ImportError:
    SAMPLER_RETURN_TYPE = "STRING"
    SCHEDULER_RETURN_TYPE = "STRING"


def _to_text(value):
    if isinstance(value, bytes):
        for encoding in ("utf-8", "latin-1"):
            try:
                return value.decode(encoding)
            except UnicodeDecodeError:
                pass
        return repr(value)

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    return str(value)


def _json_or_text(value):
    value = _to_text(value)
    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if not stripped:
        return value

    if stripped[0] not in "{[\"0123456789-tnf":
        return value

    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return value


def _json_safe(value):
    if isinstance(value, dict):
        return {str(_to_text(k)): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]

    value = _to_text(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _extract_png_comf_chunks(file_path):
    if not file_path.lower().endswith(".png"):
        return {}

    chunks = {}
    with open(file_path, "rb") as f:
        if f.read(8) != b"\x89PNG\r\n\x1a\n":
            return chunks

        while True:
            length_bytes = f.read(4)
            if len(length_bytes) != 4:
                break

            length = int.from_bytes(length_bytes, "big")
            chunk_type = f.read(4)
            data = f.read(length)
            f.read(4)

            if chunk_type == b"comf" and b"\x00" in data:
                name_bytes, payload_bytes = data.split(b"\x00", 1)
                name = name_bytes.decode("latin-1")
                payload = payload_bytes.decode("latin-1")
                chunks[name] = payload

            if chunk_type == b"IEND":
                break

    return chunks


def _extract_image_metadata(file_path):
    with Image.open(file_path) as img:
        file_info = {
            "format": img.format,
            "width": img.size[0],
            "height": img.size[1],
            "mode": img.mode,
        }

        raw = {}

        if hasattr(img, "text"):
            raw.update({str(k): _to_text(v) for k, v in img.text.items()})

        for key, value in img.info.items():
            if key == "exif":
                continue
            raw[str(key)] = _to_text(value)

        raw.update(_extract_png_comf_chunks(file_path))

        exif = img.getexif()
        if exif:
            exif_data = {}
            for tag_id, value in exif.items():
                name = ExifTags.TAGS.get(tag_id, tag_id)
                value = _to_text(value)
                exif_data[str(name)] = value

                if isinstance(value, str) and ":" in value:
                    key, text = value.split(":", 1)
                    key = key.strip()
                    if key:
                        raw[key] = text.strip()

            raw["exif"] = exif_data

    if not raw:
        return {}, {}

    metadata = {key: _json_or_text(value) for key, value in raw.items()}
    return {"file": file_info, "metadata": _json_safe(metadata), "raw": _json_safe(raw)}, metadata


def _set_if_missing(details, key, value):
    if value not in (None, "") and key not in details:
        details[key] = value


def _as_int(value, default=0):
    if value in (None, ""):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)

    match = re.search(r"-?\d+", str(value))
    if not match:
        return default
    return int(match.group(0))


def _as_float(value, default=0.0):
    if value in (None, ""):
        return default
    if isinstance(value, (int, float)):
        return float(value)

    match = re.search(r"-?\d+(?:\.\d+)?", str(value))
    if not match:
        return default
    return float(match.group(0))


def _parse_parameters_text(text):
    details = {}
    if not isinstance(text, str) or not text.strip():
        return details

    steps_match = re.search(r"(?:^|\n)Steps:\s*", text)
    negative_match = re.search(r"(?:^|\n)Negative prompt:\s*", text)

    prompt_end = len(text)
    if negative_match:
        prompt_end = negative_match.start()
    elif steps_match:
        prompt_end = steps_match.start()

    prompt = text[:prompt_end].strip()
    if prompt:
        details["prompt"] = prompt

    if negative_match:
        negative_start = negative_match.end()
        negative_end = steps_match.start() if steps_match and steps_match.start() > negative_start else len(text)
        negative_prompt = text[negative_start:negative_end].strip()
        if negative_prompt:
            details["negative_prompt"] = negative_prompt

    for key, value in re.findall(r"([A-Za-z][A-Za-z0-9 _/-]*):\s*([^,\n]+)", text):
        normalized_key = key.strip().lower()
        normalized_value = value.strip()
        if normalized_key == "steps":
            _set_if_missing(details, "steps", normalized_value)
        elif normalized_key == "sampler":
            _set_if_missing(details, "sampler", normalized_value)
        elif normalized_key == "scheduler":
            _set_if_missing(details, "scheduler", normalized_value)
        elif normalized_key in ("cfg scale", "cfg"):
            _set_if_missing(details, "cfg", normalized_value)
        elif normalized_key == "seed":
            _set_if_missing(details, "seed", normalized_value)
        elif normalized_key == "size":
            _set_if_missing(details, "size", normalized_value)
        elif normalized_key in ("model", "checkpoint"):
            _set_if_missing(details, "model", normalized_value)

    return details


def _is_prompt_text_node(class_type):
    class_type = class_type.lower()
    return "cliptextencode" in class_type or "textencode" in class_type or "prompt" in class_type


def _collect_comfy_prompt_details(prompt_graph):
    details = {}
    prompts = []
    negative_prompts = []
    models = []

    if not isinstance(prompt_graph, dict):
        return details

    for node in prompt_graph.values():
        if not isinstance(node, dict):
            continue

        inputs = node.get("inputs", {})
        if not isinstance(inputs, dict):
            continue

        class_type = str(node.get("class_type", ""))
        meta = node.get("_meta", {})
        title = str(meta.get("title", "")) if isinstance(meta, dict) else ""
        prompt_target = negative_prompts if "negative" in "{} {}".format(class_type, title).lower() else prompts

        if _is_prompt_text_node(class_type):
            for key in ("text", "prompt", "positive", "clip_l", "t5xxl"):
                value = inputs.get(key)
                if isinstance(value, str) and value.strip():
                    prompt_target.append(value.strip())

        width = inputs.get("width")
        height = inputs.get("height")
        if width and height:
            _set_if_missing(details, "size", "{}x{}".format(width, height))
            _set_if_missing(details, "width", width)
            _set_if_missing(details, "height", height)

        for key, value in inputs.items():
            key_lower = key.lower()

            if key_lower in ("seed", "noise_seed"):
                _set_if_missing(details, "seed", value)
            elif key_lower == "sampler_name":
                _set_if_missing(details, "sampler", value)
            elif key_lower == "scheduler":
                _set_if_missing(details, "scheduler", value)
            elif key_lower == "steps":
                _set_if_missing(details, "steps", value)
            elif key_lower in ("cfg", "guidance"):
                _set_if_missing(details, "cfg", value)
            elif isinstance(value, str) and (key_lower.endswith("_name") or key_lower in ("ckpt_name", "checkpoint", "model")):
                models.append(value)

    if prompts:
        details["prompt"] = max(prompts, key=len)

    if negative_prompts:
        details["negative_prompt"] = max(negative_prompts, key=len)

    if models:
        details["model"] = ", ".join(dict.fromkeys(models))

    return details


def _collect_flat_metadata_details(metadata):
    details = {}
    prompt_keys = ("Prompt", "prompt", "positive", "Positive prompt", "Positive Prompt")
    negative_keys = ("Negative prompt", "Negative Prompt", "negative", "negative_prompt")
    model_keys = ("Model", "model", "checkpoint", "Checkpoint", "ckpt_name", "unet_name")

    for key in prompt_keys:
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            _set_if_missing(details, "prompt", value.strip())

    for key in negative_keys:
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            _set_if_missing(details, "negative_prompt", value.strip())

    for key in model_keys:
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            _set_if_missing(details, "model", value.strip())

    for source_key, target_key in (
        ("sampler", "sampler"),
        ("Sampler", "sampler"),
        ("scheduler", "scheduler"),
        ("Scheduler", "scheduler"),
        ("steps", "steps"),
        ("Steps", "steps"),
        ("cfg", "cfg"),
        ("CFG scale", "cfg"),
        ("seed", "seed"),
        ("Seed", "seed"),
        ("size", "size"),
        ("Size", "size"),
        ("Software", "software"),
        ("software", "software"),
    ):
        value = metadata.get(source_key)
        if isinstance(value, (str, int, float)) and str(value).strip():
            _set_if_missing(details, target_key, value)

    return details


def _collect_details(normalized, metadata):
    details = {}
    details.update(_collect_flat_metadata_details(metadata))

    for key in ("parameters", "Parameters"):
        details.update({k: v for k, v in _parse_parameters_text(metadata.get(key)).items() if k not in details})

    prompt_graph = metadata.get("prompt")
    if isinstance(prompt_graph, dict):
        details.update({k: v for k, v in _collect_comfy_prompt_details(prompt_graph).items() if k not in details})

    file_info = normalized.get("file", {})
    if file_info:
        _set_if_missing(details, "format", file_info.get("format"))
        _set_if_missing(details, "size", "{}x{}".format(file_info.get("width"), file_info.get("height")))
        _set_if_missing(details, "width", file_info.get("width"))
        _set_if_missing(details, "height", file_info.get("height"))
        _set_if_missing(details, "mode", file_info.get("mode"))

    return details


def _format_summary(normalized, details):
    if not normalized:
        return "Nenhum metadado encontrado."

    lines = ["Metadados principais"]

    for label, key in (
        ("Formato", "format"),
        ("Dimensoes", "size"),
        ("Modo de cor", "mode"),
        ("Software", "software"),
        ("Modelo", "model"),
        ("Sampler", "sampler"),
        ("Scheduler", "scheduler"),
        ("Steps", "steps"),
        ("CFG", "cfg"),
        ("Seed", "seed"),
    ):
        value = details.get(key)
        if value not in (None, ""):
            lines.append("{}: {}".format(label, value))

    if details.get("prompt"):
        lines.extend(["", "Prompt:", str(details["prompt"])])

    if details.get("negative_prompt"):
        lines.extend(["", "Negative prompt:", str(details["negative_prompt"])])

    return "\n".join(lines)


def _image_input_types(include_mode):
    input_dir = folder_paths.get_input_directory()
    files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    files = folder_paths.filter_files_content_types(files, ["image"])
    required = {"image": (sorted(files), {"image_upload": True})}
    if include_mode:
        required["mode"] = (["principais", "todos"], {"default": "principais"})
    return {"required": required}


def _read_image_metadata(image, mode="principais"):
    image_path = folder_paths.get_annotated_filepath(image)
    normalized, metadata = _extract_image_metadata(image_path)

    if not normalized:
        return {
            "details": {},
            "metadata_text": "Nenhum metadado encontrado.",
            "metadata_json": "{}",
            "prompt": "",
            "negative_prompt": "",
        }

    metadata_json = json.dumps(normalized, ensure_ascii=False, indent=2, sort_keys=True)
    details = _collect_details(normalized, metadata)
    metadata_text = metadata_json if mode == "todos" else _format_summary(normalized, details)
    return {
        "details": details,
        "metadata_text": metadata_text,
        "metadata_json": metadata_json,
        "prompt": str(details.get("prompt", "")),
        "negative_prompt": str(details.get("negative_prompt", "")),
    }


class _DiztraidoImageMetadataBase:
    CATEGORY = "Diztraido/image"

    @classmethod
    def IS_CHANGED(cls, image, mode="principais"):
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, "rb") as f:
            m.update(f.read())
        return "{}:{}".format(mode, m.digest().hex())

    @classmethod
    def VALIDATE_INPUTS(cls, image, mode="principais"):
        if not folder_paths.exists_annotated_filepath(image):
            return "Invalid image file: {}".format(image)

        return True


class DiztraidoImageMetadataReaderBasic(_DiztraidoImageMetadataBase):
    @classmethod
    def INPUT_TYPES(cls):
        return _image_input_types(True)

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("metadata_text", "prompt", "metadata_json")
    FUNCTION = "read_metadata"

    def read_metadata(self, image, mode="principais"):
        result = _read_image_metadata(image, mode)
        return {"ui": {"text": [result["metadata_text"]]}, "result": (result["metadata_text"], result["prompt"], result["metadata_json"])}


class DiztraidoImageMetadataReaderIntermediate(_DiztraidoImageMetadataBase):
    @classmethod
    def INPUT_TYPES(cls):
        return _image_input_types(True)

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("metadata_text", "prompt", "negative_prompt", "model", "sampler_name", "scheduler", "metadata_json")
    FUNCTION = "read_metadata"

    def read_metadata(self, image, mode="principais"):
        result = _read_image_metadata(image, mode)
        details = result["details"]
        return {
            "ui": {"text": [result["metadata_text"]]},
            "result": (
                result["metadata_text"],
                result["prompt"],
                result["negative_prompt"],
                str(details.get("model", "")),
                str(details.get("sampler", "")),
                str(details.get("scheduler", "")),
                result["metadata_json"],
            ),
        }


class DiztraidoImageMetadataReaderAdvanced(_DiztraidoImageMetadataBase):
    @classmethod
    def INPUT_TYPES(cls):
        return _image_input_types(False)

    RETURN_TYPES = (
        "STRING",
        "STRING",
        "INT",
        "INT",
        "FLOAT",
        SAMPLER_RETURN_TYPE,
        SCHEDULER_RETURN_TYPE,
        "STRING",
        "INT",
        "INT",
        "STRING",
        "STRING",
    )
    RETURN_NAMES = (
        "prompt",
        "negative_prompt",
        "seed",
        "steps",
        "cfg",
        "sampler_name",
        "scheduler",
        "model",
        "width",
        "height",
        "metadata_text",
        "metadata_json",
    )
    FUNCTION = "read_metadata"

    def read_metadata(self, image):
        result = _read_image_metadata(image, "principais")
        details = result["details"]
        return {
            "ui": {"text": [result["metadata_text"]]},
            "result": (
                result["prompt"],
                result["negative_prompt"],
                _as_int(details.get("seed")),
                _as_int(details.get("steps")),
                _as_float(details.get("cfg")),
                str(details.get("sampler", "")),
                str(details.get("scheduler", "")),
                str(details.get("model", "")),
                _as_int(details.get("width")),
                _as_int(details.get("height")),
                result["metadata_text"],
                result["metadata_json"],
            ),
        }


DiztraidoImageMetadataReader = DiztraidoImageMetadataReaderBasic


class BackendRandomSeed:
    """
    Gera uma nova seed no backend em cada execução real do workflow.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "maximum": (
                    "INT",
                    {
                        "default": 9_223_372_036_854_775_807,
                        "min": 1,
                        "max": 9_223_372_036_854_775_807,
                    },
                ),
            }
        }

    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("seed", "seed_text")
    FUNCTION = "generate"
    CATEGORY = "utils/random"

    @classmethod
    def IS_CHANGED(cls, maximum):
        return float("nan")

    def generate(self, maximum):
        seed = secrets.randbelow(maximum)
        return seed, str(seed)


NODE_CLASS_MAPPINGS = {
    "DiztraidoImageMetadataReader": DiztraidoImageMetadataReaderBasic,
    "DiztraidoImageMetadataReaderBasic": DiztraidoImageMetadataReaderBasic,
    "DiztraidoImageMetadataReaderIntermediate": DiztraidoImageMetadataReaderIntermediate,
    "DiztraidoImageMetadataReaderAdvanced": DiztraidoImageMetadataReaderAdvanced,
    "BackendRandomSeed": BackendRandomSeed,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DiztraidoImageMetadataReader": "Diztraido: Image Metadata Reader",
    "DiztraidoImageMetadataReaderBasic": "Diztraido: Metadata Reader Basic",
    "DiztraidoImageMetadataReaderIntermediate": "Diztraido: Metadata Reader Intermediate",
    "DiztraidoImageMetadataReaderAdvanced": "Diztraido: Metadata Reader Advanced",
    "BackendRandomSeed": "Backend Random Seed",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
