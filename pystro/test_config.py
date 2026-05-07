import unittest

from pystro.config import Config

class TestConfig(unittest.TestCase):

    def test_config(self):
        config = Config.from_json('pystro/.config.json')
        self.assertEqual(config.aws_secret_arn, "arn:aws:secretsmanager:us-east-1:182582699441:secret:maestro-daily-scripts-test-3a3654")
        self.assertEqual(config.aws_region, "us-east-1")
        self.assertIsNotNone(config.api_token)

if __name__ == "__main__":
    unittest.main()