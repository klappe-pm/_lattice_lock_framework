# GitHub Labels Guide

This document defines how labels are used in the Lattice Lock Framework repository.

## Label Categories

### Type Labels
These labels indicate the type of change or issue. **One type label should be applied to each PR/issue.**

- `feat` - Feature change or new functionality
- `fix` - Bug fix
- `chore` - Chore/maintenance tasks (e.g., dependency updates, tooling)
- `docs` - Documentation changes
- `refactor` - Code refactoring without changing functionality
- `enhancement` - New feature request (for issues)
- `bug` - Something isn't working (for issues)

### Source Labels
These labels indicate the origin or authorship of the contribution. **One source label should be applied to each PR.**

- `human` - Authored by a human developer
- `devin` - Authored by Devin.ai
- `llm` - Authored by an LLM/agent (including Warp Agent)

### Technology/Component Labels
These labels identify which technology stack or component is affected.

- `python` - Python dependencies or Python-related changes
- `frontend` - Frontend related changes
- `npm` - NPM dependencies
- `docker` - Docker related changes
- `javascript` - JavaScript code updates
- `github-actions` - GitHub Actions workflow changes

### Dependency Labels
Automatically applied by Dependabot for dependency updates.

- `dependencies` - Pull requests that update a dependency file (always included with dependency updates)
- Technology-specific labels (`python`, `npm`, `docker`, `github-actions`) are also applied based on the ecosystem

### Issue Management Labels
Standard GitHub labels for issue triage and management.

- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `question` - Further information is requested
- `duplicate` - This issue or pull request already exists
- `invalid` - This doesn't seem right
- `wontfix` - This will not be worked on
- `documentation` - Improvements or additions to documentation

## Labeling Guidelines

### For Pull Requests
1. **Required**: Apply one Type label (`feat`, `fix`, `chore`, `docs`, or `refactor`)
2. **Required**: Apply one Source label (`human`, `devin`, or `llm`)
3. **Optional**: Apply relevant Technology/Component labels as needed
4. Dependabot PRs are automatically labeled and don't require manual source labels

### For Issues
1. Apply relevant Type labels (`bug`, `enhancement`, `question`, `documentation`)
2. Apply Technology/Component labels to indicate affected areas
3. Apply management labels (`good first issue`, `help wanted`) as appropriate

## Dependabot Configuration

Dependabot automatically applies labels based on the package ecosystem:

- **Python updates**: `dependencies`, `python`
- **NPM updates**: `dependencies`, `frontend`, `npm`
- **Docker updates**: `dependencies`, `docker`
- **GitHub Actions updates**: `dependencies`, `github-actions`

See `.github/dependabot.yml` for the complete configuration.
