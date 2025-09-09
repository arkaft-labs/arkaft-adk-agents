# ADK Agents Setup Guide

This guide provides step-by-step instructions for setting up the ADK Agents system.

## Prerequisites

Before installing the ADK Agents system, ensure you have:

- **Kiro IDE** with MCP support enabled
- **Rust toolchain** (rustc 1.70+ and Cargo)
- **Python 3.8+** with virtual environment support
- **Git** for version control
- An **ADK project** or intention to create one

## Quick Setup

### 1. Verify Prerequisites

```bash
# Check Rust installation
rustc --version
cargo --version

# Check Python installation
python --version
python -m venv --help

# Verify Kiro IDE MCP support
# (Check Kiro documentation for MCP configuration)
```

### 2. Build MCP Server

```bash
# Navigate to the MCP server directory
cd ../arkaft-mcp-google-adk

# Build the server in release mode
cargo build --release

# Verify the build
ls -la target/release/arkaft-mcp-google-adk
```

### 3. Configure MCP in Kiro

```bash
# Copy the MCP configuration
cp ../mcp-config-update.json ../.kiro/settings/mcp.json

# Or manually add to your existing MCP configuration:
```

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

### 4. Set Up Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install any required dependencies (if requirements.txt exists)
pip install -r requirements.txt
```

### 5. Configure Agents

```bash
# Create agent configuration directory
mkdir -p .kiro/settings

# Copy basic configuration
cp arkaft-adk-agents/examples/basic-setup.json .kiro/settings/adk-agents.json

# Or start with advanced configuration
cp arkaft-adk-agents/examples/advanced-setup.json .kiro/settings/adk-agents.json
```

### 6. Verify Installation

```bash
# Test MCP server connectivity
python test-mcp-server.py

# Run comprehensive verification
./verify-mcp-setup.sh

# Test individual agents
python .kiro/agents/test-adk-code-review-agent.py
```

## Detailed Setup

### MCP Server Configuration

#### Building from Source

```bash
cd arkaft-mcp-google-adk

# Clean previous builds
cargo clean

# Build with optimizations
cargo build --release

# Run tests to verify functionality
cargo test

# Check for any warnings
cargo clippy
```

#### Environment Configuration

Set up environment variables for the MCP server:

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export RUST_LOG=info
export ADK_DOCS_VERSION=latest
export MCP_SERVER_PATH="./arkaft-mcp-google-adk/target/release/arkaft-mcp-google-adk"
```

### Agent Configuration

#### Basic Configuration

Start with the basic configuration for initial setup:

```json
{
  "version": "1.0",
  "agents": {
    "adk-code-review": {
      "enabled": true,
      "mcpServer": "arkaft-google-adk"
    },
    "adk-architecture": {
      "enabled": true,
      "mcpServer": "arkaft-google-adk"
    },
    "adk-documentation": {
      "enabled": true,
      "mcpServer": "arkaft-google-adk"
    },
    "adk-project-assistant": {
      "enabled": true,
      "mcpServer": "arkaft-google-adk"
    }
  }
}
```

#### Hook Configuration

Ensure hook files are properly placed:

```bash
# Verify hook files exist
ls -la .kiro/hooks/adk-*.kiro.hook

# If missing, they should be created automatically
# or copy from examples if available
```

### Project Detection Setup

#### ADK Project Markers

Ensure your project is detected as an ADK project by including:

1. **ADK dependencies in Cargo.toml:**
   ```toml
   [dependencies]
   google-adk = "0.1.0"
   # or other ADK-related dependencies
   ```

2. **Project structure patterns:**
   ```
   src/
   ├── lib.rs or main.rs
   ├── services/
   ├── models/
   └── handlers/
   ```

3. **Configuration files:**
   - `Cargo.toml` with ADK dependencies
   - ADK-specific configuration files

### Troubleshooting Setup Issues

#### MCP Server Issues

