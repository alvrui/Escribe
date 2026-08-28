import hashlib
import hmac
import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
import webhook_receiver


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.old = webhook_receiver.SECRET
        webhook_receiver.SECRET = "test-secret"

    def tearDown(self):
        webhook_receiver.SECRET = self.old

    def test_signature(self):
        body = b'{"ok":true}'
        sig = "sha256=" + hmac.new(b"test-secret", body, hashlib.sha256).hexdigest()
        self.assertTrue(webhook_receiver.valid_signature(body, sig))
        self.assertFalse(webhook_receiver.valid_signature(body, "sha256=bad"))

    def test_only_task_file_triggers(self):
        base = {"commits": [{"added": [], "modified": ["README.md"]}]}
        self.assertFalse(webhook_receiver.task_changed(base))
        task = {"commits": [{"added": [], "modified": ["coordination/CURRENT_TASK.md"]}]}
        self.assertTrue(webhook_receiver.task_changed(task))


if __name__ == "__main__":
    unittest.main()
