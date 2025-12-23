import pytest
from lattice_lock.gauntlet.validator import GauntletValidator, PolicyViolation

def test_policy_no_direct_db_access():
    """Verify policy: no-direct-db-access with real checks."""
    # Test valid scenario
    safe_data = "Repository.get_user(id=1)"
    assert GauntletValidator.check_policy("no-direct-db-access", safe_data) is True

    # Test violation scenario
    unsafe_data = "SELECT * FROM users"
    assert GauntletValidator.check_policy("no-direct-db-access", unsafe_data) is False

def test_policy_violation_raises_error():
    """Verify that policy violations raise the correct exception."""
    unsafe_context = "DROP TABLE metadata;"
    with pytest.raises(PolicyViolation):
         GauntletValidator.enforce("no-direct-db-access", unsafe_context)

def test_policy_no_pii():
    """Verify policy: no-pii."""
    safe_data = "User profile updated."
    assert GauntletValidator.check_policy("no-pii", safe_data) is True

    unsafe_data = "Contact me at user@example.com"
    assert GauntletValidator.check_policy("no-pii", unsafe_data) is False
