# ADK Agents Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the ADK Agents system.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [MCP Server Issues](#mcp-server-issues)
- [Agent Problems](#agent-problems)
- [Hook Issues](#hook-issues)
- [Configuration Problems](#configuration-problems)
- [Performance Issues](#performance-issues)
- [Error Messages](#error-messages)

## Quick Diagnostics

### System Health Check

Run the comprehensive verification script:

```bash
./verify-mcp-setup.sh
```

This script checks:
- MCP server connectivity
- Agent configuration validity
- Hook registration status
- Required dependencies

### Individual Component Testing

Test specific components:

```bash
# Test MCP server
python test-mcp-server.py

# Test individual agents
python .kiro/agents/test-adk-code-review-agent.py
python .kiro/agents/test-adk-architecture-agent.py

# Validate configuration
python .kiro/agents/validate_config.py
```

## MCP Server Issues

### MCP Server Won't Start

**Symptoms:**
- Agents report "MCP server unavailable"
- No response from MCP tools
- Connection timeout errors

**Diagnosis:**
```bash
# Check if the MCP server binary exists
ls -la arkaft-mcp-google-adk/target/release/arkaft-mcp-google-adk

# Try running the server manually
./arkaft-mcp-google-adk/target/release/arkaft-mcp-google-adk

# Check MCP configuration
cat .kiro/settings/mcp.json
```

**Solutions:**

1. **Build the MCP server:**
   ```bash
   cd arkaft-mcp-google-adk
   cargo build --release
   ```

2. **Check configuration path:**
   ```json
   {
     "mcpServers": {
       "arkaft-google-adk": {
         "command": "./arkaft-mcp-google-adk/target/release/arkaft-mcp-google-adk",
         "args": [],
         "disabled": false
       }
     }
   }
   ```

3. **Verify permissions:**
   ```bash
   chmod +x arkaft-mcp-google-adk/target/release/arkaft-mcp-google-adk
   ```

### MCP Tools Not Available

**Symptoms:**
- "Tool not found" errors
- Partial functionality
- Agents falling back to manual guidance

**Diagnosis:**
```bash
# Test specific MCP tools
python -c "
import json
from pathlib import Path
# Test tool availability
print('Testing MCP tools...')
"
```

**Solutions:**

1. **Verify tool registration:**
   Check that all four tools are available:
   - `adk_query`
   - `review_rust_file`
   - `validate_architecture`
   - `get_best_practices`

2. **Check auto-approval settings:**
   ```json
   {
     "mcpServers": {
       "arkaft-google-adk": {
         "autoApprove": ["adk_query", "review_rust_file", "validate_architecture", "get_best_practices"]
       }
     }
   }
   ```

### MCP Server Performance Issues

**Symptoms:**
- Slow response times
- Timeout errors
- High CPU usage

**Solutions:**

1. **Adjust timeout settings:**
   ```json
   {
     "performance": {
       "resourceLimits": {
         "timeoutMs": 60000,
         "maxRetries": 3
       }
     }
   }
   ```

2. **Enable caching:**
   ```json
   {
     "caching": {
       "enabled": true,
       "mcpResponses": {
         "ttl": 3600,
         "maxSize": 100
       }
     }
   }
   ```

## Agent Problems

### Agents Not Activating

**Symptoms:**
- No agent response when expected
- Hooks not triggering
- Silent failures

**Diagnosis:**
```bash
# Check agent configuration
python .kiro/agents/validate_config.py

# Check hook registration
ls -la .kiro/hooks/*.kiro.hook

# Test agent directly
python .kiro/agents/adk_code_review_agent.py --test
```

**Solutions:**

1. **Verify agent is enabled:**
   ```json
   {
     "agents": {
       "adk-code-review": {
         "enabled": true
       }
     }
   }
   ```

2. **Check project detection:**
   Ensure your project is detected as an ADK project:
   - Has ADK dependencies in `Cargo.toml`
   - Contains ADK-specific patterns
   - Meets file size requirements

3. **Verify hook conditions:**
   ```json
   {
     "hooks": {
       "adk-code-review": {
         "enabled": true,
         "conditions": {
           "projectTypes": ["adk"],
           "maxFileSize": "50KB"
         }
       }
     }
   }
   ```

### Agent Errors and Exceptions

**Symptoms:**
- Python exceptions in agent logs
- Partial agent responses
- Error messages in Kiro

**Common Errors:**

1. **Import Errors:**
   ```bash
   # Ensure virtual environment is activated
   source .venv/bin/activate
   
   # Install missing dependencies
   pip install -r requirements.txt
   ```

2. **Configuration Errors:**
   ```bash
   # Validate configuration schema
   python .kiro/agents/validate_config.py --verbose
   ```

3. **MCP Communication Errors:**
   ```bash
   # Test MCP connectivity
   python test-mcp-server.py --verbose
   ```

### Agent Coordination Issues

**Symptoms:**
- Conflicting recommendations
- Multiple agents running simultaneously
- Inconsistent advice

**Solutions:**

1. **Configure coordination:**
   ```json
   {
     "coordination": {
       "conflictResolution": {
         "strategy": "priority-based",
         "allowConcurrent": false
       }
     }
   }
   ```

2. **Set agent priorities:**
   ```json
   {
     "agents": {
       "adk-code-review": {
         "priority": "high"
       },
       "adk-architecture": {
         "priority": "medium"
       }
     }
   }
   ```

## Hook Issues

### Hooks Not Triggering

**Symptoms:**
- File saves don't trigger agents
- Manual triggers don't work
- No hook activity in logs

**Diagnosis:**
```bash
# Check hook files exist
ls -la .kiro/hooks/adk-*.kiro.hook

# Verify hook syntax
python -c "
import json
with open('.kiro/hooks/adk-code-review.kiro.hook') as f:
    config = json.load(f)
    print('Hook config valid')
"
```

**Solutions:**

1. **Verify hook registration:**
   Ensure hook files are in the correct location with proper naming

2. **Check file patterns:**
   ```json
   {
     "when": {
       "type": "fileEdited",
       "patterns": ["*.rs", "src/**/*.rs"]
     }
   }
   ```

3. **Verify project detection:**
   ```json
   {
     "conditions": {
       "projectType": "adk",
       "fileSize": "< 50KB"
     }
   }
   ```

### Hook Performance Issues

**Symptoms:**
- Hooks triggering too frequently
- UI lag when saving files
- High resource usage

**Solutions:**

1. **Adjust debouncing:**
   ```json
   {
     "hooks": {
       "adk-code-review": {
         "debounceMs": 3000
       }
     }
   }
   ```

2. **Add exclusion patterns:**
   ```json
   {
     "triggers": {
       "excludePatterns": ["target/**", "*.test.rs", "examples/**"]
     }
   }
   ```

3. **Set file size limits:**
   ```json
   {
     "conditions": {
       "maxFileSize": "25KB"
     }
   }
   ```

## Configuration Problems

### Invalid Configuration

**Symptoms:**
- Configuration validation errors
- Agents using default settings
- Schema validation failures

**Diagnosis:**
```bash
# Validate configuration
python .kiro/agents/validate_config.py --detailed

# Check JSON syntax
python -c "
import json
with open('.kiro/settings/adk-agents.json') as f:
    config = json.load(f)
    print('JSON syntax valid')
"
```

**Solutions:**

1. **Fix JSON syntax errors:**
   - Check for missing commas
   - Verify quote marks
   - Ensure proper nesting

2. **Validate against schema:**
   ```bash
   python .kiro/agents/validate_config.py --schema-check
   ```

3. **Reset to defaults:**
   ```bash
   # Backup current config
   cp .kiro/settings/adk-agents.json .kiro/settings/adk-agents.json.backup
   
   # Generate default config
   python .kiro/agents/generate_default_config.py
   ```

### Configuration Migration Issues

**Symptoms:**
- Settings lost after updates
- Deprecated configuration warnings
- Migration failures

**Solutions:**

1. **Manual migration:**
   ```bash
   # Run migration script
   python .kiro/agents/migrate_config.py --from-version 1.0 --to-version 2.0
   ```

2. **Restore from backup:**
   ```bash
   # List available backups
   ls -la .kiro/config-backups/
   
   # Restore specific backup
   cp .kiro/config-backups/adk-agents-2024-01-01.json .kiro/settings/adk-agents.json
   ```

## Performance Issues

### Slow Agent Response

**Symptoms:**
- Long delays before agent responses
- Timeout errors
- High CPU usage

**Diagnosis:**
```bash
# Monitor resource usage
top -p $(pgrep -f "arkaft-mcp-google-adk")

# Check response times
python test-mcp-server.py --benchmark
```

**Solutions:**

1. **Optimize file size limits:**
   ```json
   {
     "triggers": {
       "fileSizeLimit": "25KB"
     }
   }
   ```

2. **Enable caching:**
   ```json
   {
     "caching": {
       "enabled": true,
       "strategies": {
         "mcpResponses": {
           "ttl": 3600
         }
       }
     }
   }
   ```

3. **Adjust concurrency:**
   ```json
   {
     "performance": {
       "rateLimiting": {
         "maxConcurrentAgents": 1,
         "maxRequestsPerMinute": 20
       }
     }
   }
   ```

### Memory Usage Issues

**Symptoms:**
- High memory consumption
- Out of memory errors
- System slowdown

**Solutions:**

1. **Configure memory limits:**
   ```json
   {
     "performance": {
       "resourceLimits": {
         "maxMemoryMB": 512,
         "gcInterval": 300
       }
     }
   }
   ```

2. **Optimize caching:**
   ```json
   {
     "caching": {
       "strategies": {
         "mcpResponses": {
           "maxSize": 50
         }
       }
     }
   }
   ```

## Error Messages

### Common Error Messages and Solutions

#### "MCP server 'arkaft-google-adk' not found"

**Cause:** MCP server not configured or disabled

**Solution:**
```json
{
  "mcpServers": {
    "arkaft-google-adk": {
      "command": "./arkaft-mcp-google-adk/target/release/arkaft-mcp-google-adk",
      "disabled": false
    }
  }
}
```

#### "Tool 'review_rust_file' not available"

**Cause:** MCP server not providing expected tools

**Solution:**
1. Rebuild MCP server: `cd arkaft-mcp-google-adk && cargo build --release`
2. Verify tool registration in server code
3. Check auto-approval settings

#### "Agent configuration validation failed"

**Cause:** Invalid configuration format or values

**Solution:**
```bash
# Get detailed validation errors
python .kiro/agents/validate_config.py --verbose --section agents
```

#### "Project not detected as ADK project"

**Cause:** Project doesn't meet ADK detection criteria

**Solution:**
1. Ensure `Cargo.toml` contains ADK dependencies
2. Check project structure matches ADK patterns
3. Add explicit ADK markers if needed

#### "Circuit breaker open - MCP server unavailable"

**Cause:** MCP server has failed multiple times

**Solution:**
1. Check MCP server status
2. Wait for circuit breaker recovery (default: 60 seconds)
3. Manually reset: `python .kiro/agents/reset_circuit_breaker.py`

#### "File too large for analysis"

**Cause:** File exceeds configured size limit

**Solution:**
```json
{
  "triggers": {
    "fileSizeLimit": "100KB"
  }
}
```

## Getting Help

### Log Files

Check log files for detailed error information:
- Agent logs: `.kiro/logs/agents/`
- MCP server logs: Check server output
- Hook logs: `.kiro/logs/hooks/`

### Debug Mode

Enable debug mode for verbose logging:
```json
{
  "debug": {
    "enabled": true,
    "logLevel": "DEBUG",
    "logToFile": true
  }
}
```

### Support Resources

1. **Documentation:** Check README.md and USER_GUIDE.md
2. **Examples:** Review configuration examples in `examples/`
3. **Test Scripts:** Use provided test scripts for diagnosis
4. **Configuration Validation:** Use `validate_config.py` for configuration issues

### Reporting Issues

When reporting issues, include:
1. Error messages and stack traces
2. Configuration files (sanitized)
3. Steps to reproduce
4. System information (OS, Python version, Rust version)
5. Output from `./verify-mcp-setup.sh`