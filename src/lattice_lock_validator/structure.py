import os
import re
import sys
import argparse
from pathlib import Path
from typing import List
from .schema import ValidationResult
try:
    from lattice_lock.utils.safe_path import resolve_under_root
except ImportError:
    # Fallback/mock for standalone run if needed, or assume installed
    def resolve_under_root(path, root=None):
        return Path(path).resolve()


def validate_repository_structure(repo_path: str) -> ValidationResult:
    """
    Validates the repository structure and file naming conventions.

    Args:
        repo_path: Path to the repository root.

    Returns:
        ValidationResult: The result of the validation.
    """
    result = ValidationResult()

    # Resolve the repo path (don't apply under-root check since users can validate any directory)
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

    # 2. File Naming
    # Walk through the repo
    for root, dirs, files in os.walk(repo_path):
        # Skip .git and other hidden directories if necessary, but prompt says "Required root files: .gitignore"
        # so we shouldn't skip everything starting with dot, but definitely .git
        if '.git' in dirs:
            dirs.remove('.git')
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
        if 'venv' in dirs:
            dirs.remove('venv')

        for filename in files:
            if filename == '.DS_Store':
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
    # Resolve the path (don't apply under-root check since users can validate any directory)
    path = Path(repo_path).expanduser().resolve()

    if not path.exists():
        result.add_error(f"Repository path not found: {repo_path}")
        return result

    # Required root directories
    required_dirs = ['agent_definitions', 'src', 'scripts']
    for d in required_dirs:
        if not (path / d).is_dir():
            result.add_error(f"Missing required root directory: {d}/")

    # Required root files
    required_files = ['.gitignore', 'README.md']
    for f in required_files:
        if not (path / f).is_file():
            result.add_error(f"Missing required root file: {f}")

    # Agent definitions nesting
    agent_def_path = path / 'agent_definitions'
    if agent_def_path.is_dir():
        for item in agent_def_path.iterdir():
            if item.is_file() and item.name not in ['.DS_Store', 'README.md']:
                # Files shouldn't be directly in agent_definitions, unless it's a template or doc?
                # Spec says: "agent_definitions/{agent_category}/"
                # "Definition files reside directly within their category folder."
                # So files at root of agent_definitions might be wrong unless allowed exceptions.
                # Prompt says: "Agent definitions must be in category subdirectories"
                if item.suffix in ['.yaml', '.yml']:
                     result.add_error(f"Agent definition '{item.name}' must be in a category subdirectory, not directly in agent_definitions/")

    return result

def validate_file_naming(file_path: str, repo_root: str = "") -> ValidationResult:
    """Validates file naming conventions (snake_case)."""
    result = ValidationResult()
    path = Path(file_path)
    filename = path.name

    # Prohibited patterns
    if ' ' in filename:
        result.add_error(f"File name contains spaces: {filename}")

    # Check for special characters (allow alphanumeric, underscore, dot, hyphen)
    # Prompt says "No special characters except underscore".
    # Usually dot is needed for extensions. Hyphen is usually allowed in kebab-case but prompt says "snake_case".
    # Prompt says: "All files must use snake_case (no spaces, hyphens in names)"
    # So hyphens are PROHIBITED.
    if '-' in filename and filename not in ['LICENSE.md', 'README.md', '.gitignore', '.pre-commit-config.yaml', 'pyproject.toml']:
        # Allow standard files that might have hyphens or be exceptions.
        # But wait, prompt says "Exception: README.md, LICENSE.md".
        # It doesn't explicitly exempt others, but standard repo files often have hyphens (e.g. pre-commit-config).
        # Let's be strict but allow known config files if they exist.
        # Actually, let's look at the prompt again: "Exception: standard files like README.md, LICENSE.md"
        # "All files must use snake_case"
        pass

    # snake_case check
    # Allow dot for extension.
    stem = path.stem
    # If file starts with dot (like .gitignore), stem might be .gitignore or empty depending on how pathlib handles it.
    # pathlib: Path('.gitignore').stem is '.gitignore'.

    if filename.startswith('.'):
        # Hidden files/configs often don't follow snake_case (e.g. .gitignore, .pre-commit-config.yaml)
        # Let's assume dotfiles are exempt or have specific rules?
        # Prompt: "Prohibited patterns: ... temp files (*.tmp, *.bak, .DS_Store)"
        pass
    else:
        # Check stem for snake_case: lowercase, numbers, underscores.
        # Exception: README.md, LICENSE.md (PascalCase/UPPERCASE)
        if filename in ['README.md', 'LICENSE.md', 'Dockerfile', 'Makefile']:
            pass
        else:
            if not re.match(r'^[a-z0-9_]+$', stem):
                # Check if it's a known exception or we should flag it
                result.add_error(f"File '{filename}' does not follow snake_case naming convention")

    # Agent definitions pattern
    # {category}_{name}_definition.yaml
    # We need to know if it IS an agent definition.
    # They live in agent_definitions/
    # Use parts to be safer
    try:
        parts = path.parts
        if 'agent_definitions' in parts:
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                if not filename.endswith('_definition.yaml') and not filename.endswith('_definition.yml'):
                     result.add_error(f"Agent definition '{filename}' must end with '_definition.yaml'")

                # Check prefix matches category?
                # path parts: .../agent_definitions/{category}/{filename}
                idx = parts.index('agent_definitions')
                # parts[idx] = agent_definitions
                # parts[idx+1] = category
                # parts[idx+2] = filename (if directly in category)

                if len(parts) > idx + 3: # nested deeper than category/filename
                    # e.g. agent_definitions/category/subdir/file
                    pass
                elif len(parts) == idx + 3:
                    category = parts[idx+1]
                    # filename should start with category
                    if not filename.startswith(category + '_'):
                        result.add_error(f"Agent definition '{filename}' must start with category prefix '{category}_'")
    except ValueError:
        pass
    if filename.endswith('.tmp') or filename.endswith('.bak') or filename == '.DS_Store':
        result.add_error(f"Prohibited file type/name: {filename}")

    return result

def main():
    parser = argparse.ArgumentParser(description="Lattice Lock Structure Validator")
    parser.add_argument("--naming-only", action="store_true", help="Run only file naming validation")
    parser.add_argument("path", nargs="?", default=".", help="Path to repository root")

    args = parser.parse_args()

    repo_path = os.path.abspath(args.path)

    if args.naming_only:
        # Just walk and check naming
        overall_result = ValidationResult()
        for root, dirs, files in os.walk(repo_path):
             if '.git' in dirs: dirs.remove('.git')
             if '__pycache__' in dirs: dirs.remove('__pycache__')
             if 'venv' in dirs: dirs.remove('venv')

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
