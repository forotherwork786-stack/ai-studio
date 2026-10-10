import unittest

from app.model_manager import model_manager


class ModelManagerTests(unittest.TestCase):
    def test_known_models_are_available(self):
        models = model_manager.list_known_models()
        ids = {item['id'] for item in models}
        self.assertIn('sd15', ids)
        self.assertIn('sdxl', ids)
        self.assertIn('wan21', ids)

    def test_compatibility_for_sd15_on_ordinary_machine(self):
        result = model_manager.check_compatibility('sd15', 16.0, 8.0)
        self.assertTrue(result['compatible'])

    def test_compatibility_for_sdxl_on_low_memory(self):
        result = model_manager.check_compatibility('sdxl', 8.0, 4.0)
        self.assertFalse(result['compatible'])

    def test_import_model_registers_local_path(self):
        result = model_manager.import_model('/models/custom/model.ckpt', 'custom-model')
        self.assertTrue(result['installed'])
        self.assertEqual(result['path'], '/models/custom/model.ckpt')


if __name__ == '__main__':
    unittest.main()
