# Custom Agent Example

This example demonstrates how to create a custom ADK agent for specialized code analysis tasks.

## Overview

The `CustomSecurityAgent` is designed to perform security-focused analysis of ADK projects, identifying potential security vulnerabilities and suggesting improvements based on ADK security best practices.

## Files

- `custom_security_agent.py`: Main agent implementation
- `security_patterns.json`: Security pattern definitions
- `test_custom_security_agent.py`: Comprehensive test suite
- `custom-security.kiro.hook`: Hook configuration for automatic triggering
- `config-example.json`: Configuration example

## Features

- **Security Pattern Detection**: Identifies common security anti-patterns
- **ADK Security Best Practices**: Leverages MCP tools for ADK-specific security guidance
- **Custom Rule Engine**: Extensible rule system for organization-specific security requirements
- **Integration with Standard Agents**: Coordinates with other ADK agents to avoid conflicts

## Installation

1. Copy the agent files to your `.kiro/agents/` directory:
   ```bash
   cp custom_security_agent.py .kiro/agents/
   cp security_patterns.json .kiro/agents/
   ```

2. Copy the hook configuration:
   ```bash
   cp custom-security.kiro.hook .kiro/hooks/
   ```

3. Update your agent configuration:
   ```bash
   # Merge config-example.json into your .kiro/settings/adk-agents.json
   ```

4. Test the installation:
   ```bash
   python .kiro/agents/test_custom_security_agent.py
   ```

## Usage

### Automatic Triggering

The agent automatically triggers when:
- Rust files containing security-sensitive patterns are saved
- Files in security-critical directories are modified
- Authentication or authorization code is changed

### Manual Triggering

Use the `adk-security` trigger in Kiro to manually activate the agent:
```
adk-security: Please review this code for security issues
```

### Configuration

Customize the agent behavior in your `adk-agents.json`:

```json
{
  "agents": {
    "custom-security": {
      "enabled": true,
      "mcpServer": "arkaft-google-adk",
      "securityRules": {
        "strictMode": true,
        "customPatterns": "security_patterns.json",
        "reportLevel": "detailed"
      }
    }
  }
}
```

## Extending the Agent

### Adding Custom Security Rules

1. Edit `security_patterns.json` to add new patterns:
   ```json
   {
     "patterns": [
       {
         "name": "hardcoded-secrets",
         "pattern": "(password|secret|key)\\s*=\\s*[\"'][^\"']+[\"']",
         "severity": "high",
         "message": "Hardcoded secrets detected"
       }
     ]
   }
   ```

2. Update the agent logic to handle new patterns

### Integration with External Tools

The agent can be extended to integrate with external security tools:

```python
async def integrate_external_scanner(self, file_content: str) -> Dict[str, Any]:
    """Integrate with external security scanning tools"""
    # Implementation for external tool integration
    pass
```

## Testing

Run the comprehensive test suite:

```bash
# Unit tests
python .kiro/agents/test_custom_security_agent.py

# Integration tests
python .kiro/agents/test_security_integration.py

# Performance tests
python .kiro/agents/test_security_performance.py
```

## Best Practices

1. **Security Rule Management**: Keep security patterns up to date
2. **False Positive Handling**: Implement mechanisms to reduce false positives
3. **Performance Optimization**: Use caching for expensive security checks
4. **Coordination**: Ensure proper coordination with other agents
5. **Reporting**: Provide clear, actionable security recommendations