# Arkaft ADK Agents System

A comprehensive agent framework that integrates with the arkaft-mcp-google-adk MCP server to provide intelligent development assistance for Google ADK projects through Kiro IDE hooks and specialized agents.

## Overview

The ADK Agents system provides automated code review, architecture validation, and development guidance for Google ADK projects. It consists of specialized agents that leverage the arkaft-mcp-google-adk MCP server's expertise to deliver real-time assistance through Kiro IDE integration.

### Key Features

- **Automated Code Review**: Real-time analysis of Rust files for ADK compliance and best practices
- **Architecture Validation**: Continuous validation of project architecture against Google ADK patterns
- **Documentation Assistant**: Context-aware ADK documentation and guidance
- **Project Assistant**: Comprehensive project setup and development guidance
- **Error Handling**: Robust error handling with graceful degradation when MCP server is unavailable
- **Agent Coordination**: Multi-agent coordination to prevent conflicts and ensure consistency

## Production Status

✅ **The ADK Agents system is production ready and fully operational**

All components are complete and tested:
- MCP Server integration with 4 production tools
- Automated code review with real-time analysis
- Architecture validation with best practices enforcement
- Documentation assistance with context-aware responses
- Project assistant with comprehensive guidance
- Configuration management with schema validation
- Enhanced error handling with graceful degradation
- Agent coordination with conflict resolution
- Performance monitoring with resource optimization
- Comprehensive test suite with full coverage
- Complete documentation and setup guides

## Project Structure

The ADK Agents system is now organized with clear separation between components:

```
arkaft-adk-agents/
├── agents/                    # ADK-specific agent implementations
│   ├── adk_architecture_agent.py
│   ├── adk_code_review_agent.py
│   ├── adk_project_assistant_agent.py
│   ├── adk_docs_agent.py
│   └── adk_config_manager.py
├── config/                    # Agent configuration files
│   ├── adk_architecture_agent.json
│   ├── adk_code_review_agent.json
│   ├── adk_project_assistant_agent.json
│   └── adk_docs_agent.json
├── tests/                     # Comprehensive test suite
│   ├── test_adk_architecture_agent.py
│   ├── test_adk_code_review_agent.py
│   ├── test_adk_project_assistant_agent.py
│   ├── test_adk_docs_agent.py
│   └── run_tests.py
├── docs/                      # Agent documentation
│   ├── adk_architecture_agent.md
│   ├── adk_code_review_agent.md
│   ├── adk_docs_assistant.md
│   └── adk_project_assistant.md
└── examples/                  # Usage examples and configurations
```

## Quick Start

### Prerequisites

- Kiro IDE with MCP support
- Rust toolchain (for arkaft-mcp-google-adk server)
- Python 3.8+ with virtual environment support
- Google ADK project or intention to create one

### Installation

1. **Set up the MCP Server**
   ```bash
   # Build the arkaft-mcp-google-adk server
   cd ../arkaft-mcp-google-adk
   cargo build --release
   ```

2. **Configure MCP in Kiro**
   ```bash
   # Update your Kiro MCP configuration
   cp mcp-config-update.json .kiro/settings/mcp.json
   ```

3. **Install Agent Dependencies**
   ```bash
   # Set up Python virtual environment
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   
   # Install required packages (if any additional dependencies needed)
   pip install -r requirements.txt  # if requirements.txt exists
   ```

4. **Verify Installation**
   ```bash
   # Test MCP server connectivity
   python test-mcp-server.py
   
   # Verify complete setup
   ./verify-mcp-setup.sh
   ```

### Basic Usage

Once installed, the agents will automatically activate when working with ADK projects:

