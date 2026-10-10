import unittest

from app.coordinator import GenerationCoordinator
from app.comfyui_integration import ComfyUIIntegration
from app.generator import LocalImageGenerator


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.generator = LocalImageGenerator()

    def test_validate_request_rejects_empty_prompt(self):
        valid, error = self.generator.validate_request('')
        self.assertFalse(valid)
        self.assertIn('empty', error.lower())

    def test_validate_request_accepts_valid_params(self):
        valid, error = self.generator.validate_request('A test prompt')
        self.assertTrue(valid)
        self.assertIsNone(error)

    def test_build_generation_request_adjusts_for_low_resource_mode(self):
        result = self.generator.build_generation_request(
            task_id='test-1',
            model_name='Stable Diffusion 1.5',
            prompt='A test prompt',
            width=1024,
            height=1024,
            steps=50,
            resource_profile='Low Resource Mode',
        )
        self.assertTrue(result['valid'])
        self.assertEqual(result['width'], 512)
        self.assertEqual(result['height'], 512)
        self.assertLessEqual(result['steps'], 15)

    def test_get_generation_defaults_for_profiles(self):
        low = self.generator.get_generation_defaults('Low Resource Mode')
        self.assertEqual(low['width'], 512)
        self.assertLessEqual(low['steps'], 20)

        quality = self.generator.get_generation_defaults('Quality Mode')
        self.assertGreaterEqual(quality['width'], 1024)
        self.assertGreaterEqual(quality['steps'], 40)


class ComfyUITests(unittest.TestCase):
    def setUp(self):
        self.comfyui = ComfyUIIntegration()

    def test_comfyui_status(self):
        status = self.comfyui.get_status()
        self.assertIn('available', status)
        self.assertIn('message', status)

    def test_build_sd15_workflow(self):
        workflow = self.comfyui.build_sd15_workflow(
            prompt='A test image',
            width=512,
            height=512,
            steps=20,
        )
        self.assertIn('1', workflow)
        self.assertIn('2', workflow)
        self.assertIn('7', workflow)

    def test_get_model_requirements(self):
        reqs = self.comfyui.get_model_requirements('sd-v1-5.ckpt')
        self.assertIn('vram_min_gb', reqs)
        self.assertIn('ram_recommended_gb', reqs)
        self.assertGreater(reqs['vram_recommended_gb'], 0)


class CoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.coordinator = GenerationCoordinator()

    def test_can_generate_image_returns_checks(self):
        result = self.coordinator.can_generate_image()
        self.assertIn('hardware_ok', result)
        self.assertIn('can_proceed', result)
        self.assertIn('warnings', result)
        self.assertIn('errors', result)

    def test_get_optimized_settings_for_profiles(self):
        low = self.coordinator.get_optimized_settings('Low Resource Mode')
        self.assertEqual(low['width'], 512)

        balanced = self.coordinator.get_optimized_settings('Balanced Mode')
        self.assertGreater(balanced['width'], low['width'])


if __name__ == '__main__':
    unittest.main()
