# Development Workflow

## Development Workflow

1. **Always read the required Claude files first** (`CLAUDE.md.md`, context, and plans)
2. **Set up environment** using `./setup_orchestrator.sh`
3. **Set up local models** (optional but recommended):
   - Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
   - Start service: `./start-ollama.sh`
   - Install models: `ollama pull llama3.2:8b`
   - Warm up models: `./warmup-models.sh`
4. **Test functionality** with `./orchestrator-cli.py test`
5. **Use analysis mode** to understand model selection: `./orchestrator-cli.py analyze "your task"`
6. **Make incremental changes** and test with integration test suite
7. **Follow naming conventions**: Use Title Case for folders, descriptive names for scripts

The orchestrator system is designed for extensibility - new models, providers, and interaction patterns can be added by extending the core classes and updating configuration files.
