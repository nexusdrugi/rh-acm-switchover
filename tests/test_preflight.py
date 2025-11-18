"""Unit tests for modules/preflight.py."""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.preflight import PreflightValidator
from lib.utils import StateManager
import tempfile


class TestPreflightValidator(unittest.TestCase):
    """Test cases for PreflightValidator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_primary = MagicMock()
        self.mock_secondary = MagicMock()
        
        self.validator = PreflightValidator(
            self.mock_primary,
            self.mock_secondary,
            method="passive"
        )

    def tearDown(self):
        """Clean up test fixtures."""
        pass  # No cleanup needed with mocks only

    def test_add_result_passed(self):
        """Test recording a passed validation result."""
        self.validator.add_result("test_check", True, "all good", critical=True)
        
        self.assertEqual(len(self.validator.validation_results), 1)
        result = self.validator.validation_results[0]
        self.assertEqual(result["check"], "test_check")
        self.assertTrue(result["passed"])
        self.assertEqual(result["message"], "all good")
        self.assertTrue(result["critical"])

    def test_add_result_failed(self):
        """Test recording a failed validation result."""
        self.validator.add_result("test_check", False, "failed", critical=True)
        
        self.assertEqual(len(self.validator.validation_results), 1)
        result = self.validator.validation_results[0]
        self.assertEqual(result["check"], "test_check")
        self.assertFalse(result["passed"])
        self.assertEqual(result["message"], "failed")
        self.assertTrue(result["critical"])

    def test_add_result_warning(self):
        """Test recording a non-critical warning result."""
        self.validator.add_result("test_check", False, "warning", critical=False)
        
        result = self.validator.validation_results[0]
        self.assertFalse(result["passed"])
        self.assertFalse(result["critical"])


if __name__ == '__main__':
    unittest.main()


if __name__ == '__main__':
    unittest.main()
