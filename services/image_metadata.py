"""Leitura e normalização de metadados de imagens.

Este módulo não depende da interface de nós do ComfyUI. Ele concentra a
extração de PNG, EXIF e formatos de metadados usados por geradores de imagem.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from PIL import ExifTags, Image


def to_text(value: Any) -> Any:
    """Converte valores de metadados em uma representação textual segura."""
    if isinstance(value, bytes):
        for encoding in ("utf-8", "latin-1"):
            try:
                return value.decode(encoding)
            except UnicodeDecodeError:
                continue
        return repr(value)

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def json_or_text(value: Any) -> Any:
    """Desserializa valores JSON quando o conteúdo parecer ser JSON válido."""
    value = to_text(value)
    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if not stripped or stripped[0] not in "{[\"0123456789-tnf":
        return value

    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return value


def json_safe(value: Any) -> Any:
    """Normaliza recursivamente valores para que possam ser serializados em JSON."""
    if isinstance(value, dict):
        return {str(to_text(key)): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]

    value = to_text(value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def extract_png_comf_chunks(file_path: str | Path) -> dict[str, str]:
    """Extrai chunks PNG ``comf`` adicionados pelo ComfyUI."""
    file_path = Path(file_path)
    if file_path.suffix.lower() != ".png":
        return {}

    chunks: dict[str, str] = {}
    with file_path.open("rb") as image_file:
        if image_file.read(8) != b"\x89PNG\r\n\x1a\n":
            return chunks

        while True:
            length_bytes = image_file.read(4)
            if len(length_bytes) != 4:
                break

            length = int.from_bytes(length_bytes, "big")
            chunk_type = image_file.read(4)
            data = image_file.read(length)
            image_file.read(4)  # CRC

            if chunk_type == b"comf" and b"\x00" in data:
                name_bytes, payload_bytes = data.split(b"\x00", 1)
                chunks[name_bytes.decode("latin-1")] = payload_bytes.decode("latin-1")

            if chunk_type == b"IEND":
                break

    return chunks


def extract_image_metadata(file_path: str | Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Retorna os metadados normalizados e os valores originais da imagem."""
    file_path = Path(file_path)
    with Image.open(file_path) as image:
        file_info = {
            "format": image.format,
            "width": image.size[0],
            "height": image.size[1],
            "mode": image.mode,
        }
        raw: dict[str, Any] = {}

        if hasattr(image, "text"):
            raw.update({str(key): to_text(value) for key, value in image.text.items()})

        for key, value in image.info.items():
            if key != "exif":
                raw[str(key)] = to_text(value)

        raw.update(extract_png_comf_chunks(file_path))

        exif = image.getexif()
        if exif:
            exif_data = {}
            for tag_id, value in exif.items():
                name = ExifTags.TAGS.get(tag_id, tag_id)
                value = to_text(value)
                exif_data[str(name)] = value

                if isinstance(value, str) and ":" in value:
                    key, text = value.split(":", 1)
                    if key.strip():
                        raw[key.strip()] = text.strip()
            raw["exif"] = exif_data

    if not raw:
        return {}, {}

    metadata = {key: json_or_text(value) for key, value in raw.items()}
    normalized = {"file": file_info, "metadata": json_safe(metadata), "raw": json_safe(raw)}
    return normalized, metadata


def set_if_missing(details: dict[str, Any], key: str, value: Any) -> None:
    if value not in (None, "") and key not in details:
        details[key] = value


def as_int(value: Any, default: int = 0) -> int:
    if value in (None, ""):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)

    match = re.search(r"-?\d+", str(value))
    return int(match.group(0)) if match else default


