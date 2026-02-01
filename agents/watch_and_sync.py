#!/usr/bin/env python3
"""
Watch agent definition files for changes and automatically sync to multiple targets.

This script monitors the agent_definitions folder and automatically converts
any changed files to the configured sync targets (Claude Code, Lattice Lock, etc.).

Features:
- Automatic syncing on file changes
- Debouncing to batch rapid changes
- Support for multiple sync targets
- Initial sync on startup
"""

import time
from pathlib import Path

from sync_agents_to_claude import AgentSyncer, create_sync_targets
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class AgentFileHandler(FileSystemEventHandler):
    """
    Handler for file system events in agent definitions folder.

    Monitors YAML files for changes and triggers syncing to all configured targets.
    Uses debouncing to avoid excessive syncs when multiple files change rapidly.
    """

    def __init__(self, source_dir: Path, syncer: AgentSyncer):
        """
        Initialize the file handler.

        Args:
            source_dir: Directory to monitor for changes
            syncer: AgentSyncer instance configured with targets
        """
        self.source_dir = source_dir
        self.syncer = syncer
        self.last_sync = 0
        self.debounce_seconds = 2  # Wait 2 seconds before syncing to batch changes

    def on_modified(self, event):
        """Called when a file is modified."""
        if event.is_directory:
            return

        if event.src_path.endswith(".yaml"):
            self._trigger_sync(f"Modified: {Path(event.src_path).name}")

    def on_created(self, event):
        """Called when a file is created."""
        if event.is_directory:
            return

        if event.src_path.endswith(".yaml"):
            self._trigger_sync(f"Created: {Path(event.src_path).name}")

    def on_deleted(self, event):
        """Called when a file is deleted."""
        if event.is_directory:
            return

        if event.src_path.endswith(".yaml"):
            print(f"\n⚠️  Deleted: {Path(event.src_path).name}")
            print("   Note: You may want to manually remove the corresponding .md file")

    def _trigger_sync(self, reason: str):
        """
        Trigger a sync with debouncing.

        Args:
            reason: Human-readable reason for the sync (e.g., file that changed)
        """
        current_time = time.time()

        # Debounce: only sync if enough time has passed since last sync
        if current_time - self.last_sync < self.debounce_seconds:
            return

        self.last_sync = current_time

        print(f"\n{'=' * 60}")
        print(f"🔄 Change detected: {reason}")
        print(f"{'=' * 60}")

        try:
            # Use the syncer to sync to all targets
            results = self.syncer.sync_all_targets()

            # Display summary
            total = sum(results.values())
            print(f"\n✓ Synced {total} agents across {len(results)} targets")

        except Exception as e:
            print(f"\n✗ Error during sync: {e}")

        print(f"{'=' * 60}")
        print("Watching for changes...")
        print(f"{'=' * 60}\n")


def main():
    """
    Main entry point for the watch script.

    Sets up file watching and performs initial sync to all configured targets.
    """
    # Define paths
    script_dir = Path(__file__).parent
    agents_root = script_dir
    source_dir = agents_root / "agent_definitions"
    project_root = script_dir.parent

    print("=" * 60)
    print("Agent File Watcher - Multi-Target Auto-Sync")
    print("=" * 60)

    # Validate source directory
    if not source_dir.exists():
        print(f"\n✗ Error: Source directory not found: {source_dir}")
        print("   Make sure you're running this from the agents/ directory")
        return 1

    # Ask user which targets to sync
    print(f"\nSource: {source_dir}")
    print("\nSync Targets:")
    print("1. Claude Code (project-level) + Lattice Lock archive [RECOMMENDED]")
    print("2. Claude Code (user-level) + Lattice Lock archive")
    print("3. All targets (project + user + archive)")
    print("4. Lattice Lock archive only")

    choice = input("\nEnter choice (1-4) [default: 1]: ").strip() or "1"

    # Create sync targets based on choice
    targets = create_sync_targets(agents_root, project_root, choice)

    if not targets:
        print("\n✗ Error: Invalid choice or no targets selected")
        return 1

    # Display what will be synced
    print(f"\n{'=' * 60}")
    print("Will watch and sync to:")
    for target in targets:
        print(f"  • {target.name}: {target.get_target_dir()}")
        print(f"    ({target.description})")
    print(f"{'=' * 60}\n")

    # Create syncer instance
    syncer = AgentSyncer(source_dir, targets)

    # Perform initial sync
    print(f"{'=' * 60}")
    print("Performing initial sync...")
    print(f"{'=' * 60}")

    results = syncer.sync_all_targets()

    total = sum(results.values())
    print(f"\n✓ Initial sync complete: {total} agents synced\n")

    # Set up file watcher
    event_handler = AgentFileHandler(source_dir, syncer)
    observer = Observer()
    observer.schedule(event_handler, str(source_dir), recursive=True)
    observer.start()

    print(f"{'=' * 60}")
    print("👀 Watching for changes...")
    print(f"{'=' * 60}")
    print(f"Monitoring: {source_dir}")
    print(f"Targets: {len(targets)} configured")
    print("\nPress Ctrl+C to stop\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("Stopping file watcher...")
        print("=" * 60)
        observer.stop()

    observer.join()
    print("\n✓ File watcher stopped")
    return 0


if __name__ == "__main__":
    exit(main())
