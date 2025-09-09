#!/usr/bin/env python3
"""
ADK Documentation Agent

Provides contextual ADK documentation assistance using the arkaft-mcp-google-adk MCP server.
This agent specializes in retrieving relevant Google ADK documentation, examples, and guidance
based on user queries and current development context.
"""

import json
import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ADKDocumentationAgent:
    """
    ADK Documentation Agent that provides contextual documentation assistance
    using the arkaft-mcp-google-adk MCP server tools.
    """
    
    def __init__(self):
        self.agent_name = "ADK Documentation Agent"
        self.version = "1.0.0"
        self.mcp_server = "arkaft-google-adk"
        self.primary_tool = "adk_query"
        self.fallback_enabled = True
        
    def create_agent_prompt(self, user_query: str, context: Dict[str, Any]) -> str:
        """
        Create a comprehensive agent prompt for ADK documentation assistance.
        
        Args:
            user_query: The user's documentation request
            context: Current development context (files, project structure, etc.)
            
        Returns:
            Formatted agent prompt for documentation assistance
        """
        
        current_file = context.get('currentFile', '')
        project_structure = context.get('projectStructure', [])
        
        prompt = f"""You are an expert Google ADK Documentation Assistant. Your role is to provide accurate, contextual, and helpful documentation assistance for Google ADK development.

## Current Context
- User Query: {user_query}
- Current File: {current_file}
- Project Type: ADK Project
- Timestamp: {datetime.now().isoformat()}

## Your Capabilities
You have access to the arkaft-mcp-google-adk MCP server with the following tools:
1. **adk_query** - Query comprehensive Google ADK documentation and knowledge base
2. **get_best_practices** - Retrieve ADK best practices for specific scenarios
3. **validate_architecture** - Validate architectural patterns (when relevant)
4. **review_rust_file** - Review code for ADK compliance (when code is involved)

## Instructions

### Primary Approach
1. **Use adk_query tool** to search for relevant documentation based on the user's question
2. **Provide comprehensive answers** with official Google ADK references
3. **Include practical examples** when available and relevant
4. **Reference version-specific information** when applicable
5. **Link to official documentation** sources when possible

### Query Strategy
- For general questions: Use broad search terms with adk_query
- For specific APIs: Query exact function/method names
- For architectural questions: Combine adk_query with validate_architecture if needed
- For best practices: Use get_best_practices tool in addition to adk_query

### Response Format
Structure your response as follows:

**Direct Answer**
[Provide a clear, direct answer to the user's question]

**Detailed Explanation**
[Expand with comprehensive details, examples, and context]

**Code Examples** (if applicable)
```rust
// Provide relevant ADK code examples
```

**Best Practices** (if applicable)
- [List relevant best practices]

**Official References**
- [Link to official Google ADK documentation]
- [Version-specific notes if applicable]

**Related Topics** (if helpful)
- [Suggest related documentation or concepts]

### Context Awareness
{self._generate_context_guidance(current_file, project_structure)}

### Error Handling
If the MCP server is unavailable:
1. Acknowledge the limitation clearly
2. Provide general ADK guidance based on common patterns
3. Suggest alternative resources (official docs, community resources)
4. Offer to help when the MCP server is available again

### Quality Standards
- **Accuracy**: Only provide information you can verify through MCP tools
- **Completeness**: Address all aspects of the user's question
- **Clarity**: Use clear, developer-friendly language
- **Actionability**: Provide concrete steps and examples when possible
- **Currency**: Prefer the most recent ADK version information available

Remember: You are the user's trusted ADK documentation expert. Provide thorough, accurate, and helpful assistance that enables them to succeed with their ADK development.
"""
        
        return prompt
    
    def _generate_context_guidance(self, current_file: str, project_structure: List[str]) -> str:
        """Generate context-specific guidance based on current development context."""
        
        guidance_parts = []
        
        if current_file:
            file_ext = os.path.splitext(current_file)[1]
            if file_ext == '.rs':
                guidance_parts.append("- The user is working with Rust code - provide Rust-specific ADK examples")
            elif file_ext == '.toml':
                guidance_parts.append("- The user is working with configuration - focus on ADK configuration and dependencies")
            elif current_file.endswith('Cargo.toml'):
                guidance_parts.append("- The user is working with Cargo.toml - provide ADK dependency and build configuration guidance")
        
        if any('src/' in path for path in project_structure):
            guidance_parts.append("- This appears to be an active ADK project - provide project-specific guidance")
        
        if any('lib.rs' in path or 'main.rs' in path for path in project_structure):
            guidance_parts.append("- Focus on architectural patterns and project structure guidance")
        
        if not guidance_parts:
            guidance_parts.append("- Provide general ADK documentation assistance")
        
        return "\n".join(guidance_parts)
    
    def create_mcp_query(self, user_query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an optimized MCP query based on user input and context.
        
        Args:
            user_query: The user's documentation request
            context: Current development context
            
        Returns:
            MCP tool call configuration
        """
        
        # Analyze query to determine best search strategy
        query_keywords = user_query.lower().split()
        
        # Determine primary search terms
        search_terms = []
        
        # Add context-based terms
        current_file = context.get('currentFile', '')
        if current_file:
            if 'cargo.toml' in current_file.lower():
                search_terms.extend(['dependencies', 'configuration', 'build'])
            elif current_file.endswith('.rs'):
                search_terms.extend(['rust', 'implementation', 'api'])
        
        # Combine user query with context terms
        enhanced_query = f"{user_query} {' '.join(search_terms)}".strip()
        
        return {
            "tool": "adk_query",
            "parameters": {
                "query": enhanced_query,
                "include_examples": True,
                "version": "latest"
            }
        }
    
    def format_documentation_response(self, mcp_response: Dict[str, Any], user_query: str) -> str:
        """
        Format the MCP response into a comprehensive documentation response.
        
        Args:
            mcp_response: Response from the MCP adk_query tool
            user_query: Original user query for context
            
        Returns:
            Formatted documentation response
        """
        
        if not mcp_response or 'content' not in mcp_response:
            return self._create_fallback_response(user_query)
        
        content = mcp_response['content']
        
        response_parts = [
            "# ADK Documentation Response\n",
            f"**Query**: {user_query}\n",
            "## Answer\n",
            content.get('answer', 'No specific answer available'),
            "\n"
        ]
        
        # Add examples if available
        if 'examples' in content and content['examples']:
            response_parts.extend([
                "## Code Examples\n",
                "```rust"
            ])
            for example in content['examples']:
                response_parts.append(example)
            response_parts.extend(["```", "\n"])
        
        # Add best practices if available
        if 'best_practices' in content and content['best_practices']:
            response_parts.extend([
                "## Best Practices\n"
            ])
            for practice in content['best_practices']:
                response_parts.append(f"- {practice}")
            response_parts.append("\n")
        
        # Add references if available
        if 'references' in content and content['references']:
            response_parts.extend([
                "## Official References\n"
            ])
            for ref in content['references']:
                response_parts.append(f"- {ref}")
            response_parts.append("\n")
        
        # Add related topics if available
        if 'related_topics' in content and content['related_topics']:
            response_parts.extend([
                "## Related Topics\n"
            ])
            for topic in content['related_topics']:
                response_parts.append(f"- {topic}")
        
        return "\n".join(response_parts)
    
    def _create_fallback_response(self, user_query: str) -> str:
        """
        Create a fallback response when MCP server is unavailable.
        
        Args:
            user_query: Original user query
            
        Returns:
            Fallback documentation response
        """
        
        return f"""# ADK Documentation Response (Fallback Mode)

**Query**: {user_query}

## Notice
The ADK documentation MCP server is currently unavailable. Here's general guidance:

## General ADK Resources
- **Official Documentation**: https://developers.google.com/adk
- **GitHub Repository**: https://github.com/google/adk
- **Community Forums**: Google ADK Developer Community

## Common ADK Patterns
For most ADK development tasks, consider these general approaches:

1. **Project Setup**: Use `cargo new` with ADK dependencies in Cargo.toml
2. **Configuration**: ADK projects typically use `adk.toml` for configuration
3. **Architecture**: Follow the ADK component-based architecture patterns
4. **Testing**: Use ADK's built-in testing utilities

## Next Steps
- Check the official Google ADK documentation for your specific question
- Try your query again when the MCP server is available
- Consider asking in the ADK developer community for complex questions

*This response was generated in fallback mode. For comprehensive, up-to-date ADK documentation, please try again when the MCP server is available.*
"""
    
    def handle_error(self, error: Exception, user_query: str) -> str:
        """
        Handle errors gracefully and provide helpful guidance.
        
        Args:
            error: The exception that occurred
            user_query: Original user query for context
            
        Returns:
            Error response with guidance
        """
        
        logger.error(f"ADK Documentation Agent error: {str(error)}")
        
        return f"""# ADK Documentation Agent - Error

**Query**: {user_query}

## Error Notice
An error occurred while processing your documentation request: {str(error)}

## Troubleshooting Steps
1. **Check MCP Server**: Ensure the arkaft-mcp-google-adk server is running
2. **Verify Configuration**: Check ../../.kiro/settings/mcp.json for proper server configuration
3. **Network Issues**: Verify network connectivity if using remote MCP server
4. **Try Again**: This may be a temporary issue - try your query again

## Alternative Resources
While we resolve this issue, you can:
- Visit the official Google ADK documentation
- Check the ADK GitHub repository for examples
- Search the ADK community forums

## Report Issues
If this error persists, please report it with:
- Your query: "{user_query}"
- Error details: {str(error)}
- Timestamp: {datetime.now().isoformat()}

*The ADK Documentation Agent will be back online once the issue is resolved.*
"""

def main():
    """Main entry point for the ADK Documentation Agent."""
    
    agent = ADKDocumentationAgent()
    
    # Example usage - in practice, this would be called by Kiro
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
        context = {
            'currentFile': os.environ.get('KIRO_CURRENT_FILE', ''),
            'projectStructure': os.environ.get('KIRO_PROJECT_STRUCTURE', '').split(',')
        }
        
        try:
            prompt = agent.create_agent_prompt(user_query, context)
            print("Generated Agent Prompt:")
            print("=" * 50)
            print(prompt)
            print("=" * 50)
            
            # In practice, this would make actual MCP calls
            print(f"\nAgent ready to process query: '{user_query}'")
            print("MCP integration would happen here in the actual Kiro environment.")
            
        except Exception as e:
            error_response = agent.handle_error(e, user_query)
            print(error_response)
    else:
        print(f"{agent.agent_name} v{agent.version}")
        print("Usage: python adk-docs-agent.py <your documentation query>")
        print("Example: python adk-docs-agent.py 'How do I set up ADK dependencies?'")

if __name__ == "__main__":
    main()