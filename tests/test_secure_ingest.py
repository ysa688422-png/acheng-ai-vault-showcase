import unittest

from examples.secure_ingest import validate_payload


class SecureIngestTests(unittest.TestCase):
    def test_accepts_sanitized_content(self):
        document = validate_payload({
            "title": "Demo",
            "content": "A public architecture description.",
            "source_type": "test",
        })
        self.assertEqual(document.title, "Demo")
        self.assertEqual(len(document.fingerprint), 64)

    def test_rejects_sensitive_field(self):
        with self.assertRaisesRegex(ValueError, "Sensitive fields"):
            validate_payload({
                "title": "Unsafe",
                "content": "Example",
                "api_key": "not-a-real-key",
            })

    def test_rejects_secret_like_content(self):
        with self.assertRaisesRegex(ValueError, "appears to contain a secret"):
            validate_payload({
                "title": "Unsafe",
                "content": "secret = do-not-publish",
            })


if __name__ == "__main__":
    unittest.main()