def as_float(value: Any, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    if isinstance(value, (int, float)):
        return float(value)

    match = re.search(r"-?\d+(?:\.\d+)?", str(value))
    return float(match.group(0)) if match else default


def parse_parameters_text(text: Any) -> dict[str, Any]:
    """Lê o bloco de parâmetros normalmente gravado pelo A1111 e derivados."""
    details: dict[str, Any] = {}
    if not isinstance(text, str) or not text.strip():
        return details

    steps_match = re.search(r"(?:^|\n)Steps:\s*", text)
    negative_match = re.search(r"(?:^|\n)Negative prompt:\s*", text)
    prompt_end = negative_match.start() if negative_match else steps_match.start() if steps_match else len(text)
    prompt = text[:prompt_end].strip()
    if prompt:
        details["prompt"] = prompt

    if negative_match:
        negative_start = negative_match.end()
        negative_end = steps_match.start() if steps_match and steps_match.start() > negative_start else len(text)
        negative_prompt = text[negative_start:negative_end].strip()
        if negative_prompt:
            details["negative_prompt"] = negative_prompt

    key_mapping = {
        "steps": "steps",
        "sampler": "sampler",
        "scheduler": "scheduler",
        "cfg scale": "cfg",
        "cfg": "cfg",
        "seed": "seed",
        "size": "size",
        "model": "model",
        "checkpoint": "model",
    }
    for key, value in re.findall(r"([A-Za-z][A-Za-z0-9 _/-]*):\s*([^,\n]+)", text):
        target_key = key_mapping.get(key.strip().lower())
        if target_key:
            set_if_missing(details, target_key, value.strip())

    return details


def is_prompt_text_node(class_type: str) -> bool:
    class_type = class_type.lower()
    return "cliptextencode" in class_type or "textencode" in class_type or "prompt" in class_type


def collect_comfy_prompt_details(prompt_graph: Any) -> dict[str, Any]:
    """Extrai detalhes do workflow serializado pelo ComfyUI."""
    details: dict[str, Any] = {}
    prompts: list[str] = []
    negative_prompts: list[str] = []
    models: list[str] = []
    if not isinstance(prompt_graph, dict):
        return details

    for node in prompt_graph.values():
        if not isinstance(node, dict) or not isinstance(node.get("inputs", {}), dict):
            continue

        inputs = node["inputs"]
        class_type = str(node.get("class_type", ""))
        meta = node.get("_meta", {})
        title = str(meta.get("title", "")) if isinstance(meta, dict) else ""
        prompt_target = negative_prompts if "negative" in f"{class_type} {title}".lower() else prompts

        if is_prompt_text_node(class_type):
            for key in ("text", "prompt", "positive", "clip_l", "t5xxl"):
                value = inputs.get(key)
                if isinstance(value, str) and value.strip():
                    prompt_target.append(value.strip())

        width, height = inputs.get("width"), inputs.get("height")
        if width and height:
            set_if_missing(details, "size", f"{width}x{height}")
            set_if_missing(details, "width", width)
            set_if_missing(details, "height", height)

        for key, value in inputs.items():
            key_lower = key.lower()
            if key_lower in ("seed", "noise_seed"):
                set_if_missing(details, "seed", value)
            elif key_lower == "sampler_name":
                set_if_missing(details, "sampler", value)
            elif key_lower == "scheduler":
                set_if_missing(details, "scheduler", value)
            elif key_lower == "steps":
                set_if_missing(details, "steps", value)
            elif key_lower in ("cfg", "guidance"):
                set_if_missing(details, "cfg", value)
            elif isinstance(value, str) and (key_lower.endswith("_name") or key_lower in ("ckpt_name", "checkpoint", "model")):
                models.append(value)

    if prompts:
        details["prompt"] = max(prompts, key=len)
    if negative_prompts:
        details["negative_prompt"] = max(negative_prompts, key=len)
    if models:
        details["model"] = ", ".join(dict.fromkeys(models))
    return details


def collect_flat_metadata_details(metadata: dict[str, Any]) -> dict[str, Any]:
    details: dict[str, Any] = {}
    for source_keys, target_key in (
        (("Prompt", "prompt", "positive", "Positive prompt", "Positive Prompt"), "prompt"),
        (("Negative prompt", "Negative Prompt", "negative", "negative_prompt"), "negative_prompt"),
        (("Model", "model", "checkpoint", "Checkpoint", "ckpt_name", "unet_name"), "model"),
    ):
        for key in source_keys:
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                set_if_missing(details, target_key, value.strip())

    for source_key, target_key in (
        ("sampler", "sampler"), ("Sampler", "sampler"), ("scheduler", "scheduler"),
        ("Scheduler", "scheduler"), ("steps", "steps"), ("Steps", "steps"),
        ("cfg", "cfg"), ("CFG scale", "cfg"), ("seed", "seed"), ("Seed", "seed"),
        ("size", "size"), ("Size", "size"), ("Software", "software"), ("software", "software"),
    ):
        value = metadata.get(source_key)
        if isinstance(value, (str, int, float)) and str(value).strip():
            set_if_missing(details, target_key, value)
    return details


def collect_details(normalized: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    """Consolida dados de diferentes convenções de metadados em um só formato."""
    details = collect_flat_metadata_details(metadata)
    for key in ("parameters", "Parameters"):
        details.update({key: value for key, value in parse_parameters_text(metadata.get(key)).items() if key not in details})

    prompt_graph = metadata.get("prompt")
    if isinstance(prompt_graph, dict):
        details.update({key: value for key, value in collect_comfy_prompt_details(prompt_graph).items() if key not in details})

    file_info = normalized.get("file", {})
    if file_info:
        set_if_missing(details, "format", file_info.get("format"))
        set_if_missing(details, "size", f"{file_info.get('width')}x{file_info.get('height')}")
        set_if_missing(details, "width", file_info.get("width"))
        set_if_missing(details, "height", file_info.get("height"))
        set_if_missing(details, "mode", file_info.get("mode"))
    return details


def format_summary(normalized: dict[str, Any], details: dict[str, Any]) -> str:
    if not normalized:
        return "Nenhum metadado encontrado."

    lines = ["Metadados principais"]
    for label, key in (
        ("Formato", "format"), ("Dimensoes", "size"), ("Modo de cor", "mode"),
        ("Software", "software"), ("Modelo", "model"), ("Sampler", "sampler"),
        ("Scheduler", "scheduler"), ("Steps", "steps"), ("CFG", "cfg"), ("Seed", "seed"),
    ):
        value = details.get(key)
        if value not in (None, ""):
            lines.append(f"{label}: {value}")

    if details.get("prompt"):
        lines.extend(["", "Prompt:", str(details["prompt"])])
    if details.get("negative_prompt"):
        lines.extend(["", "Negative prompt:", str(details["negative_prompt"])])
    return "\n".join(lines)


def read_image_metadata(file_path: str | Path) -> dict[str, Any]:
    """Lê uma imagem e retorna resultados prontos para consumo pelos nós."""
    normalized, metadata = extract_image_metadata(file_path)
    if not normalized:
        return {"details": {}, "metadata_text": "Nenhum metadado encontrado.", "metadata_json": "{}", "prompt": "", "negative_prompt": ""}

    details = collect_details(normalized, metadata)
    return {
        "details": details,
        "metadata_text": format_summary(normalized, details),
        "metadata_json": json.dumps(
            normalized,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        ),
        "prompt": str(details.get("prompt", "")),
        "negative_prompt": str(details.get("negative_prompt", "")),
    }
