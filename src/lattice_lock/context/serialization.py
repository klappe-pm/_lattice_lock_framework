import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from lattice_lock.orchestrator.types import APIResponse

logger = logging.getLogger(__name__)

class ContextHandoff:
    """
    Manages serialization and deserialization of conversation context.
    """

    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.handoff_dir = self.project_dir / ".lattice-lock" / "handoffs"
        self.handoff_dir.mkdir(parents=True, exist_ok=True)

    def serialize(self, messages: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Serialize messages and metadata to a JSON string.
        """
        handoff_data = {
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "messages": messages,
            "metadata": metadata or {}
        }
        return json.dumps(handoff_data, indent=2)

    def save(self, name: str, messages: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> Path:
        """
        Save handoff data to a file.
        """
        file_path = self.handoff_dir / f"{name}.json"
        content = self.serialize(messages, metadata)
        file_path.write_text(content)
        logger.info(f"Context handoff saved to {file_path}")
        return file_path

    def load(self, name: str) -> Dict[str, Any]:
        """
        Load handoff data from a file.
        """
        file_path = self.handoff_dir / f"{name}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Handoff file not found: {file_path}")
        
        data = json.loads(file_path.read_text())
        return data

    def list_handoffs(self) -> List[str]:
        """
        List all available handoffs.
        """
        return [f.stem for f in self.handoff_dir.glob("*.json")]