```bash
# Test MCP server manually
./arkaft-mcp-google-adk/target/release/arkaft-mcp-google-adk

# Check for missing dependencies
ldd ./arkaft-mcp-google-adk/target/release/arkaft-mcp-google-adk  # Linux
otool -L ./arkaft-mcp-google-adk/target/release/arkaft-mcp-google-adk  # macOS

# Rebuild if necessary
cd arkaft-mcp-google-adk
cargo clean
cargo build --release
```

#### Configuration Issues

```bash
# Validate JSON syntax
python -c "import json; json.load(open('.kiro/settings/adk-agents.json'))"

# Validate against schema
python .kiro/agents/validate_config.py

# Reset to defaults if corrupted
cp arkaft-adk-agents/examples/basic-setup.json .kiro/settings/adk-agents.json
```

#### Permission Issues

```bash
# Ensure MCP server is executable
chmod +x arkaft-mcp-google-adk/target/release/arkaft-mcp-google-adk

# Check directory permissions
ls -la .kiro/
ls -la .kiro/settings/
ls -la .kiro/hooks/
```

## Advanced Setup

### Custom Agent Development

1. **Set up development environment:**
   ```bash
   # Install development dependencies
   pip install pytest pytest-asyncio

   # Set up pre-commit hooks (if available)
   pre-commit install
   ```

2. **Create custom agent:**
   ```bash
   # Copy template
   cp arkaft-adk-agents/examples/custom-agent-example/custom_security_agent.py .kiro/agents/

   # Customize for your needs
   # Add to configuration
   ```

### Performance Optimization

1. **Configure caching:**
   ```json
   {
     "caching": {
       "enabled": true,
       "strategies": {
         "mcpResponses": {
           "ttl": 3600,
           "maxSize": 100
         }
       }
     }
   }
   ```

2. **Adjust resource limits:**
   ```json
   {
     "performance": {
       "resourceLimits": {
         "maxFileSize": "50KB",
         "timeoutMs": 30000,
         "maxRetries": 3
       }
     }
   }
   ```

### Team Setup

1. **Shared configuration:**
   ```bash
   # Add configuration to version control
   git add .kiro/settings/adk-agents.json
   git commit -m "Add ADK agents configuration"
   ```

2. **Environment-specific settings:**
   ```bash
   # Create environment-specific overrides
   cp .kiro/settings/adk-agents.json .kiro/settings/adk-agents.local.json
   
   # Add local config to .gitignore
   echo ".kiro/settings/adk-agents.local.json" >> .gitignore
   ```

## Verification

### Complete System Test

```bash
# Run all verification steps
./verify-mcp-setup.sh

# Expected output:
# ✓ MCP server binary exists
# ✓ MCP server starts successfully
# ✓ All MCP tools available
# ✓ Agent configuration valid
# ✓ Hooks properly configured
# ✓ Project detection working
```

### Individual Component Tests

```bash
# Test MCP server
python test-mcp-server.py

# Test agents
python .kiro/agents/test-adk-code-review-agent.py
python .kiro/agents/test-adk-architecture-agent.py
python .kiro/agents/test-adk-docs-agent.py
python .kiro/agents/test-adk-project-assistant-agent.py

# Validate configuration
python .kiro/agents/validate_config.py
```

## Next Steps

After successful setup:

1. **Test with a real ADK project:**
   - Open an ADK project in Kiro
   - Save a Rust file to trigger code review
   - Try manual documentation assistance

2. **Customize configuration:**
   - Adjust agent sensitivity
   - Configure hook triggers
   - Set up custom patterns

3. **Monitor performance:**
   - Check agent response times
   - Monitor resource usage
   - Adjust settings as needed

4. **Explore advanced features:**
   - Custom agent development
   - Workflow automation
   - Team collaboration features

## Support

- **Documentation:** See README.md, USER_GUIDE.md, and TROUBLESHOOTING.md
- **Examples:** Check the examples/ directory for configuration templates
- **Testing:** Use provided test scripts for diagnosis
- **Issues:** Check TROUBLESHOOTING.md for common problems and solutions