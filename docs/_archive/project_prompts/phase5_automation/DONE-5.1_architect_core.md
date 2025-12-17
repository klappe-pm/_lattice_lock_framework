# Task 5.1: Prompt Architect Core Agent Design

**Status:** Approved
**Owner:** Gemini Antimatter
**Implementation Task:** 5.3 (Devin AI)

---

## 1. Objective
An agent that takes a high-level goal ("Add a login page") and generates the sequence of prompts needed for a coding agent to build it.

## 2. Cognitive Architecture

1.  **Ingest:** Read `task.md`, codebase map, and `lattice.yaml`.
2.  **Breakdown:** Split user goal into atomic steps (Design -> Scaffold -> Implement -> Test).
3.  **Prompt Generation:** For each step, fill a template:
    *   *Context:* Files to edit.
    *   *Constraint:* "Do not touch `core.py`".
    *   *Goal:* "Implement function X".

## 3. The "Meta-Prompt"
The Prompt Architect runs on a Chain-of-Thought model (o1-pro or Claude Opus).

> "You are the Architect. Your goal is not to write code, but to write instructions for a Junior Dev (Devin). Break this task into 3 safe steps."
