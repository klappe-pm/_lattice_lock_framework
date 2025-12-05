import click
import logging
from lattice_lock.rollback import RollbackTrigger, CheckpointManager

logger = logging.getLogger(__name__)

@click.command()
@click.option('--checkpoint', help='Checkpoint ID to restore')
@click.option('--latest', is_flag=True, help='Restore latest checkpoint')
def rollback(checkpoint, latest):
    """
    Manually trigger a rollback to a previous state.
    """
    if not checkpoint and not latest:
        click.echo("Error: You must specify either --checkpoint or --latest.")
        return

    if checkpoint and latest:
        click.echo("Error: You cannot specify both --checkpoint and --latest.")
        return

    click.echo("Initiating rollback...")
    
    # Initialize components
    # In a real app, these might be injected or initialized from a context
    checkpoint_manager = CheckpointManager()
    trigger = RollbackTrigger(checkpoint_manager)
    
    success = False
    if latest:
        success = trigger.trigger_rollback("Manual rollback (latest)")
    else:
        success = trigger.trigger_rollback(f"Manual rollback ({checkpoint})", checkpoint_id=checkpoint)
        
    if success:
        click.echo("Rollback completed successfully.")
    else:
        click.echo("Rollback failed. Check logs for details.")
        exit(1)
