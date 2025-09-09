#!/usr/bin/env python3
"""
Test Suite for ADK Documentation Agent

Comprehensive tests for the ADK Documentation Agent functionality,
including MCP integration, context awareness, and error handling.
"""

import unittest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add the agent to the path for testing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import the renamed module
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))
    import adk_docs_agent
    from adk_docs_agent import *
    ADKDocumentationAgent = adk_docs_agent.ADKDocumentationAgent
except ImportError as e:
    print(f"Error importing ADK Documentation Agent: {e}")
    print("Make sure adk-docs-agent.py is in the same directory as this test file.")
    sys.exit(1)

class TestADKDocumentationAgent(unittest.TestCase):
    """Test cases for the ADK Documentation Agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = ADKDocumentationAgent()
        self.sample_context = {
            'currentFile': 'src/main.rs',
            'projectStructure': ['src/', 'Cargo.toml', 'src/lib.rs', 'src/main.rs']
        }
    
    def test_agent_initialization(self):
        """Test agent initialization and basic properties."""
        self.assertEqual(self.agent.agent_name, "ADK Documentation Agent")
        self.assertEqual(self.agent.version, "1.0.0")
        self.assertEqual(self.agent.mcp_server, "arkaft-google-adk")
        self.assertEqual(self.agent.primary_tool, "adk_query")
        self.assertTrue(self.agent.fallback_enabled)
    
    def test_create_agent_prompt_basic(self):
        """Test basic agent prompt creation."""
        user_query = "How do I set up ADK dependencies?"
        prompt = self.agent.create_agent_prompt(user_query, self.sample_context)
        
        self.assertIn("ADK Documentation Assistant", prompt)
        self.assertIn(user_query, prompt)
        self.assertIn("src/main.rs", prompt)
        self.assertIn("adk_query", prompt)
        self.assertIn("arkaft-mcp-google-adk", prompt)
    
    def test_create_agent_prompt_with_rust_context(self):
        """Test agent prompt creation with Rust file context."""
        user_query = "How do I implement ADK components?"
        context = {
            'currentFile': 'src/components.rs',
            'projectStructure': ['src/', 'src/components.rs']
        }
        
        prompt = self.agent.create_agent_prompt(user_query, context)
        
        self.assertIn("Rust-specific ADK examples", prompt)
        self.assertIn("src/components.rs", prompt)
    
    def test_create_agent_prompt_with_cargo_context(self):
        """Test agent prompt creation with Cargo.toml context."""
        user_query = "What ADK dependencies should I add?"
        context = {
            'currentFile': 'Cargo.toml',
            'projectStructure': ['Cargo.toml', 'src/']
        }
        
        prompt = self.agent.create_agent_prompt(user_query, context)
        
        self.assertIn("ADK configuration and dependencies", prompt)
        self.assertIn("Cargo.toml", prompt)
    
    def test_generate_context_guidance(self):
        """Test context guidance generation."""
        # Test with Rust file
        guidance = self.agent._generate_context_guidance('src/main.rs', ['src/'])
        self.assertIn("Rust-specific ADK examples", guidance)
        
        # Test with Cargo.toml
        guidance = self.agent._generate_context_guidance('Cargo.toml', ['Cargo.toml'])
        self.assertIn("ADK configuration and dependencies", guidance)
        
        # Test with lib.rs in structure
        guidance = self.agent._generate_context_guidance('', ['src/lib.rs'])
        self.assertIn("architectural patterns", guidance)
    
    def test_create_mcp_query_basic(self):
        """Test MCP query creation."""
        user_query = "How do I create ADK components?"
        mcp_query = self.agent.create_mcp_query(user_query, self.sample_context)
        
        self.assertEqual(mcp_query['tool'], 'adk_query')
        self.assertIn('query', mcp_query['parameters'])
        self.assertIn(user_query, mcp_query['parameters']['query'])
        self.assertTrue(mcp_query['parameters']['include_examples'])
        self.assertEqual(mcp_query['parameters']['version'], 'latest')
    
    def test_create_mcp_query_with_cargo_context(self):
        """Test MCP query creation with Cargo.toml context."""
        user_query = "ADK setup help"
        context = {
            'currentFile': 'Cargo.toml',
            'projectStructure': ['Cargo.toml']
        }
        
        mcp_query = self.agent.create_mcp_query(user_query, context)
        query_text = mcp_query['parameters']['query']
        
        self.assertIn('dependencies', query_text)
        self.assertIn('configuration', query_text)
        self.assertIn('build', query_text)
    
    def test_format_documentation_response_complete(self):
        """Test documentation response formatting with complete MCP response."""
        user_query = "How do I use ADK components?"
        mcp_response = {
            'content': {
                'answer': 'ADK components are created using the Component trait...',
                'examples': [
                    'struct MyComponent;\nimpl Component for MyComponent { ... }'
                ],
                'best_practices': [
                    'Always implement proper error handling',
                    'Use dependency injection patterns'
                ],
                'references': [
                    'https://developers.google.com/adk/components',
                    'ADK Component Guide v2.1'
                ],
                'related_topics': [
                    'ADK Lifecycle Management',
                    'Component Testing'
                ]
            }
        }
        
        response = self.agent.format_documentation_response(mcp_response, user_query)
        
        self.assertIn("ADK Documentation Response", response)
        self.assertIn(user_query, response)
        self.assertIn("ADK components are created", response)
        self.assertIn("```rust", response)
        self.assertIn("MyComponent", response)
        self.assertIn("Best Practices", response)
        self.assertIn("Official References", response)
        self.assertIn("Related Topics", response)
    
    def test_format_documentation_response_minimal(self):
        """Test documentation response formatting with minimal MCP response."""
        user_query = "Simple ADK question"
        mcp_response = {
            'content': {
                'answer': 'Simple answer here'
            }
        }
        
        response = self.agent.format_documentation_response(mcp_response, user_query)
        
        self.assertIn("Simple answer here", response)
        self.assertIn(user_query, response)
    
    def test_format_documentation_response_empty(self):
        """Test documentation response formatting with empty MCP response."""
        user_query = "Test query"
        mcp_response = {}
        
        response = self.agent.format_documentation_response(mcp_response, user_query)
        
        # Should fall back to fallback response
        self.assertIn("Fallback Mode", response)
        self.assertIn("MCP server is currently unavailable", response)
    
    def test_create_fallback_response(self):
        """Test fallback response creation."""
        user_query = "How do I use ADK?"
        fallback = self.agent._create_fallback_response(user_query)
        
        self.assertIn("Fallback Mode", fallback)
        self.assertIn(user_query, fallback)
        self.assertIn("MCP server is currently unavailable", fallback)
        self.assertIn("Official Documentation", fallback)
        self.assertIn("developers.google.com/adk", fallback)
        self.assertIn("Common ADK Patterns", fallback)
    
    def test_handle_error(self):
        """Test error handling."""
        user_query = "Test query"
        test_error = Exception("Test error message")
        
        error_response = self.agent.handle_error(test_error, user_query)
        
        self.assertIn("Error Notice", error_response)
        self.assertIn("Test error message", error_response)
        self.assertIn(user_query, error_response)
        self.assertIn("Troubleshooting Steps", error_response)
        self.assertIn("arkaft-mcp-google-adk", error_response)
        self.assertIn("Alternative Resources", error_response)

class TestADKDocumentationAgentIntegration(unittest.TestCase):
    """Integration tests for the ADK Documentation Agent."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.agent = ADKDocumentationAgent()
    
    @patch('sys.argv', ['adk-docs-agent.py', 'How', 'do', 'I', 'use', 'ADK?'])
    @patch.dict(os.environ, {
        'KIRO_CURRENT_FILE': 'src/main.rs',
        'KIRO_PROJECT_STRUCTURE': 'src/,Cargo.toml,src/lib.rs'
    })
    def test_main_with_arguments(self):
        """Test main function with command line arguments."""
        with patch('builtins.print') as mock_print:
            # Import and run main
            main = adk_docs_agent.main
            main()
            
            # Check that output was generated
            mock_print.assert_called()
            call_args = [call[0][0] for call in mock_print.call_args_list]
            output = '\n'.join(call_args)
            
            self.assertIn("Generated Agent Prompt", output)
            self.assertIn("How do I use ADK", output)
    
    @patch('sys.argv', ['adk-docs-agent.py'])
    def test_main_without_arguments(self):
        """Test main function without arguments (usage message)."""
        with patch('builtins.print') as mock_print:
            main = adk_docs_agent.main
            main()
            
            call_args = [call[0][0] for call in mock_print.call_args_list]
            output = '\n'.join(call_args)
            
            self.assertIn("ADK Documentation Agent", output)
            self.assertIn("Usage:", output)
            self.assertIn("Example:", output)

