import argparse
import os
import re
import sys
from pathlib import Path

from .schema import ValidationResult


def validate_repository_structure(repo_path: str) -> ValidationResult:
    """
    Validates the repository structure and file naming conventions.

    Args:
        repo_path: Path to the repository root.

    Returns:
        ValidationResult: The result of the validation.
    """
    result = ValidationResult()

    # Resolve the repo path
    repo_path = Path(repo_path).expanduser().resolve()

    if not repo_path.exists():
        result.add_error(f"Repository path not found: {repo_path}")
        result.valid = False
        return result

    if not repo_path.is_dir():
        result.add_error(f"Repository path is not a directory: {repo_path}")
        result.valid = False
        return result

    # 1. Directory Structure
    dir_result = validate_directory_structure(repo_path)
    result.errors.extend(dir_result.errors)
    result.warnings.extend(dir_result.warnings)
    if not dir_result.valid:
        result.valid = False

    # 2. File and Folder Naming
    for root, dirs, files in os.walk(repo_path):
        # Filter directories to skip hidden ones (except .github) and common build artifacts
        dirs[:] = [
            d for d in dirs 
            if not (d.startswith(".") and d not in [".github"]) 
            and not d.startswith("_") 
            and not d.endswith(".egg-info")
            and d not in ["__pycache__", "venv", ".venv", "build", "dist", ".pytest_cache", ".ruff_cache"]
        ]

        # Validate folder naming
        for d in dirs:
            folder_path = os.path.join(root, d)
            f_result = validate_folder_naming(folder_path, repo_path)
            result.errors.extend(f_result.errors)
            result.warnings.extend(f_result.warnings)
            if not f_result.valid:
                result.valid = False

        # Validate file naming
        for filename in files:
            if filename == ".DS_Store":
                continue
            file_path = os.path.join(root, filename)
            naming_result = validate_file_naming(file_path, repo_path)
            result.errors.extend(naming_result.errors)
            result.warnings.extend(naming_result.warnings)
            if not naming_result.valid:
                result.valid = False

    return result


def validate_directory_structure(repo_path: str) -> ValidationResult:
    """Validates the directory structure against requirements."""
    result = ValidationResult()
    path = Path(repo_path).expanduser().resolve()

    if not path.exists():
        result.add_error(f"Repository path not found: {repo_path}")
        return result

    # Required root directories
    required_dirs = ["docs", "src", "scripts"]
    for d in required_dirs:
        if not (path / d).is_dir():
            result.add_error(f"Missing required root directory: {d}/")

    # Required root files
    required_files = [".gitignore", "README.md"]
    for f in required_files:
        if not (path / f).is_file():
            result.add_error(f"Missing required root file: {f}")

    # Agent definitions nesting
    agent_def_path = path / "docs" / "agents" / "agent_definitions"
    if agent_def_path.is_dir():
        for item in agent_def_path.iterdir():
            if item.is_file() and item.name not in [".DS_Store", "README.md"]:
                if item.suffix in [".yaml", ".yml"]:
                    result.add_error(
                        f"Agent definition '{item.name}' must be in a category subdirectory, not directly in agent_definitions/"
                    )

    return result


def validate_folder_naming(folder_path: str, repo_root: str = "") -> ValidationResult:
    """Validates folder name conventions (snake_case)."""
    result = ValidationResult()
    path = Path(folder_path)
    foldername = path.name

    # Hidden folders are handled by the walker's filter, but as a secondary check:
    if foldername.startswith(".") and foldername not in [".github"]:
        return result

    # snake_case check
    if foldername == ".github":
        return result

    if not re.match(r"^[a-z0-9_]+$", foldername):
        result.add_error(f"Folder '{foldername}' does not follow snake_case naming convention")

    return result


