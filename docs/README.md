import unittest

from app.coordinator import GenerationCoordinator
from app.generator import LocalImageGenerator


class GenerationFlowTests(unittest.TestCase):
    def test_validation_rejects_empty_prompt(self):
        result = LocalImageGenerator().validate_request('')
        self.assertFalse(result[0])

    def test_generation_request_is_valid_for_small_config(self):
        request = LocalImageGenerator().build_generation_request(
            task_id='abc',
            model_name='Stable Diffusion 1.5',
            prompt='A test prompt',
            width=512,
            height=512,
            steps=15,
            resource_profile='Low Resource Mode',
        )
        self.assertTrue(request['valid'])
        self.assertEqual(request['width'], 512)

    def test_coordinator_returns_preflight_checks(self):
        checks = GenerationCoordinator().can_generate_image('sd-v1-5.ckpt', 512, 512)
        self.assertIn('can_proceed', checks)
        self.assertIn('warnings', checks)
        self.assertIn('errors', checks)


if __name__ == '__main__':
    unittest.main()
