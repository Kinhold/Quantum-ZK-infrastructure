import os
import unittest
from unittest.mock import patch

from claude_zk_integration import DryRunProvider, ZKReviewAssistant, build_provider


class DryRunProviderTests(unittest.TestCase):
    def test_review_is_offline_and_deterministic(self):
        source = "fn main(x: Field) { assert(x != 0); }"
        assistant = ZKReviewAssistant(DryRunProvider())

        result = assistant.analyze_source(source)

        self.assertIn("[dry-run] No request was sent.", result)
        self.assertIn("review prompt", result)

    def test_empty_source_is_rejected(self):
        assistant = ZKReviewAssistant(DryRunProvider())

        with self.assertRaisesRegex(ValueError, "source must not be empty"):
            assistant.analyze_source("  ")

    @patch.dict(os.environ, {}, clear=True)
    def test_default_provider_needs_no_credentials(self):
        self.assertIsInstance(build_provider(live=False), DryRunProvider)


if __name__ == "__main__":
    unittest.main()