class TestADKDocumentationAgentConfiguration(unittest.TestCase):
    """Test configuration file validation."""
    
    def test_agent_configuration_file_exists(self):
        """Test that the agent configuration file exists and is valid."""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'adk_docs_agent.json')
        
        # Check if running from test directory
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.dirname(__file__), 'adk_docs_agent.json')
        
        self.assertTrue(os.path.exists(config_path), 
                       f"Configuration file not found at {config_path}")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Validate required configuration fields
        self.assertIn('name', config)
        self.assertIn('version', config)
        self.assertIn('description', config)
        self.assertIn('mcp_integration', config)
        self.assertIn('capabilities', config)
        
        # Validate MCP integration configuration
        mcp_config = config['mcp_integration']
        self.assertEqual(mcp_config['server'], 'arkaft-google-adk')
        self.assertIn('adk_query', mcp_config['primary_tools'])
        self.assertTrue(mcp_config['fallback_enabled'])

class TestADKDocumentationHookConfiguration(unittest.TestCase):
    """Test hook configuration file validation."""
    
    def test_hook_configuration_file_exists(self):
        """Test that the hook configuration file exists and is valid."""
        hook_path = os.path.join(os.path.dirname(__file__), '..', '..', '.kiro', 'hooks', 'adk-docs-assistant.kiro.hook')
        
        # Check if running from test directory
        if not os.path.exists(hook_path):
            hook_path = os.path.join(os.path.dirname(__file__), 
                                   '../../.kiro/hooks/adk-docs-assistant.kiro.hook')
        
        self.assertTrue(os.path.exists(hook_path), 
                       f"Hook configuration file not found at {hook_path}")
        
        with open(hook_path, 'r') as f:
            hook_config = json.load(f)
        
        # Validate required hook fields
        self.assertTrue(hook_config['enabled'])
        self.assertEqual(hook_config['name'], 'ADK Documentation Assistant')
        self.assertEqual(hook_config['when']['type'], 'manual')
        self.assertEqual(hook_config['when']['trigger'], 'adk-help')
        self.assertEqual(hook_config['then']['agent'], 'adk-docs-agent')
        
        # Validate project detection configuration
        self.assertIn('projectDetection', hook_config)
        project_detection = hook_config['projectDetection']
        self.assertIn('cargoTomlDependencies', project_detection)
        self.assertIn('google-adk', project_detection['cargoTomlDependencies'])

def run_tests():
    """Run all tests with detailed output."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestADKDocumentationAgent,
        TestADKDocumentationAgentIntegration,
        TestADKDocumentationAgentConfiguration,
        TestADKDocumentationHookConfiguration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    print("ADK Documentation Agent Test Suite")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)