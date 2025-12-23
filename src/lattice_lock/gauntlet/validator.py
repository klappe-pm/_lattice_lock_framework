"""
Gauntlet Policy Validator

Provides validation logic for semantic contracts defined in lattice.yaml.
"""

import re
import logging

logger = logging.getLogger(__name__)

class PolicyViolation(Exception):
    """Raised when a Gauntlet policy is violated."""
    pass

class GauntletValidator:
    """
    Validates data against semantic contracts.
    """

    @staticmethod
    def check_policy(policy_name: str, context: str) -> bool:
        """
        Check if the context violates the named policy.

        Args:
            policy_name: The name of the policy to check (e.g., 'no-direct-db-access')
            context: The text/data to validate

        Returns:
            True if valid, False otherwise.
        """
        if policy_name == "no-direct-db-access":
            # Disallow direct SQL keywords in the context
            forbidden = [r"\bSELECT\b", r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b", r"\bDROP\b"]
            for pattern in forbidden:
                if re.search(pattern, context, re.IGNORECASE):
                    logger.warning(f"Policy violation: {policy_name} - Found pattern {pattern}")
                    return False
            return True
        
        if policy_name == "no-pii":
            # Simple regex for email/phone as PII placeholders
            email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
            if re.search(email_pattern, context):
                 logger.warning(f"Policy violation: {policy_name} - Found email")
                 return False
            return True

        # Default to pass for unknown policies (warning)
        logger.debug(f"Unknown policy: {policy_name}. Passing by default.")
        return True

    @classmethod
    def enforce(cls, policy_name: str, context: str):
        """Enforce a policy, raising PolicyViolation if it fails."""
        if not cls.check_policy(policy_name, context):
            raise PolicyViolation(f"Policy '{policy_name}' violated in context.")
