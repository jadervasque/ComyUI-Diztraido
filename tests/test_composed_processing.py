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


class _BasicGuiderNode:
    FUNCTION = "build"

    def build(self, model, conditioning):
        return (f"guider({model}|{conditioning})",)


class _BasicGuiderListAwareNode:
    FUNCTION = "build"

    def build(self, model, conditioning):
        if not isinstance(conditioning, list):
            raise AssertionError("conditioning deveria permanecer lista")
        if len(conditioning) < 2 or len(conditioning[0]) != 2:
            raise AssertionError("conditioning foi truncado ou corrompido")
        return ("guider-ok",)


class _BasicGuiderNodeOutputAwareNode:
    FUNCTION = "build"

    def build(self, model, conditioning):
        if not isinstance(conditioning, list):
            raise AssertionError("conditioning deveria ter sido extraido do NodeOutput")
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


def _factory(name):
    return {
        "RandomNoise": _RandomNoiseNode,
        "BasicGuider": _BasicGuiderNode,
        "KSamplerSelect": _KSamplerSelectNode,
        "Flux2Scheduler": _Flux2SchedulerNode,
        "EmptyFlux2LatentImage": _EmptyLatentNode,
        "SamplerCustomAdvanced": _SamplerAdvancedNode,
        "VAEDecode": _VAEDecodeNode,
    }[name]()


def _factory_list_aware(name):
    return {
        "RandomNoise": _RandomNoiseNode,
        "BasicGuider": _BasicGuiderListAwareNode,
        "KSamplerSelect": _KSamplerSelectNode,
        "Flux2Scheduler": _Flux2SchedulerNode,
        "EmptyFlux2LatentImage": _EmptyLatentNode,
        "SamplerCustomAdvanced": _SamplerAdvancedNode,
        "VAEDecode": _VAEDecodeNode,
    }[name]()


def _factory_node_output_aware(name):
    return {
        "RandomNoise": _RandomNoiseNode,
        "BasicGuider": _BasicGuiderNodeOutputAwareNode,
        "KSamplerSelect": _KSamplerSelectNode,
        "Flux2Scheduler": _Flux2SchedulerNode,
        "EmptyFlux2LatentImage": _EmptyLatentNode,
        "SamplerCustomAdvanced": _SamplerAdvancedNode,
        "VAEDecode": _VAEDecodeNode,
    }[name]()


class ComposedProcessingTests(unittest.TestCase):
    def test_normalizes_params(self):
        params = normalize_processing_params(
            noise_seed="5",
            sampler_name="",
            steps=0,
            width=-1,
            height=99999,
            batch_size="0",
        )
        self.assertEqual(params["noise_seed"], 5)
        self.assertEqual(params["sampler_name"], "euler")
        self.assertEqual(params["steps"], 1)
        self.assertEqual(params["width"], 8)
        self.assertEqual(params["height"], 16384)
        self.assertEqual(params["batch_size"], 1)

    def test_runs_pipeline_with_expected_call_flow(self):
        image = run_processing_pipeline(
            model="m0",
            conditioning="c0",
            vae="v0",
            noise_seed=42,
            sampler_name="euler",
            steps=20,
            width=1024,
            height=768,
            batch_size=1,
            node_factory=_factory,
        )

        self.assertEqual(
            image,
            "image(sampled(noise(42)|guider(m0|c0)|sampler(euler)|sigmas(20|1024|768)|latent(1024|768|1))|v0)",
        )

    def test_preserves_conditioning_list_structure_for_basic_guider(self):
        conditioning = [["embed", {"a": 1}], ["embed2", {"b": 2}]]
        image = run_processing_pipeline(
            model="m0",
            conditioning=conditioning,
            vae="v0",
            noise_seed=42,
            sampler_name="euler",
            steps=20,
            width=1024,
            height=768,
            batch_size=1,
            node_factory=_factory_list_aware,
        )
        self.assertEqual(
            image,
            "image(sampled(noise(42)|guider-ok|sampler(euler)|sigmas(20|1024|768)|latent(1024|768|1))|v0)",
        )

    def test_extracts_native_node_output_before_basic_guider(self):
        conditioning = [["embed", {"a": 1}]]
        image = run_processing_pipeline(
            model="m0",
            conditioning=conditioning,
            vae="v0",
            noise_seed=42,
            sampler_name="euler",
            steps=20,
            width=1024,
            height=768,
            batch_size=1,
            node_factory=_factory_node_output_aware,
        )
        self.assertEqual(
            image,
            "image(sampled(noise(42)|guider-node-output-ok|sampler(euler)|sigmas(20|1024|768)|latent(1024|768|1))|v0)",
        )


if __name__ == "__main__":
    unittest.main()
