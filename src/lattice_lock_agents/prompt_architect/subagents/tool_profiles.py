from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import yaml
import os

class ToolProfile(BaseModel):
    name: str
    identifier: str
    strengths: List[str] = Field(default_factory=list)
    preferred_files: List[str] = Field(default_factory=list)

    def calculate_affinity(self, task_description: str, task_files: List[str]) -> float:
        score = 0.0

        # Capability matching based on strengths
        for strength in self.strengths:
            if strength.lower() in task_description.lower():
                score += 0.2

        # File ownership matching
        for file in task_files:
            for pattern in self.preferred_files:
                if pattern.endswith('/'): # Directory match
                    if pattern in file:
                        score += 0.5
                elif pattern in file: # File match
                    score += 0.5

        return min(score, 1.0) # Normalize to max 1.0

class Task(BaseModel):
    id: str
    description: str
    files: List[str] = Field(default_factory=list)
    type: str = "general"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ToolAssignment(BaseModel):
    task_id: str
    tool: str
    confidence: float
    files_owned: List[str] = Field(default_factory=list)
    reasoning: str = ""

def load_tool_profiles(yaml_path: str) -> Dict[str, ToolProfile]:
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Tool profile configuration not found at {yaml_path}")

    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)

    profiles = {}
    if 'tool_profiles' in data:
        for key, profile_data in data['tool_profiles'].items():
            profiles[key] = ToolProfile(**profile_data)

    return profiles
