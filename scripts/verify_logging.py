import logging
import sys

# Ensure no handlers are configured on root logger initially
initial_handlers = len(logging.getLogger().handlers)

import lattice_lock

# Check if lattice_lock added handlers to root logger (it shouldn't)
final_handlers = len(logging.getLogger().handlers)

if final_handlers > initial_handlers:
    print(f"FAIL: Root logger handlers increased from {initial_handlers} to {final_handlers}")
    sys.exit(1)

# Check if lattice_lock logger is configured
ll_logger = logging.getLogger("lattice_lock")
if not any(isinstance(h, logging.NullHandler) for h in ll_logger.handlers):
    print("FAIL: lattice_lock logger missing NullHandler")
    sys.exit(1)

print("SUCCESS: Logging configuration verified")
