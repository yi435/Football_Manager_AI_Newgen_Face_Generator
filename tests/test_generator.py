import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.generator import FaceGenerator, DEFAULT_NEGATIVE_PROMPT, PROVIDER_NAMES


class GeneratorTest(unittest.TestCase):
    def test_generator_initialization_defaults(self):
        gen = FaceGenerator(
            graphics_dir="./graphics/test",
            concurrency_limit=1
        )
        self.assertEqual(gen.sampler, "euler_ancestral")
        self.assertEqual(gen.scheduler, "karras")
        self.assertEqual(gen.steps, 25)
        self.assertEqual(gen.cfg, 6.0)
        self.assertEqual(gen.width, 896)
        self.assertEqual(gen.height, 1152)
        self.assertEqual(gen.provider, "comfyui")
        self.assertEqual(gen.provider_name, "Local ComfyUI (SDXL)")

    def test_build_sdxl_workflow_structure(self):
        prompt_text = "portrait of a 18-year-old French footballer"
        negative_text = DEFAULT_NEGATIVE_PROMPT
        checkpoint = "RealVisXL_V5.0_fp16.safetensors"
        uid = "2000000001"

        gen = FaceGenerator(
            graphics_dir="./graphics/test",
            concurrency_limit=1,
            steps=25,
            cfg=6.0,
            sampler="euler_a",
            scheduler="karras",
            width=896,
            height=1152
        )

        workflow = gen.build_sdxl_workflow(
            uid=uid,
            prompt=prompt_text,
            checkpoint=checkpoint
        )

        # Check required ComfyUI node keys
        self.assertIn("4", workflow)  # CheckpointLoaderSimple
        self.assertEqual(workflow["4"]["inputs"]["ckpt_name"], checkpoint)

        self.assertIn("6", workflow)  # CLIPTextEncode (Positive)
        self.assertEqual(workflow["6"]["inputs"]["text"], prompt_text)

        self.assertIn("7", workflow)  # CLIPTextEncode (Negative)
        self.assertEqual(workflow["7"]["inputs"]["text"], negative_text)

        self.assertIn("3", workflow)  # KSampler
        ksampler_inputs = workflow["3"]["inputs"]
        self.assertEqual(ksampler_inputs["steps"], 25)
        self.assertEqual(ksampler_inputs["cfg"], 6.0)
        # euler_a must be normalized to euler_ancestral for ComfyUI KSampler!
        self.assertEqual(ksampler_inputs["sampler_name"], "euler_ancestral")
        self.assertEqual(ksampler_inputs["scheduler"], "karras")
        # Deterministic seed derivation from UID
        self.assertEqual(ksampler_inputs["seed"], int(uid) % 2147483647)

        self.assertIn("5", workflow)  # EmptyLatentImage
        self.assertEqual(workflow["5"]["inputs"]["width"], 896)
        self.assertEqual(workflow["5"]["inputs"]["height"], 1152)


if __name__ == "__main__":
    unittest.main()
