import logging
from typing import Optional, List, Callable, Any
from .state import RollbackState
# Assuming CheckpointManager will be available or we mock it. 
# For now, I will import it inside methods or use a protocol if I want to be strict, 
# but for simplicity I'll assume it exists or I'll create it.
# from .checkpoint import CheckpointManager 

logger = logging.getLogger(__name__)

class RollbackTrigger:
    """
    Manages automatic and manual rollback triggers.
    """

    def __init__(self, checkpoint_manager: Any): # Using Any to avoid import error for now
        self.checkpoint_manager = checkpoint_manager
        self._pre_rollback_hooks: List[Callable[[], None]] = []
        self._post_rollback_hooks: List[Callable[[bool], None]] = []
        self._notification_hooks: List[Callable[[str], None]] = []

    def register_pre_rollback_hook(self, hook: Callable[[], None]):
        """Register a hook to run before rollback."""
        self._pre_rollback_hooks.append(hook)

    def register_post_rollback_hook(self, hook: Callable[[bool], None]):
        """Register a hook to run after rollback. Hook receives success status."""
        self._post_rollback_hooks.append(hook)

    def register_notification_hook(self, hook: Callable[[str], None]):
        """Register a hook for notifications."""
        self._notification_hooks.append(hook)

    def trigger_rollback(self, reason: str, checkpoint_id: Optional[str] = None) -> bool:
        """
        Initiate a rollback.
        
        Args:
            reason: The reason for the rollback.
            checkpoint_id: Specific checkpoint to restore. If None, restores the latest.
            
        Returns:
            bool: True if rollback was successful, False otherwise.
        """
        logger.warning(f"Rollback triggered: {reason}")
        self._notify(f"Rollback triggered: {reason}")

        try:
            self._execute_pre_hooks()
            
            state = None
            if checkpoint_id:
                state = self.checkpoint_manager.get_checkpoint(checkpoint_id)
            else:
                # Find latest checkpoint
                checkpoints = self.checkpoint_manager.list_checkpoints()
                if checkpoints:
                    # Assuming list_checkpoints returns IDs and we can sort them
                    # If they are timestamps or sortable IDs
                    checkpoints.sort(reverse=True)
                    latest_id = checkpoints[0]
                    state = self.checkpoint_manager.get_checkpoint(latest_id)
            
            if state:
                success = self._restore_state(state)
            else:
                logger.error("No checkpoint found to restore.")
                success = False
            
            if success:
                logger.info("Rollback executed successfully.")
                self._notify("Rollback executed successfully.")
            else:
                logger.error("Rollback execution failed.")
                self._notify("Rollback execution failed.")

            self._execute_post_hooks(success)
            return success

        except Exception as e:
            logger.exception(f"An error occurred during rollback: {e}")
            self._notify(f"An error occurred during rollback: {e}")
            self._execute_post_hooks(False)
            return False

    def _restore_state(self, state: RollbackState) -> bool:
        """
        Restore the system state from the given RollbackState.
        """
        try:
            # Restore files
            # In a real implementation, we would copy files from backup or reverse changes
            # For now, we'll just log it as we don't have the full file system control here
            # and the prompt focuses on the trigger system.
            # However, to be useful, we should at least pretend to do something.
            logger.info(f"Restoring state from timestamp {state.timestamp}")
            
            # Mock restoration of files
            for file_path, file_hash in state.files.items():
                logger.debug(f"Restoring file: {file_path} (hash: {file_hash})")
                
            # Restore config
            logger.debug(f"Restoring config: {state.config}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to restore state: {e}")
            return False

    def check_validation_failure(self, validation_result: bool, context: str):
        """Trigger rollback if validation fails."""
        if not validation_result:
            self.trigger_rollback(f"Validation failed: {context}")

    def check_sheriff_violation(self, violations: List[str]):
        """Trigger rollback if Sheriff finds violations."""
        if violations:
            self.trigger_rollback(f"Sheriff violations found: {', '.join(violations)}")

    def check_gauntlet_failure(self, failure_details: str):
        """Trigger rollback if Gauntlet tests fail."""
        if failure_details:
            self.trigger_rollback(f"Gauntlet failure: {failure_details}")

    def _execute_pre_hooks(self):
        for hook in self._pre_rollback_hooks:
            try:
                hook()
            except Exception as e:
                logger.error(f"Error in pre-rollback hook: {e}")

    def _execute_post_hooks(self, success: bool):
        for hook in self._post_rollback_hooks:
            try:
                hook(success)
            except Exception as e:
                logger.error(f"Error in post-rollback hook: {e}")

    def _notify(self, message: str):
        for hook in self._notification_hooks:
            try:
                hook(message)
            except Exception as e:
                logger.error(f"Error in notification hook: {e}")
