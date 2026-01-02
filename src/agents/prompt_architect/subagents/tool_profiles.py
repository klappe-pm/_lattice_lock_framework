import os
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ToolProfile(BaseModel):
    name: str
    identifier: str
    strengths: list[str] = Field(default_factory=list)
    preferred_files: list[str] = Field(default_factory=list)

    def calculate_affinity(self, task_description: str, task_files: list[str]) -> float:
        score = 0.0

        # Capability matching based on strengths
        for strength in self.strengths:
            if strength.lower() in task_description.lower():
                score += 0.2

        # File ownership matching
        for file in task_files:
            for pattern in self.preferred_files:
                if pattern.endswith("/"):  # Directory match
                    if pattern in file:
                        score += 0.5
                elif pattern in file:  # File match
                    score += 0.5

        return min(score, 1.0)  # Normalize to max 1.0


class Task(BaseModel):
    id: str
    description: str
    files: list[str] = Field(default_factory=list)
    type: str = "general"
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolAssignment(BaseModel):
    task_id: str
    tool: str
    confidence: float
    files_owned: list[str] = Field(default_factory=list)
    reasoning: str = ""


def load_tool_profiles(yaml_path: str) -> dict[str, ToolProfile]:
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Tool profile configuration not found at {yaml_path}")

    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    profiles = {}
    if "tool_profiles" in data:
        for key, profile_data in data["tool_profiles"].items():
            profiles[key] = ToolProfile(**profile_data)

    return profiles
