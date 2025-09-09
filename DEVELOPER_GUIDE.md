# ADK Agents Developer Guide

This guide covers how to extend the ADK Agents system, create custom agents, and contribute to the framework.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Creating Custom Agents](#creating-custom-agents)
- [Extending MCP Integration](#extending-mcp-integration)
- [Custom Hook Development](#custom-hook-development)
- [Testing Framework](#testing-framework)
- [Contributing Guidelines](#contributing-guidelines)

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        ADK Agents System                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │    Hooks    │  │   Agents    │  │    MCP Integration      │  │
│  │             │  │             │  │                         │  │
│  │ - File      │  │ - Base      │  │ - Client Wrapper        │  │
│  │   Triggers  │  │   Agent     │  │ - Error Handling        │  │
│  │ - Manual    │  │ - Specific  │  │ - Tool Management       │  │
│  │   Triggers  │  │   Agents    │  │ - Health Monitoring     │  │
│  │ - Conditions│  │ - Coord.    │  │                         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Config Mgmt │  │ Error Hdlg  │  │    Coordination         │  │
│  │             │  │             │  │                         │  │
│  │ - Schema    │  │ - Circuit   │  │ - Context Sharing       │  │
│  │   Validation│  │   Breaker   │  │ - Conflict Resolution   │  │
│  │ - Migration │  │ - Retry     │  │ - Priority Management   │  │
│  │ - Defaults  │  │   Logic     │  │ - Message Consistency   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Core Classes

#### BaseADKAgent

The foundation class for all agents:

```python
from .base_agent import BaseADKAgent
from typing import Dict, Any, Optional

class BaseADKAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mcp_client = MCPClientWrapper(config.get('mcpServer'))
        self.error_handler = MCPErrorHandler()
        self.context_manager = SharedContextManager()
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution method - override in subclasses"""
        raise NotImplementedError
    
    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Error handling with fallback responses"""
        return await self.error_handler.handle_error(error, context, self.get_fallback_response)
    
    def get_fallback_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback response when MCP is unavailable"""
        raise NotImplementedError
```

#### MCPClientWrapper

Handles MCP server communication:

```python
class MCPClientWrapper:
    def __init__(self, server_name: str):
        self.server_name = server_name
        self.circuit_breaker = CircuitBreaker()
        self.retry_handler = RetryHandler()
        self.health_checker = HealthChecker()
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool with error handling and retry logic"""
        if not await self.health_checker.is_healthy():
            raise MCPServerUnavailableError()
        
        return await self.circuit_breaker.call(
            self._make_tool_call, tool_name, arguments
        )
```

## Creating Custom Agents

### Basic Agent Structure

1. **Create the agent class:**

```python
# .kiro/agents/custom_adk_agent.py
from .base_agent import BaseADKAgent
from typing import Dict, Any

class CustomADKAgent(BaseADKAgent):
    """Custom agent for specific ADK development tasks"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "custom-adk-agent"
        self.description = "Custom agent for specialized ADK tasks"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution logic"""
        try:
            # Get file content from context
            file_content = context.get('file_content', '')
            file_path = context.get('file_path', '')
            
            # Use MCP tools for analysis
            analysis_result = await self.mcp_client.call_tool(
                'review_rust_file',
                {'file_content': file_content, 'file_path': file_path}
            )
            
            # Process results
            recommendations = self._process_analysis(analysis_result)
            
            # Update shared context
            await self.context_manager.update_context(
                file_path, 
                {'agent': self.agent_name, 'recommendations': recommendations}
            )
            
            return {
                'success': True,
                'recommendations': recommendations,
                'agent': self.agent_name
            }
            
        except Exception as e:
            return await self.handle_error(e, context)
    
    def _process_analysis(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process MCP tool results into actionable recommendations"""
        # Custom processing logic here
        return []
    
    def get_fallback_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback when MCP server is unavailable"""
        return {
            'success': False,
            'message': 'MCP server unavailable - using fallback guidance',
            'fallback_recommendations': [
                {
                    'type': 'general',
                    'message': 'Review code manually for ADK compliance',
                    'priority': 'medium'
                }
            ]
        }
```

2. **Add configuration:**

```json
{
  "agents": {
    "custom-adk-agent": {
      "enabled": true,
      "mcpServer": "arkaft-google-adk",
      "customSettings": {
        "analysisDepth": "detailed",
        "includeExamples": true
      }
    }
  }
}
```

3. **Create test file:**

```python
# .kiro/agents/test_custom_adk_agent.py
import asyncio
import json
from custom_adk_agent import CustomADKAgent

async def test_custom_agent():
    """Test custom agent functionality"""
    config = {
        'mcpServer': 'arkaft-google-adk',
        'customSettings': {
            'analysisDepth': 'detailed'
        }
    }
    
    agent = CustomADKAgent(config)
    
    test_context = {
        'file_content': 'fn main() { println!("Hello, ADK!"); }',
        'file_path': 'src/main.rs'
    }
    
    result = await agent.execute(test_context)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(test_custom_agent())
```

### Advanced Agent Features

#### Multi-Tool Integration

```python
class AdvancedADKAgent(BaseADKAgent):
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use multiple MCP tools for comprehensive analysis"""
        
        # Step 1: Get best practices
        best_practices = await self.mcp_client.call_tool(
            'get_best_practices',
            {'category': 'architecture', 'context': context.get('project_type')}
        )
        
        # Step 2: Review code
        code_review = await self.mcp_client.call_tool(
            'review_rust_file',
            {'file_content': context['file_content']}
        )
        
        # Step 3: Validate architecture
        arch_validation = await self.mcp_client.call_tool(
            'validate_architecture',
            {'project_structure': context.get('project_structure')}
        )
        
        # Step 4: Query documentation if needed
        if self._needs_documentation(code_review):
            docs = await self.mcp_client.call_tool(
                'adk_query',
                {'query': self._generate_doc_query(code_review)}
            )
        
        # Combine results
        return self._combine_results(best_practices, code_review, arch_validation, docs)
```

#### Context-Aware Processing

```python
class ContextAwareAgent(BaseADKAgent):
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process based on current development context"""
        
        # Analyze current context
        project_context = await self._analyze_project_context(context)
        
        # Adjust analysis based on context
        if project_context['is_new_project']:
            return await self._handle_new_project(context)
        elif project_context['is_refactoring']:
            return await self._handle_refactoring(context)
        else:
            return await self._handle_maintenance(context)
    
    async def _analyze_project_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the current development context"""
        # Implementation for context analysis
        pass
```

## Extending MCP Integration

### Adding New MCP Tools

1. **Extend the MCP server** (in Rust):

```rust
// In arkaft-mcp-google-adk/src/server/handlers.rs
pub async fn handle_custom_tool(
    params: CustomToolParams,
) -> Result<CustomToolResult, Box<dyn std::error::Error + Send + Sync>> {
    // Implementation for new tool
    Ok(CustomToolResult {
        analysis: "Custom analysis result".to_string(),
        recommendations: vec!["Custom recommendation".to_string()],
    })
}
```

2. **Update agent to use new tool:**

```python
class ExtendedADKAgent(BaseADKAgent):
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Use the new custom tool
        custom_result = await self.mcp_client.call_tool(
            'custom_tool',
            {'input': context['custom_input']}
        )
        
        return self._process_custom_result(custom_result)
```

### Custom MCP Client Extensions

```python
class ExtendedMCPClient(MCPClientWrapper):
    def __init__(self, server_name: str):
        super().__init__(server_name)
        self.custom_cache = CustomCache()
    
    async def call_tool_with_caching(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced tool calling with custom caching logic"""
        cache_key = self._generate_cache_key(tool_name, arguments)
        
        if cached_result := self.custom_cache.get(cache_key):
            return cached_result
        
        result = await self.call_tool(tool_name, arguments)
        self.custom_cache.set(cache_key, result)
        
        return result
```

## Custom Hook Development

### Creating Custom Hooks

1. **Define hook configuration:**

```json
{
  "enabled": true,
  "name": "Custom ADK Hook",
  "description": "Custom hook for specialized triggers",
  "version": "1",
  "when": {
    "type": "fileEdited",
    "patterns": ["src/custom/**/*.rs"],
    "conditions": {
      "projectType": "adk",
      "customMarker": "// @custom-review"
    }
  },
  "then": {
    "type": "askAgent",
    "agent": "custom-adk-agent",
    "prompt": "Custom analysis prompt for specialized components"
  }
}
```

2. **Advanced hook conditions:**

```json
{
  "when": {
    "type": "composite",
    "conditions": [
      {
        "type": "fileEdited",
        "patterns": ["*.rs"]
      },
      {
        "type": "custom",
        "script": ".kiro/hooks/custom_condition.py",
        "function": "check_custom_condition"
      }
    ],
    "operator": "AND"
  }
}
```

3. **Custom condition script:**

```python
# .kiro/hooks/custom_condition.py
def check_custom_condition(context: Dict[str, Any]) -> bool:
    """Custom condition logic"""
    file_content = context.get('file_content', '')
    
    # Custom logic to determine if hook should trigger
    return '// @custom-review' in file_content and len(file_content) > 1000
```

### Hook Testing

```python
# .kiro/hooks/test_custom_hook.py
import json
from pathlib import Path

def test_hook_configuration():
    """Test hook configuration validity"""
    hook_file = Path('.kiro/hooks/custom-adk-hook.kiro.hook')
    
    with open(hook_file) as f:
        config = json.load(f)
    
    # Validate required fields
    assert 'enabled' in config
    assert 'when' in config
    assert 'then' in config
    
    print("Hook configuration valid")

def test_hook_conditions():
    """Test hook trigger conditions"""
    # Simulate file edit event
    context = {
        'file_path': 'src/custom/test.rs',
        'file_content': '// @custom-review\nfn test() {}'
    }
    
    # Test condition logic
    from custom_condition import check_custom_condition
    assert check_custom_condition(context) == True
    
    print("Hook conditions working correctly")
```

## Testing Framework

### Agent Testing

```python
# .kiro/agents/test_framework.py
import asyncio
import pytest
from unittest.mock import Mock, AsyncMock
from base_agent import BaseADKAgent

class TestADKAgent:
    @pytest.fixture
    def mock_mcp_client(self):
        client = Mock()
        client.call_tool = AsyncMock()
        return client
    
    @pytest.fixture
    def test_agent(self, mock_mcp_client):
        config = {'mcpServer': 'test-server'}
        agent = BaseADKAgent(config)
        agent.mcp_client = mock_mcp_client
        return agent
    
    @pytest.mark.asyncio
    async def test_agent_execution(self, test_agent, mock_mcp_client):
        """Test basic agent execution"""
        mock_mcp_client.call_tool.return_value = {
            'analysis': 'Test analysis',
            'recommendations': ['Test recommendation']
        }
        
        context = {
            'file_content': 'fn main() {}',
            'file_path': 'src/main.rs'
        }
        
        result = await test_agent.execute(context)
        
        assert result['success'] == True
        mock_mcp_client.call_tool.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, test_agent, mock_mcp_client):
        """Test agent error handling"""
        mock_mcp_client.call_tool.side_effect = Exception("MCP Error")
        
        context = {'file_content': 'fn main() {}'}
        result = await test_agent.execute(context)
        
        assert result['success'] == False
        assert 'fallback' in result
```

### Integration Testing

```python
# .kiro/agents/integration_test.py
import asyncio
import tempfile
from pathlib import Path

async def test_end_to_end_workflow():
    """Test complete workflow from hook trigger to agent response"""
    
    # Create temporary ADK project
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        
        # Create Cargo.toml with ADK dependencies
        cargo_toml = project_path / "Cargo.toml"
        cargo_toml.write_text("""
[package]
name = "test-adk-project"
version = "0.1.0"

[dependencies]
google-adk = "0.1.0"
        """)
        
        # Create test Rust file
        src_dir = project_path / "src"
        src_dir.mkdir()
        main_rs = src_dir / "main.rs"
        main_rs.write_text("fn main() { println!('Hello, ADK!'); }")
        
        # Simulate file save event
        context = {
            'file_path': str(main_rs),
            'file_content': main_rs.read_text(),
            'project_path': str(project_path)
        }
        
        # Test agent activation
        from adk_code_review_agent import ADKCodeReviewAgent
        agent = ADKCodeReviewAgent({'mcpServer': 'arkaft-google-adk'})
        
        result = await agent.execute(context)
        
        assert result['success'] == True
        assert 'recommendations' in result
        
        print("End-to-end workflow test passed")
```

### Performance Testing

```python
# .kiro/agents/performance_test.py
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

async def test_agent_performance():
    """Test agent performance under load"""
    
    async def run_agent_test():
        from adk_code_review_agent import ADKCodeReviewAgent
        agent = ADKCodeReviewAgent({'mcpServer': 'arkaft-google-adk'})
        
        context = {
            'file_content': 'fn main() { println!("Hello, ADK!"); }',
            'file_path': 'src/main.rs'
        }
        
        start_time = time.time()
        result = await agent.execute(context)
        end_time = time.time()
        
        return end_time - start_time, result['success']
    
    # Run multiple concurrent tests
    tasks = [run_agent_test() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    
    # Analyze results
    times = [r[0] for r in results]
    successes = [r[1] for r in results]
    
    print(f"Average response time: {sum(times) / len(times):.2f}s")
    print(f"Success rate: {sum(successes) / len(successes) * 100:.1f}%")
    print(f"Max response time: {max(times):.2f}s")
```

## Contributing Guidelines

### Code Standards

1. **Python Code Style:**
   - Follow PEP 8
   - Use type hints
   - Write docstrings for all public methods
   - Use async/await for I/O operations

2. **Error Handling:**
   - Always implement graceful degradation
   - Use circuit breaker pattern for external services
   - Provide meaningful error messages
   - Log errors appropriately

3. **Testing:**
   - Write unit tests for all new functionality
   - Include integration tests for complex features
   - Test error scenarios and edge cases
   - Maintain test coverage above 80%

### Development Workflow

1. **Feature Development:**
   ```bash
   # Create feature branch
   git checkout -b feature/custom-agent
   
   # Implement feature with tests
   # Run tests
   python -m pytest .kiro/agents/test_custom_agent.py
   
   # Validate configuration
   python .kiro/agents/validate_config.py
   
   # Run integration tests
   python .kiro/agents/integration_test.py
   ```

2. **Documentation:**
   - Update README.md for new features
   - Add examples for new functionality
   - Update troubleshooting guide for new error conditions
   - Include configuration examples

3. **Configuration Schema:**
   - Update JSON schemas for new configuration options
   - Provide migration scripts for breaking changes
   - Test configuration validation

### Submission Guidelines

1. **Pull Request Requirements:**
   - All tests passing
   - Documentation updated
   - Configuration validated
   - Performance impact assessed

2. **Code Review Checklist:**
   - Error handling implemented
   - Tests cover edge cases
   - Documentation is clear
   - Performance is acceptable
   - Security considerations addressed

### Extension Examples

See the `examples/` directory for complete examples:
- `custom-agent-example/`: Complete custom agent implementation
- `advanced-hook-example/`: Advanced hook with custom conditions
- `mcp-extension-example/`: Example of extending MCP integration
- `testing-example/`: Comprehensive testing setup