"""
Approver Agent - The Single Authority for Testing and Quality Approvals.

The Approver Agent is ENABLED BY DEFAULT and owns:
- Test reviews and quality enforcement
- 90% code coverage enforcement
- Documentation validation
- Requirements traceability
- Bug automation coordination

Toggle via settings: settings.agents.approver_agent.enabled
Or environment: LATTICE_APPROVER_ENABLED=false
"""

from lattice_lock.agents.approver.agent import ApproverAgent
from lattice_lock.agents.approver.models import (
    ApprovalResult,
    CoverageResult,
    DocumentationResult,
    TestReviewResult,
)

__all__ = [
    "ApproverAgent",
    "ApprovalResult",
    "CoverageResult",
    "DocumentationResult",
    "TestReviewResult",
]
