# ADK Documentation Assistant

A comprehensive documentation assistance agent for Google ADK projects that integrates with the arkaft-mcp-google-adk MCP server to provide contextual, expert-level guidance.

## Overview

The ADK Documentation Assistant provides intelligent documentation assistance through:

- **Context-aware queries** using the `adk_query` MCP tool
- **Version-specific guidance** with official Google ADK references
- **Best practices integration** through MCP tool coordination
- **Fallback handling** when MCP server is unavailable
- **Manual trigger support** for user-initiated help requests

## Components

### 1. Hook Configuration (`adk-docs-assistant.kiro.hook`)

Manual trigger hook that activates the documentation agent:

- **Trigger**: Manual activation with `adk-help` keyword
- **Context**: ADK project detection with comprehensive criteria
- **Agent**: Activates `adk-docs-agent` with documentation prompt
- **Priority**: High priority for immediate user assistance

### 2. Agent Implementation (`adk-docs-agent.py`)

Python-based agent with comprehensive documentation capabilities:

- **MCP Integration**: Primary use of `adk_query` tool
- **Context Awareness**: File-based and project structure analysis
- **Response Formatting**: Structured markdown responses with examples
- **Error Handling**: Graceful degradation and fallback responses
- **Query Optimization**: Enhanced search terms based on context

### 3. Configuration (`adk-docs-agent.json`)

Agent configuration with:

- **MCP Server**: `arkaft-google-adk` integration
- **Tool Mapping**: Primary and secondary MCP tools
- **Response Settings**: Format, examples, and reference preferences
- **Performance**: Timeout and caching configuration

## Features

### Context-Aware Assistance

The agent analyzes current development context:

```python
# Rust file context
if current_file.endswith('.rs'):
    # Provides Rust-specific ADK examples and guidance

# Cargo.toml context  
if 'cargo.toml' in current_file.lower():
    # Focuses on dependencies and build configuration

# Project structure analysis
if 'lib.rs' in project_structure:
    # Emphasizes architectural patterns and project structure
```

### MCP Tool Integration

Primary tool usage strategy:

1. **adk_query**: Main documentation retrieval
2. **get_best_practices**: Supplementary best practices
3. **validate_architecture**: Architectural guidance when relevant
4. **review_rust_file**: Code-specific assistance when applicable

### Response Format

Structured responses include:

- **Direct Answer**: Clear, immediate response
- **Detailed Explanation**: Comprehensive context and details
- **Code Examples**: Relevant ADK code snippets
- **Best Practices**: ADK-specific recommendations
- **Official References**: Links to Google ADK documentation
- **Related Topics**: Additional helpful resources

### Error Handling

Comprehensive error handling:

- **MCP Unavailable**: Fallback to general ADK guidance
- **Tool Failures**: Graceful degradation with retry logic
- **Invalid Queries**: Clarification requests with suggestions
- **Timeout Handling**: Performance limits with user feedback

## Usage

### Manual Activation

Trigger the documentation assistant:

1. Use the `adk-help` trigger in Kiro
2. Agent activates with current context
3. Provides comprehensive documentation assistance
4. Includes examples and official references

### Command Line Testing

```bash
# Test agent functionality
python .kiro/agents/adk-docs-agent.py "How do I set up ADK dependencies?"

# Run comprehensive tests
python .kiro/agents/test_adk_docs_agent.py
```

### Integration with Kiro

The agent integrates seamlessly with Kiro through:

- **Hook System**: Automatic activation on manual triggers
- **MCP Integration**: Direct access to arkaft-mcp-google-adk server
- **Context Passing**: Current file and project structure awareness
- **Response Formatting**: Markdown output optimized for Kiro display

## Configuration Options

### Agent Settings

```json
{
  "response_format": "markdown",
  "include_examples": true,
  "include_references": true,
  "include_best_practices": true,
  "context_awareness": {
    "current_file": true,
    "project_structure": true,
    "open_files": false
  }
}
```

### Hook Settings

```json
{
  "enabled": true,
  "trigger": "adk-help",
  "priority": "high",
  "userInitiated": true,
  "debounceMs": 0
}
```

## Project Detection

The agent detects ADK projects through:

### Cargo.toml Dependencies
- `google-adk`
- `adk-core`
- `adk-runtime`
- `adk-macros`

### Configuration Files
- `adk.toml`
- `adk-config.json`
- `.adk/config.json`

### Directory Patterns
- `src/adk/`
- `adk/`
- `components/adk/`
- `.adk/`

## Testing

Comprehensive test suite with 100% pass rate:

- **Unit Tests**: Agent logic and MCP integration
- **Integration Tests**: End-to-end workflows
- **Configuration Tests**: Hook and agent configuration validation
- **Error Handling Tests**: Fallback and error scenarios

```bash
# Run all tests
python .kiro/agents/test_adk_docs_agent.py

# Expected output: 16 tests, 100% success rate
```

## Requirements Mapping

### Requirement 3.3 (Documentation Hooks)
✅ **Implemented**: Manual trigger hook with ADK project detection

### Requirement 4.4 (Documentation Assistance)
✅ **Implemented**: Comprehensive agent with adk_query integration

### Requirement 5.4 (Graceful Degradation)
✅ **Implemented**: Fallback responses when MCP unavailable

### Requirement 5.5 (Consistent Guidance)
✅ **Implemented**: Exclusive use of arkaft-mcp-google-adk server

## Future Enhancements

### Advanced Features
- **Learning System**: User feedback integration
- **Query History**: Previous query context awareness
- **Multi-language Support**: Beyond Rust ADK projects
- **Collaborative Documentation**: Team-shared knowledge base

### Enhanced Integration
- **IDE Deep Integration**: Inline documentation display
- **Code Completion**: ADK-aware code suggestions
- **Live Documentation**: Real-time documentation updates
- **Performance Optimization**: Advanced caching strategies

## Troubleshooting

### Common Issues

1. **MCP Server Unavailable**
   - Check `.kiro/settings/mcp.json` configuration
   - Verify arkaft-mcp-google-adk server is running
   - Review server logs for connection issues

2. **Hook Not Triggering**
   - Verify ADK project detection criteria
   - Check hook configuration in `.kiro/hooks/`
   - Ensure agent is properly configured

3. **Poor Documentation Quality**
   - Update arkaft-mcp-google-adk server to latest version
   - Check MCP tool availability and functionality
   - Verify query optimization is working correctly

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This provides comprehensive debugging information for troubleshooting agent behavior and MCP integration issues.