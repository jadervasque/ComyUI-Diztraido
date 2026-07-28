"""Testes da composicao do pipeline de processamento."""

from __future__ import annotations

import unittest

from services.composed_pipelines import normalize_processing_params, run_processing_pipeline


class _NodeOutputLike:
    def __init__(self, *args):
        self.args = args

    @property
    def result(self):
        return self.args if self.args else None


class _RandomNoiseNode:
    FUNCTION = "build"

    def build(self, noise_seed):
        return (f"noise({noise_seed})",)


class _CFGGuiderNode:
    FUNCTION = "build"

    def build(self, model, positive, negative, cfg):
        return (f"guider({model}|{positive}|{negative}|{cfg})",)


class _CFGGuiderListAwareNode:
    FUNCTION = "build"

    def build(self, model, positive, negative, cfg):
        if not isinstance(positive, list) or not isinstance(negative, list):
            raise AssertionError("conditionings deveriam permanecer listas")
        if len(positive) < 2 or len(positive[0]) != 2:
            raise AssertionError("positive foi truncado ou corrompido")
        return ("guider-ok",)


class _CFGGuiderNodeOutputAwareNode:
    FUNCTION = "build"

    def build(self, model, positive, negative, cfg):
        if not isinstance(positive, list):
            raise AssertionError("positive deveria ter sido extraido do NodeOutput")
        return _NodeOutputLike("guider-node-output-ok")


class _KSamplerSelectNode:
    FUNCTION = "pick"

    def pick(self, sampler_name):
        return (f"sampler({sampler_name})",)


class _Flux2SchedulerNode:
    FUNCTION = "schedule"

    def schedule(self, steps, width, height):
        return (f"sigmas({steps}|{width}|{height})",)


class _EmptyLatentNode:
    FUNCTION = "create"

    def create(self, width, height, batch_size):
        return (f"latent({width}|{height}|{batch_size})",)


class _SamplerAdvancedNode:
    FUNCTION = "sample"

    def sample(self, noise, guider, sampler, sigmas, latent_image):
        return (f"sampled({noise}|{guider}|{sampler}|{sigmas}|{latent_image})",)


class _VAEDecodeNode:
    FUNCTION = "decode"

    def decode(self, samples, vae):
        return (f"image({samples}|{vae})",)


def _factory_with_guider(guider_cls, calls=None):
    mapping = {
        "RandomNoise": _RandomNoiseNode,
        "CFGGuider": guider_cls,
        "KSamplerSelect": _KSamplerSelectNode,
        "Flux2Scheduler": _Flux2SchedulerNode,
        "EmptyFlux2LatentImage": _EmptyLatentNode,
        "SamplerCustomAdvanced": _SamplerAdvancedNode,
        "VAEDecode": _VAEDecodeNode,
    }

    def factory(name):
        if calls is not None:
            calls.append(name)
        return mapping[name]()

    return factory


class ComposedProcessingTests(unittest.TestCase):
    def test_normalizes_params(self):
        params = normalize_processing_params(
            noise_seed="5",
            sampler_name="",
            steps=0,
            cfg="4.5",
            width=-1,
            height=99999,
            batch_size="0",
        )
        self.assertEqual(params["noise_seed"], 5)
        self.assertEqual(params["sampler_name"], "euler")
        self.assertEqual(params["steps"], 1)
        self.assertEqual(params["cfg"], 4.5)
        self.assertEqual(params["width"], 8)
        self.assertEqual(params["height"], 16384)
        self.assertEqual(params["batch_size"], 1)

    def test_runs_cfg_pipeline_and_returns_image_and_latent(self):
        image, latent = run_processing_pipeline(
            model="m0",
            positive="p0",
            negative="n0",
            vae="v0",
            noise_seed=42,
            sampler_name="euler",
            steps=50,
            cfg=4.0,
            width=1024,
            height=768,
            batch_size=1,
            node_factory=_factory_with_guider(_CFGGuiderNode),
        )

        expected_latent = (
            "sampled(noise(42)|guider(m0|p0|n0|4.0)|sampler(euler)|"
            "sigmas(50|1024|768)|latent(1024|768|1))"
        )
        self.assertEqual(latent, expected_latent)
        self.assertEqual(image, f"image({expected_latent}|v0)")

    def test_skips_vae_decode_when_image_is_not_requested(self):
        calls = []
        image, latent = run_processing_pipeline(
            model="m0",
            positive="p0",
            negative="n0",
            vae=None,
            noise_seed=42,
            sampler_name="euler",
            steps=50,
            cfg=4.0,
            width=1024,
            height=768,
            batch_size=1,
            decode_image=False,
            node_factory=_factory_with_guider(_CFGGuiderNode, calls),
        )
        self.assertIsNone(image)
        self.assertTrue(latent.startswith("sampled("))
        self.assertNotIn("VAEDecode", calls)

    def test_preserves_conditioning_list_structure_for_cfg_guider(self):
        positive = [["embed", {"a": 1}], ["embed2", {"b": 2}]]
        negative = [["neg", {"c": 3}]]
        image, _ = run_processing_pipeline(
            model="m0",
            positive=positive,
            negative=negative,
            vae="v0",
            noise_seed=42,
            sampler_name="euler",
            steps=50,
            cfg=4.0,
            width=1024,
            height=768,
            batch_size=1,
            node_factory=_factory_with_guider(_CFGGuiderListAwareNode),
        )
        self.assertIn("guider-ok", image)

    def test_extracts_native_node_output_before_cfg_guider(self):
        positive = [["embed", {"a": 1}]]
        image, _ = run_processing_pipeline(
            model="m0",
            positive=positive,
            negative=[["neg", {"b": 2}]],
            vae="v0",
            noise_seed=42,
            sampler_name="euler",
            steps=50,
            cfg=4.0,
            width=1024,
            height=768,
            batch_size=1,
            node_factory=_factory_with_guider(_CFGGuiderNodeOutputAwareNode),
        )
        self.assertIn("guider-node-output-ok", image)


if __name__ == "__main__":
    unittest.main()
