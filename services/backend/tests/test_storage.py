import unittest

from app.hardware import build_generation_plan, build_hardware_summary, choose_resource_profile


class HardwareTests(unittest.TestCase):
    def test_profile_for_small_memory(self):
        self.assertEqual(choose_resource_profile(6.0), 'Low Resource Mode')

    def test_profile_for_moderate_memory(self):
        self.assertEqual(choose_resource_profile(12.0), 'Balanced Mode')

    def test_build_hardware_summary_has_expected_fields(self):
        summary = build_hardware_summary()
        self.assertTrue(summary.platform)
        self.assertTrue(summary.cpu_model)
        self.assertGreater(summary.cpu_cores, 0)
        self.assertIn(summary.resource_profile, {'Low Resource Mode', 'Balanced Mode', 'Quality Mode'})

    def test_generation_plan_rejects_missing_model(self):
        with self.assertRaises(ValueError):
            build_generation_plan('', 12.0, 4.0)

    def test_generation_plan_for_reasonable_machine(self):
        plan = build_generation_plan('Stable Diffusion 1.5', 32.0, 8.0)
        self.assertEqual(plan['recommended_mode'], 'Balanced Mode')
        self.assertTrue(plan['allow_gpu'])


if __name__ == '__main__':
    unittest.main()