- **Code Review**: Save any `.rs` file in an ADK project to trigger automatic review
- **Architecture Validation**: Modify architectural files (`lib.rs`, `main.rs`, `Cargo.toml`) for validation
- **Documentation Help**: Use the `adk-help` trigger or manual activation for documentation assistance
- **Project Assistance**: Access comprehensive project guidance through the project assistant agent

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Kiro IDE      │    │   Agent System   │    │ arkaft-mcp-google-  │
│                 │    │                  │    │ adk MCP Server      │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │                     │
│ │   Hooks     │─┼────┼─│   Agents     │─┼────┼─ adk_query          │
│ │             │ │    │ │              │ │    │ review_rust_file    │
│ │ - Code      │ │    │ - Code Review │ │    │ validate_architecture│
│ │   Review    │ │    │ - Architecture│ │    │ get_best_practices  │
│ │ - Arch      │ │    │ - Docs        │ │    │                     │
│ │   Validator │ │    │ - Project     │ │    │                     │
│ │ - Docs      │ │    │   Assistant   │ │    │                     │
│ │   Assistant │ │    │               │ │    │                     │
│ └─────────────┘ │    │ └──────────────┘ │    │                     │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
```

## Components

### Agents

1. **ADK Code Review Agent** (`adk_code_review_agent.py`)
   - Automatically reviews Rust files for ADK compliance
   - Provides specific improvement suggestions
   - Identifies translation opportunities and architectural issues

2. **ADK Architecture Agent** (`adk_architecture_agent.py`)
   - Validates project architecture against ADK best practices
   - Checks component organization and dependency management
   - Ensures adherence to ADK architectural patterns

3. **ADK Documentation Agent** (`adk_docs_agent.py`)
   - Provides context-aware ADK documentation assistance
   - Retrieves relevant information based on current development context
   - Links to official Google ADK documentation and examples

4. **ADK Project Assistant Agent** (`adk_project_assistant_agent.py`)
   - Comprehensive project guidance and setup assistance
   - Architectural decision support and troubleshooting
   - Task breakdown and step-by-step development guidance

### Hooks

1. **adk-code-review.kiro.hook**
   - Triggers on `.rs` file saves in ADK projects
   - Activates Code Review Agent for automatic analysis

2. **adk-architecture-validator.kiro.hook**
   - Triggers on architectural file modifications
   - Activates Architecture Agent for validation

3. **adk-docs-assistant.kiro.hook**
   - Manual trigger with `adk-help` keyword
   - Activates Documentation Agent for assistance

### Configuration

- **Agent Settings**: `.kiro/settings/adk-agents.json`
- **MCP Configuration**: `.kiro/settings/mcp.json`
- **Hook Definitions**: `.kiro/hooks/*.kiro.hook`

## Configuration

### Agent Configuration

The main agent configuration is stored in `.kiro/settings/adk-agents.json`:

```json
{
  "agents": {
    "adk-project-assistant": {
      "enabled": true,
      "mcpServer": "arkaft-google-adk",
      "preferences": {
        "verbosity": "detailed",
        "autoSuggest": true,
        "adkVersion": "latest"
      }
    },
    "adk-code-review": {
      "enabled": true,
      "mcpServer": "arkaft-google-adk",
      "triggers": {
        "autoReview": true,
        "fileSizeLimit": "50KB",
        "excludePatterns": ["target/**", "*.test.rs"]
      }
    }
  },
  "hooks": {
    "adk-code-review": {
      "enabled": true,
      "sensitivity": "medium",
      "debounceMs": 2000
    }
  }
}
```

### MCP Server Configuration

Configure the arkaft-mcp-google-adk server in `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "arkaft-google-adk": {
      "command": "./arkaft-mcp-google-adk/target/release/arkaft-mcp-google-adk",
      "args": [],
      "env": {
        "RUST_LOG": "info",
        "ADK_DOCS_VERSION": "latest"
      },
      "disabled": false,
      "autoApprove": ["adk_query", "review_rust_file", "validate_architecture", "get_best_practices"]
    }
  }
}
```

## Error Handling

The system includes comprehensive error handling with graceful degradation:

- **Circuit Breaker Pattern**: Prevents cascade failures when MCP server is unavailable
- **Retry Logic**: Automatic retry with exponential backoff for transient failures
- **Fallback Responses**: Context-aware fallback guidance when MCP tools are unavailable
- **User-Friendly Messages**: Clear error messages with troubleshooting guidance

## Development

### Extending the System

To create custom agents:

1. Inherit from `BaseADKAgent` in `.kiro/agents/base_agent.py`
2. Implement required methods for your specific use case
3. Add configuration to `.kiro/settings/adk-agents.json`
4. Create corresponding hook files if needed

### Testing

```bash
# Test individual agents
python .kiro/agents/test-adk-code-review-agent.py
python .kiro/agents/test-adk-architecture-agent.py

# Test MCP server integration
python test-mcp-server.py

# Validate configuration
python .kiro/agents/validate_config.py

# Run comprehensive verification
./verify-mcp-setup.sh
```

## Documentation

### Setup and Configuration
- **[SETUP.md](SETUP.md)**: Complete setup instructions and verification steps
- **[USER_GUIDE.md](USER_GUIDE.md)**: Comprehensive guide for customizing agent behavior and hooks
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**: Common issues and solutions

### Development and Extension
- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)**: Guide for extending the system and creating custom agents
- **[examples/](examples/)**: Complete configuration examples and custom agent implementations

### Quick Links
- [Basic Setup Configuration](examples/basic-setup.json)
- [Advanced Setup Configuration](examples/advanced-setup.json)
- [Custom Agent Example](examples/custom-agent-example/)
- [Workflow Examples](examples/new-component-workflow/)

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## Contributing

1. Follow the spec-driven development process outlined in [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
2. Ensure all code passes quality checks (`cargo clippy`, `cargo fmt` for Rust)
3. Write comprehensive tests for new functionality
4. Update documentation for any changes
5. Test with provided verification scripts

## License

This project is part of the Arkaft Development Suite. See the main repository for license information.