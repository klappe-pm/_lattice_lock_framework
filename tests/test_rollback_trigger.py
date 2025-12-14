import pytest
from unittest.mock import MagicMock, patch
from lattice_lock.rollback.trigger import RollbackTrigger
from lattice_lock.rollback.checkpoint import CheckpointManager
from lattice_lock.rollback.state import RollbackState
from click.testing import CliRunner
from lattice_lock_cli.commands.rollback import rollback

class TestRollbackTrigger:
    @pytest.fixture
    def mock_checkpoint_manager(self):
        return MagicMock(spec=CheckpointManager)

    @pytest.fixture
    def trigger(self, mock_checkpoint_manager):
        return RollbackTrigger(mock_checkpoint_manager)

    @pytest.fixture
    def mock_state(self):
        return RollbackState(
            timestamp=1234567890.0,
            files={"file1": "hash1"},
            config={"key": "value"},
            schema_version="1.0"
        )

    def test_trigger_rollback_success(self, trigger, mock_checkpoint_manager, mock_state):
        mock_checkpoint_manager.get_checkpoint.return_value = mock_state

        success = trigger.trigger_rollback("Test reason", "ckpt_123")

        assert success is True
        mock_checkpoint_manager.get_checkpoint.assert_called_once_with("ckpt_123")

    def test_trigger_rollback_latest_success(self, trigger, mock_checkpoint_manager, mock_state):
        mock_checkpoint_manager.list_checkpoints.return_value = ["ckpt_123", "ckpt_124"]
        mock_checkpoint_manager.get_checkpoint.return_value = mock_state

        success = trigger.trigger_rollback("Test reason")

        assert success is True
        mock_checkpoint_manager.list_checkpoints.assert_called_once()
        mock_checkpoint_manager.get_checkpoint.assert_called_once_with("ckpt_124")

    def test_trigger_rollback_failure_no_checkpoint(self, trigger, mock_checkpoint_manager):
        mock_checkpoint_manager.get_checkpoint.return_value = None

        success = trigger.trigger_rollback("Test reason", "ckpt_123")

        assert success is False

    def test_hooks_execution(self, trigger, mock_checkpoint_manager, mock_state):
        mock_checkpoint_manager.list_checkpoints.return_value = ["ckpt_123"]
        mock_checkpoint_manager.get_checkpoint.return_value = mock_state

        pre_hook = MagicMock()
        post_hook = MagicMock()
        notification_hook = MagicMock()

        trigger.register_pre_rollback_hook(pre_hook)
        trigger.register_post_rollback_hook(post_hook)
        trigger.register_notification_hook(notification_hook)

        trigger.trigger_rollback("Test reason")

        pre_hook.assert_called_once()
        post_hook.assert_called_once_with(True)
        assert notification_hook.call_count >= 2 # Triggered and Success messages

    def test_check_validation_failure(self, trigger):
        with patch.object(trigger, 'trigger_rollback') as mock_trigger:
            trigger.check_validation_failure(False, "Context")
            mock_trigger.assert_called_once()

            mock_trigger.reset_mock()
            trigger.check_validation_failure(True, "Context")
            mock_trigger.assert_not_called()

    def test_check_sheriff_violation(self, trigger):
        with patch.object(trigger, 'trigger_rollback') as mock_trigger:
            trigger.check_sheriff_violation(["violation1"])
            mock_trigger.assert_called_once()

            mock_trigger.reset_mock()
            trigger.check_sheriff_violation([])
            mock_trigger.assert_not_called()

    def test_check_gauntlet_failure(self, trigger):
        with patch.object(trigger, 'trigger_rollback') as mock_trigger:
            trigger.check_gauntlet_failure("details")
            mock_trigger.assert_called_once()

            mock_trigger.reset_mock()
            trigger.check_gauntlet_failure("")
            mock_trigger.assert_not_called()

class TestRollbackCLI:
    def test_rollback_command_latest(self):
        runner = CliRunner()
        with patch('lattice_lock_cli.commands.rollback.RollbackTrigger') as MockTrigger, \
             patch('lattice_lock_cli.commands.rollback.CheckpointManager') as MockManager:

            mock_trigger_instance = MockTrigger.return_value
            mock_trigger_instance.trigger_rollback.return_value = True

            result = runner.invoke(rollback, ['--latest'])

            assert result.exit_code == 0
            assert "Rollback completed successfully." in result.output
            mock_trigger_instance.trigger_rollback.assert_called_with("Manual rollback (latest)")

    def test_rollback_command_checkpoint(self):
        runner = CliRunner()
        with patch('lattice_lock_cli.commands.rollback.RollbackTrigger') as MockTrigger, \
             patch('lattice_lock_cli.commands.rollback.CheckpointManager') as MockManager:

            mock_trigger_instance = MockTrigger.return_value
            mock_trigger_instance.trigger_rollback.return_value = True

            result = runner.invoke(rollback, ['--checkpoint', 'ckpt_123'])

            assert result.exit_code == 0
            assert "Rollback completed successfully." in result.output
            mock_trigger_instance.trigger_rollback.assert_called_with("Manual rollback (ckpt_123)", checkpoint_id='ckpt_123')

    def test_rollback_command_missing_args(self):
        runner = CliRunner()
        result = runner.invoke(rollback, [])
        assert result.exit_code == 0
        assert "Error: You must specify either --checkpoint or --latest." in result.output

    def test_rollback_command_conflict_args(self):
        runner = CliRunner()
        result = runner.invoke(rollback, ['--checkpoint', 'ckpt_123', '--latest'])
        assert result.exit_code == 0
        assert "Error: You cannot specify both --checkpoint and --latest." in result.output
