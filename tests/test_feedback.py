"""
Tests for the Feedback Collection System
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from lattice_lock.feedback import (
    FeedbackCategory,
    FeedbackCollector,
    FeedbackPriority,
)


@pytest.fixture
def feedback_file():
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "feedback.json"


@pytest.fixture
def collector(feedback_file):
    return FeedbackCollector(feedback_file)


def test_initialization_creates_file(feedback_file):
    assert not feedback_file.exists()
    FeedbackCollector(feedback_file)
    assert feedback_file.exists()
    assert feedback_file.read_text() == "[]"


def test_submit_feedback(collector):
    fid = collector.submit(
        content="Test feedback",
        category=FeedbackCategory.BUG,
        priority=FeedbackPriority.HIGH,
        source="unit_test",
    )

    assert fid is not None
    assert len(fid) > 0  # basic check for UUID

    items = collector.list_feedback()
    assert len(items) == 1
    assert items[0].id == fid
    assert items[0].content == "Test feedback"
    assert items[0].category == FeedbackCategory.BUG
    assert items[0].priority == FeedbackPriority.HIGH
    assert items[0].source == "unit_test"


def test_get_feedback(collector):
    fid = collector.submit("Search me")

    item = collector.get(fid)
    assert item is not None
    assert item.content == "Search me"

    assert collector.get("non-existent") is None


def test_list_feedback_filters(collector):
    collector.submit("Bug 1", category=FeedbackCategory.BUG, source="user_a")
    collector.submit("Feature 1", category=FeedbackCategory.FEATURE, source="user_b")
    collector.submit("Bug 2", category=FeedbackCategory.BUG, source="user_b")

    all_bugs = collector.list_feedback(category=FeedbackCategory.BUG)
    assert len(all_bugs) == 2
    assert all(i.category == FeedbackCategory.BUG for i in all_bugs)

    user_b_items = collector.list_feedback(source="user_b")
    assert len(user_b_items) == 2
    assert all(i.source == "user_b" for i in user_b_items)

    user_b_bugs = [
        i for i in collector.list_feedback(category=FeedbackCategory.BUG) if i.source == "user_b"
    ]
    # Ideally list_feedback might support multiple filters or we chain them
    # The current implementation supports simple individual filters in the signature,
    # but let's test the specific method behavior

    # Testing combined manual filter based on method capability
    # The method currently supports category OR source if passed individually,
    # or both if implemented. Let's check implementation.
    # Ah, I implemented it to filter sequentially.

    items = collector.list_feedback(category=FeedbackCategory.BUG, source="user_b")
    assert len(items) == 1
    assert items[0].content == "Bug 2"


def test_persistence(feedback_file):
    # 1. Create and save
    c1 = FeedbackCollector(feedback_file)
    c1.submit("Persisted item")

    # 2. Reload from same file
    c2 = FeedbackCollector(feedback_file)
    items = c2.list_feedback()
    assert len(items) == 1
    assert items[0].content == "Persisted item"


def test_malformed_file_handling(feedback_file):
    feedback_file.write_text("{invalid_json")

    c = FeedbackCollector(feedback_file)
    # Should handle gracefully and return empty or maybe overwrite on next save
    assert c.list_feedback() == []

    # Should be able to write new data even if old was corrupt (depends on implementation choice, usually overwrite/append)
    # My implementation loads, appends, saves. If load returns [], it will overwrite the bad file with new list.
    c.submit("New item")
    assert len(c.list_feedback()) == 1
