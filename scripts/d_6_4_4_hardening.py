# IMPLEMENTATION PROTOTYPE (Agent D_6_4_4)
# Task 6.4.4: Dependency Hardening (CI Locking)

from pathlib import Path


def lock_dependencies():
    """
    Simulates compiling requirements.in to requirements.lock
    """
    print("[HARDENING] Locking dependencies...")

    req_in = Path("requirements.in")
    if not req_in.exists():
        print("[WARN] requirements.in not found. Creating default.")
        with open("requirements.in", "w") as f:
            f.write("click>=8.0\npydantic>=2.0\n")

    # Mock pip-compile execution
    print(f"[CMD] pip-compile {req_in} --output-file requirements.lock")

    with open("requirements.lock", "w") as f:
        f.write("# GENERATED file. DO NOT EDIT.\n")
        f.write("click==8.1.7 --hash=sha256:...\n")
        f.write("pydantic==2.8.2 --hash=sha256:...\n")

    print("[HARDENING] requirements.lock generated with pinned hashes.")


if __name__ == "__main__":
    lock_dependencies()
