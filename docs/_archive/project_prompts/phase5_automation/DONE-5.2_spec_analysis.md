# Task 5.2: Specification Analysis Logic Design

**Status:** Approved
**Owner:** Gemini Antimatter
**Implementation Task:** 5.3 (Devin AI)

---

## 1. Input/Output
*   **Input:** Raw user request ("I need a React login page with JWT auth").
*   **Output:** Structured JSON Specification.

## 2. The Structured Spec (Pydantic)

```python
class Specification(BaseModel):
    goal: str
    components: List[str] # ["frontend/Login.tsx", "backend/auth.py"]
    requirements: List[str] # ["Use JWT", "store token in HttpOnly cookie"]
    constraints: List[str] # ["No external UI libraries"]
    complexity: int # 1-10
```

## 3. Analysis Prompt
The Agent uses a "Requirement Extraction" prompt:

> "Analyze the user request. Identify implicit requirements (e.g., if they ask for 'Login', they implicitly need 'Logout' and 'Password Reset'). convert to JSON."

## 4. Validation
The generated Spec is validated against `lattice.yaml` rules (e.g., checking if the requested components violate module boundaries).
