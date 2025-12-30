import json

from lattice_lock.context.serialization import ContextHandoff


def test_handoff_save_load(tmp_path):
    handler = ContextHandoff(project_dir=tmp_path)
    messages = [{"role": "user", "content": "Hello"}]
    metadata = {"model": "gpt-4o"}

    file_path = handler.save("test_handoff", messages, metadata)

    assert file_path.exists()
    assert file_path.suffix == ".json"

    loaded_data = handler.load("test_handoff")
    assert loaded_data["messages"] == messages
    assert loaded_data["metadata"] == metadata
    assert loaded_data["version"] == "1.0"


def test_handoff_serialize():
    handler = ContextHandoff()
    messages = [{"role": "user", "content": "Hello"}]
    serialized = handler.serialize(messages)
    data = json.loads(serialized)
    assert data["messages"] == messages


def test_handoff_list(tmp_path):
    handler = ContextHandoff(project_dir=tmp_path)
    handler.save("handoff1", [])
    handler.save("handoff2", [])

    handoffs = handler.list_handoffs()
    assert "handoff1" in handoffs
    assert "handoff2" in handoffs
    assert len(handoffs) == 2