def validate_file_naming(file_path: str, repo_root: str = "") -> ValidationResult:
    """Validates file naming conventions (snake_case)."""
    result = ValidationResult()
    path = Path(file_path)
    filename = path.name

    # Prohibited patterns
    if " " in filename:
        result.add_error(f"File name contains spaces: {filename}")

    # snake_case check
    if filename.startswith("."):
        # Hidden files/configs often don't follow snake_case
        pass
    else:
        # Exemptions for standard files
        exemptions = [
            "README.md", "LICENSE.md", "Dockerfile", "Makefile", 
            "ROADMAP.md", "requirements-dev.lock", "requirements.lock",
            "pyproject.toml"
        ]
        if filename in exemptions:
            pass
        elif ".github" in path.parts:
            # Allow hyphens in GitHub workflows/actions
            pass
        else:
            # Check for hyphens
            if "-" in filename:
                 result.add_error(f"File '{filename}' contains hyphens (use snake_case instead)")

            # Check all segments (stem parts) for snake_case: lowercase, numbers, underscores.
            segments = filename.split(".")
            parts_to_check = segments[:-1] if len(segments) > 1 else segments
            
            for part in parts_to_check:
                if not re.match(r"^[a-z0-9_]+$", part):
                    result.add_error(f"File '{filename}' does not follow snake_case naming convention")
                    break

    # Agent definitions pattern: {category}_{name}_definition.yaml
    try:
        parts = path.parts
        if "agent_definitions" in parts:
            idx = parts.index("agent_definitions")
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                if not filename.endswith("_definition.yaml") and not filename.endswith(
                    "_definition.yml"
                ):
                    result.add_error(
                        f"Agent definition '{filename}' must end with '_definition.yaml'"
                    )

                if len(parts) == idx + 3:
                    category = parts[idx + 1]
                    if not filename.startswith(category + "_"):
                        result.add_error(
                            f"Agent definition '{filename}' must start with category prefix '{category}_'"
                        )
    except ValueError:
        pass

    if filename.endswith(".tmp") or filename.endswith(".bak") or filename == ".DS_Store":
        result.add_error(f"Prohibited file type/name: {filename}")

    return result

    return result


def main():
    parser = argparse.ArgumentParser(description="Lattice Lock Structure Validator")
    parser.add_argument(
        "--naming-only", action="store_true", help="Run only file naming validation"
    )
    parser.add_argument("path", nargs="?", default=".", help="Path to repository root")

    args = parser.parse_args()

    # Resolve the path - users can validate any directory, not just within the framework
    repo_path = Path(args.path).expanduser().resolve()

    if not repo_path.exists():
        print(f"Error: Path does not exist: {repo_path}")
        sys.exit(1)
        return  # Explicit return for test mocking of sys.exit

    if not repo_path.is_dir():
        print(f"Error: Path is not a directory: {repo_path}")
        sys.exit(1)
        return  # Explicit return for test mocking of sys.exit

    if args.naming_only:
        # Just walk and check naming
        overall_result = ValidationResult()
        for root, dirs, files in os.walk(repo_path):
            if ".git" in dirs:
                dirs.remove(".git")
            if "__pycache__" in dirs:
                dirs.remove("__pycache__")
            if ".venv" in dirs:
                dirs.remove(".venv")
            if ".construction" in dirs:
                dirs.remove(".construction")

            for d in dirs:
                folder_path = os.path.join(root, d)
                res = validate_folder_naming(folder_path, repo_path)
                overall_result.errors.extend(res.errors)
                overall_result.warnings.extend(res.warnings)
                if not res.valid:
                    overall_result.valid = False

            for filename in files:
                file_path = os.path.join(root, filename)
                res = validate_file_naming(file_path, repo_path)
                overall_result.errors.extend(res.errors)
                overall_result.warnings.extend(res.warnings)
                if not res.valid:
                    overall_result.valid = False
    else:
        overall_result = validate_repository_structure(repo_path)

    if not overall_result.valid:
        print("Validation FAILED:")
        for error in overall_result.errors:
            print(f"  [ERROR] {error.message}")
        sys.exit(1)
    else:
        print("Validation PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
