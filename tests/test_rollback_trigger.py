import subprocess
import unittest
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from lattice_lock.rollback.checkpoint import CheckpointManager
from lattice_lock.rollback.state import RollbackState
from lattice_lock.rollback.trigger import RollbackTrigger
from lattice_lock_cli.commands.rollback import rollback


class TestRollbackTrigger(unittest.TestCase):
    def setUp(self):
        self.mock_checkpoint_manager = MagicMock(spec=CheckpointManager)
        self.trigger = RollbackTrigger(self.mock_checkpoint_manager)

        self.mock_state = RollbackState(
            timestamp=1234567890.0,
            files={"file1": "hash1"},
            config={"key": "value"},
            schema_version="1.0",
        )

    def test_trigger_rollback_success(self):
        self.mock_checkpoint_manager.get_checkpoint.return_value = self.mock_state

        success = self.trigger.trigger_rollback("Test reason", "ckpt_123")

        self.assertTrue(success)
        self.mock_checkpoint_manager.get_checkpoint.assert_called_once_with("ckpt_123")

    def test_trigger_rollback_latest_success(self):
        self.mock_checkpoint_manager.list_checkpoints.return_value = ["ckpt_123", "ckpt_124"]
        self.mock_checkpoint_manager.get_checkpoint.return_value = self.mock_state

        success = self.trigger.trigger_rollback("Test reason")

        self.assertTrue(success)
        self.mock_checkpoint_manager.list_checkpoints.assert_called_once()
        self.mock_checkpoint_manager.get_checkpoint.assert_called_once_with("ckpt_124")

    def test_trigger_rollback_failure_no_checkpoint(self):
        self.mock_checkpoint_manager.get_checkpoint.return_value = None

        success = self.trigger.trigger_rollback("Test reason", checkpoint_id="ckpt_123")

        self.assertFalse(success)

    @patch("subprocess.run")
    def test_trigger_rollback_git_success(self, mock_subprocess):
        mock_subprocess.return_value.returncode = 0

        success = self.trigger.trigger_rollback("Test reason", mode="git_revert")

        self.assertTrue(success)
        mock_subprocess.assert_called_with(
            ["git", "revert", "--no-edit", "HEAD"], check=True, capture_output=True
        )

    @patch("subprocess.run")
    def test_trigger_rollback_git_failure(self, mock_subprocess):
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, ["git", "revert"])

        success = self.trigger.trigger_rollback("Test reason", mode="git_revert")

        self.assertFalse(success)

    def test_hooks_execution(self):
        self.mock_checkpoint_manager.list_checkpoints.return_value = ["ckpt_123"]
        self.mock_checkpoint_manager.get_checkpoint.return_value = self.mock_state

        pre_hook = MagicMock()
        post_hook = MagicMock()
        notification_hook = MagicMock()

        self.trigger.register_pre_rollback_hook(pre_hook)
        self.trigger.register_post_rollback_hook(post_hook)
        self.trigger.register_notification_hook(notification_hook)

        self.trigger.trigger_rollback("Test reason")

        pre_hook.assert_called_once()
        post_hook.assert_called_once_with(True)
        self.assertGreaterEqual(notification_hook.call_count, 2)  # Triggered and Success messages

    def test_check_validation_failure(self):
        with patch.object(self.trigger, "trigger_rollback") as mock_trigger:
            self.trigger.check_validation_failure(False, "Context")
            mock_trigger.assert_called_once_with("Validation failed: Context", mode="git_revert")

            mock_trigger.reset_mock()
            self.trigger.check_validation_failure(True, "Context")
            mock_trigger.assert_not_called()

    def test_check_sheriff_violation(self):
        with patch.object(self.trigger, "trigger_rollback") as mock_trigger:
            self.trigger.check_sheriff_violation(["violation1"])
            mock_trigger.assert_called_once_with(
                "Sheriff violations found: violation1", mode="git_revert"
            )

            mock_trigger.reset_mock()
            self.trigger.check_sheriff_violation([])
            mock_trigger.assert_not_called()

    def test_check_gauntlet_failure(self):
        with patch.object(self.trigger, "trigger_rollback") as mock_trigger:
            self.trigger.check_gauntlet_failure("details")
            mock_trigger.assert_called_once_with("Gauntlet failure: details", mode="git_revert")

            mock_trigger.reset_mock()
            self.trigger.check_gauntlet_failure("")
            mock_trigger.assert_not_called()


class TestRollbackCLI(unittest.TestCase):
    def test_rollback_command_latest(self):
        runner = CliRunner()
        with patch("lattice_lock_cli.commands.rollback.RollbackTrigger") as MockTrigger, patch(
            "lattice_lock_cli.commands.rollback.CheckpointManager"
        ) as MockManager:
            mock_trigger_instance = MockTrigger.return_value
            mock_trigger_instance.trigger_rollback.return_value = True

            result = runner.invoke(rollback, ["--latest"])

            self.assertEqual(result.exit_code, 0)
            self.assertIn("Rollback completed successfully.", result.output)
            mock_trigger_instance.trigger_rollback.assert_called_with("Manual rollback (latest)")

    def test_rollback_command_checkpoint(self):
        runner = CliRunner()
        with patch("lattice_lock_cli.commands.rollback.RollbackTrigger") as MockTrigger, patch(
            "lattice_lock_cli.commands.rollback.CheckpointManager"
        ) as MockManager:
            mock_trigger_instance = MockTrigger.return_value
            mock_trigger_instance.trigger_rollback.return_value = True

            result = runner.invoke(rollback, ["--checkpoint", "ckpt_123"])

            self.assertEqual(result.exit_code, 0)
            self.assertIn("Rollback completed successfully.", result.output)
            mock_trigger_instance.trigger_rollback.assert_called_with(
                "Manual rollback (ckpt_123)", checkpoint_id="ckpt_123"
            )

    def test_rollback_command_missing_args(self):
        runner = CliRunner()
        result = runner.invoke(rollback, [])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Error: You must specify either --checkpoint or --latest.", result.output)

    def test_rollback_command_conflict_args(self):
        runner = CliRunner()
        result = runner.invoke(rollback, ["--checkpoint", "ckpt_123", "--latest"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Error: You cannot specify both --checkpoint and --latest.", result.output)


if __name__ == "__main__":
    unittest.main()
