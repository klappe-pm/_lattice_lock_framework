import os
import re
from pathlib import Path

# Configuration
PROJECT_ROOT = "/Users/kevinlappe/Documents/lattice-lock-framework"
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "docs/04-meta/SHADOW_MAP.md")


def find_files(directory, extensions):
    files = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    return files


def parse_frontmatter(file_path):
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Simple regex to extract file_ids from YAML frontmatter
    # file_ids: [id1, id2] or file_ids: \n - id1
    match = re.search(r"^---\s+.*?\s+file_ids:\s*\[(.*?)\]", content, re.DOTALL | re.MULTILINE)
    if match:
        ids_str = match.group(1)
        ids = [i.strip().strip("'").strip('"') for i in ids_str.split(",") if i.strip()]
        return ids

    # Check for multiline format
    # file_ids:
    #   - id1
    # Note: simplified, might need more robust parsing if complex
    return []


def scan_docs():
    doc_map = {}
    files = find_files(DOCS_DIR, [".md"])
    for f in files:
        ids = parse_frontmatter(f)
        rel_path = os.path.relpath(f, PROJECT_ROOT)
        for i in ids:
            doc_map[i] = rel_path
    return doc_map


def scan_src():
    src_files = []
    files = find_files(SRC_DIR, [".py"])
    for f in files:
        if "__init__.py" in f:
            continue
        rel_path = os.path.relpath(f, PROJECT_ROOT)
        src_files.append(rel_path)
    return src_files


def generate_report(doc_map, src_files):
    # This is a heuristic report.
    # In a real scenario, we'd look for mapping annotations in source code if they existed,
    # or rely on naming conventions. Here we list what we found.

    with open(OUTPUT_FILE, "w") as f:
        f.write("# Documentation Shadow Map\n\n")
        f.write("Generated report linking source files to documentation.\n\n")

        f.write("## Documentation with IDs\n\n")
        f.write("| File ID | Document Path |\n")
        f.write("|---------|---------------|\n")
        for file_id, path in sorted(doc_map.items()):
            f.write(f"| `{file_id}` | `{path}` |\n")

        f.write("\n## User-Facing Source Files Scan\n\n")
        f.write(f"Total Python files found: {len(src_files)}\n\n")

        # Heuristic matching attempt
        f.write("## Potential Gaps (Heuristic Match)\n\n")
        f.write("| Source File | Potential Doc Match (by name) | Status |\n")
        f.write("|-------------|-------------------------------|--------|\n")

        for src in sorted(src_files):
            basename = os.path.basename(src).replace(".py", "").replace("_", "-")
            # specific override for cli/init
            found = False
            for file_id in doc_map:
                if basename in file_id:
                    f.write(f"| `{src}` | `{doc_map[file_id]}` (`{file_id}`) | ✅ |\n")
                    found = True
                    break

            if not found:
                f.write(f"| `{src}` | - | ⚠️ |\n")


if __name__ == "__main__":
    print("Scanning documentation...")
    docs = scan_docs()
    print(f"Found {len(docs)} documented IDs.")

    print("Scanning source code...")
    src = scan_src()
    print(f"Found {len(src)} source files.")

    print("Generating report...")
    generate_report(docs, src)
    print(f"Report generated at {OUTPUT_FILE}")
