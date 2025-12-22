import sys
from unittest.mock import patch

from lattice_lock_validator.structure import main


def test_main_success(tmp_path):
    # Create valid structure
    (tmp_path / "docs" / "agent_definitions").mkdir(parents=True)
    (tmp_path / "src").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / ".gitignore").touch()
    (tmp_path / "README.md").touch()

    with (
        patch.object(sys, "argv", ["structure.py", str(tmp_path)]),
        patch.object(sys, "exit") as mock_exit,
    ):
        main()
        mock_exit.assert_called_with(0)


def test_main_failure(tmp_path):
    # Missing directories
    with (
        patch.object(sys, "argv", ["structure.py", str(tmp_path)]),
        patch.object(sys, "exit") as mock_exit,
    ):
        main()
        mock_exit.assert_called_with(1)


def test_main_naming_only(tmp_path):
    # Create bad file
    (tmp_path / "BadName.py").touch()

    with (
        patch.object(sys, "argv", ["structure.py", "--naming-only", str(tmp_path)]),
        patch.object(sys, "exit") as mock_exit,
    ):
        main()
        mock_exit.assert_called_with(1)
