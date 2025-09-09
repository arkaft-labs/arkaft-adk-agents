#!/usr/bin/env python3
"""
Test Suite for ADK Project Assistant Agent

Comprehensive tests for the ADK Project Assistant Agent functionality,
including all assistance types, MCP integration, and error handling.
"""

import unittest
import json
import os
import sys
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime

# Add the agent to the path for testing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))
    from adk_project_assistant_agent import (
        ADKProjectAssistantAgent,
        AssistanceType,
        Priority,
        ProjectSetupGuidance,
        ArchitecturalGuidance,
        CodeExample,
        TroubleshootingGuidance,
        TaskBreakdown,
        ProjectAssistanceResult,
        format_project_assistance_result
    )
except ImportError as e:
    print(f"Error importing ADK Project Assistant Agent: {e}")
    print("Make sure adk_project_assistant_agent.py is in the same directory as this test file.")
    sys.exit(1)


class TestADKProjectAssistantAgent(unittest.TestCase):
    """Test cases for the ADK Project Assistant Agent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_mcp_client = AsyncMock()
        self.agent = ADKProjectAssistantAgent(self.mock_mcp_client)
        self.sample_context = {
            'currentFile': 'src/main.rs',
            'projectStructure': ['src/', 'Cargo.toml', 'src/lib.rs', 'src/main.rs'],
            'projectType': 'adk'
        }
    
    def test_agent_initialization(self):
        """Test agent initialization and basic properties."""
        self.assertEqual(self.agent.mcp_server_name, "arkaft-google-adk")
        self.assertIsNotNone(self.agent.mcp_client)
        self.assertEqual(self.agent.project_context, {})
    
    def test_determine_assistance_type_project_setup(self):
        """Test assistance type determination for project setup."""
        test_cases = [
            ("How do I set up a new ADK project?", AssistanceType.PROJECT_SETUP),
            ("Create a new ADK application", AssistanceType.PROJECT_SETUP), 
            ("Initialize ADK project", AssistanceType.PROJECT_SETUP),
            ("Start new project with ADK", AssistanceType.PROJECT_SETUP)
        ]
        
        for request, expected_type in test_cases:
            assistance_type = self.agent._determine_assistance_type(request, self.sample_context)
            # Debug output to see what's happening
            if assistance_type != expected_type:
                print(f"DEBUG: Request '{request}' returned {assistance_type}, expected {expected_type}")
            self.assertEqual(assistance_type, expected_type, 
                           f"Request '{request}' should return {expected_type}, got {assistance_type}")
    
    def test_determine_assistance_type_architecture(self):
        """Test assistance type determination for architecture guidance."""
        test_cases = [
            "What's the best architecture for my service?",
            "How should I design my components?",
            "ADK architectural patterns",
            "Component organization structure"
        ]
        
        for request in test_cases:
            assistance_type = self.agent._determine_assistance_type(request, self.sample_context)
            self.assertEqual(assistance_type, AssistanceType.ARCHITECTURE_GUIDANCE)
    
    def test_determine_assistance_type_code_examples(self):
        """Test assistance type determination for code examples."""
        test_cases = [
            "Show me how to implement a component",
            "Code example for ADK service",
            "How to implement error handling",
            "Sample ADK application code"
        ]
        
        for request in test_cases:
            assistance_type = self.agent._determine_assistance_type(request, self.sample_context)
            self.assertEqual(assistance_type, AssistanceType.CODE_EXAMPLES)
    
    def test_determine_assistance_type_troubleshooting(self):
        """Test assistance type determination for troubleshooting."""
        test_cases = [
            "My ADK app has an error",
            "Getting issues when running", 
            "Debug compilation problems",
            "Fix runtime errors"
        ]
        
        for request in test_cases:
            assistance_type = self.agent._determine_assistance_type(request, self.sample_context)
            self.assertEqual(assistance_type, AssistanceType.TROUBLESHOOTING)
    
    def test_determine_assistance_type_task_breakdown(self):
        """Test assistance type determination for task breakdown."""
        test_cases = [
            "Break down building a user service",
            "Step-by-step guide for implementation",
            "Plan for creating ADK components",
            "Roadmap for project development"
        ]
        
        for request in test_cases:
            assistance_type = self.agent._determine_assistance_type(request, self.sample_context)
            self.assertEqual(assistance_type, AssistanceType.TASK_BREAKDOWN)
    
    def test_enhance_query_for_type(self):
        """Test query enhancement based on assistance type."""
        user_request = "How do I create components?"
        
        enhanced = self.agent._enhance_query_for_type(user_request, AssistanceType.CODE_EXAMPLES)
        self.assertIn(user_request, enhanced)
        self.assertIn("code examples", enhanced)
        self.assertIn("implementation patterns", enhanced)
    
    def test_determine_best_practices_scenario(self):
        """Test best practices scenario determination."""
        scenarios = {
            AssistanceType.PROJECT_SETUP: "project_initialization",
            AssistanceType.ARCHITECTURE_GUIDANCE: "architectural_design",
            AssistanceType.CODE_EXAMPLES: "implementation_patterns",
            AssistanceType.TROUBLESHOOTING: "error_handling",
            AssistanceType.TASK_BREAKDOWN: "development_process",
            AssistanceType.GENERAL_GUIDANCE: "general_development"
        }
        
        for assistance_type, expected_scenario in scenarios.items():
            scenario = self.agent._determine_best_practices_scenario(assistance_type, "test request")
            self.assertEqual(scenario, expected_scenario)
    
    def test_create_sample_content_for_validation(self):
        """Test sample content creation for validation."""
        user_request = "Test architecture validation"
        content = self.agent._create_sample_content_for_validation(user_request, self.sample_context)
        
        self.assertIn(user_request, content)
        self.assertIn("Component", content)
        self.assertIn("Service", content)
        self.assertIn("adk_core", content)
    
    def test_create_sample_code_for_analysis(self):
        """Test sample code creation for analysis."""
        user_request = "Test code analysis"
        code = self.agent._create_sample_code_for_analysis(user_request, self.sample_context)
        
        self.assertIn(user_request, code)
        self.assertIn("Component", code)
        self.assertIn("initialize", code)
        self.assertIn("Result", code)


class TestADKProjectAssistantAgentAsync(unittest.IsolatedAsyncioTestCase):
    """Async test cases for the ADK Project Assistant Agent."""
    
    async def asyncSetUp(self):
        """Set up async test fixtures."""
        self.mock_mcp_client = AsyncMock()
        self.agent = ADKProjectAssistantAgent(self.mock_mcp_client)
        self.sample_context = {
            'currentFile': 'src/main.rs',
            'projectStructure': ['src/', 'Cargo.toml'],
            'projectType': 'adk'
        }
        
        # Set up mock responses
        self.setup_mock_responses()
    
    def setup_mock_responses(self):
        """Set up mock MCP responses."""
        async def mock_call_tool(server_name, tool_name, arguments):
            if tool_name == "adk_query":
                return {
                    "answer": "ADK components are building blocks...",
                    "examples": [
                        {
                            "title": "Basic Component",
                            "code": "impl Component for MyComponent { ... }",
                            "description": "Simple component",
                            "language": "rust",
                            "explanation": "Basic implementation",
                            "best_practices": ["Use proper error handling"],
                            "related_patterns": ["Component Pattern"]
                        }
                    ],
                    "best_practices": ["Follow ADK patterns"],
                    "references": ["ADK Guide"],
                    "setup_steps": [
                        {
                            "title": "Initialize Project",
                            "command": "cargo new project",
                            "description": "Create new project"
                        }
                    ]
                }
            elif tool_name == "get_best_practices":
                return {
                    "recommendations": ["Use dependency injection", "Implement error handling"],
                    "references": ["Best Practices Guide"],
                    "prerequisites": ["Rust knowledge"],
                    "implementation_guidance": ["Start simple", "Add complexity gradually"]
                }
            elif tool_name == "validate_architecture":
                return {
                    "recommended_approach": "Component-based architecture",
                    "findings": [],
                    "references": ["Architecture Guide"]
                }
            elif tool_name == "review_rust_file":
                return {
                    "findings": [],
                    "best_practices": {"error_handling": True},
                    "references": ["Code Review Guide"],
                    "common_issues": ["Missing error handling"],
                    "solutions": [
                        {
                            "issue": "Compilation Error",
                            "solution": "Check dependencies",
                            "command": "cargo check"
                        }
                    ]
                }
            return {"error": "Unknown tool"}
        
        self.mock_mcp_client.call_tool = mock_call_tool
    
    async def test_query_adk_documentation(self):
        """Test ADK documentation querying."""
        result = await self.agent._query_adk_documentation(
            "How to create components?", 
            AssistanceType.CODE_EXAMPLES
        )
        
        self.assertIn("answer", result)
        self.assertIn("examples", result)
        self.assertEqual(result["answer"], "ADK components are building blocks...")
    
    async def test_get_relevant_best_practices(self):
        """Test best practices retrieval."""
        result = await self.agent._get_relevant_best_practices(
            "Project setup help",
            AssistanceType.PROJECT_SETUP,
            self.sample_context
        )
        
        self.assertIn("recommendations", result)
        self.assertIn("Use dependency injection", result["recommendations"])
    
    async def test_get_architectural_guidance(self):
        """Test architectural guidance retrieval."""
        result = await self.agent._get_architectural_guidance(
            "Architecture advice",
            self.sample_context
        )
        
        self.assertIn("recommended_approach", result)
        self.assertEqual(result["recommended_approach"], "Component-based architecture")
    
    async def test_get_code_insights(self):
        """Test code insights retrieval."""
        result = await self.agent._get_code_insights(
            "Code help",
            self.sample_context
        )
        
        self.assertIn("best_practices", result)
        self.assertTrue(result["best_practices"]["error_handling"])
    
    async def test_gather_comprehensive_data(self):
        """Test comprehensive data gathering."""
        mcp_data = await self.agent._gather_comprehensive_data(
            "Help with project setup",
            self.sample_context,
            AssistanceType.PROJECT_SETUP
        )
        
        self.assertIn("adk_query", mcp_data)
        self.assertIn("best_practices", mcp_data)
        self.assertIn("architecture_validation", mcp_data)
    
    async def test_generate_project_setup_guidance(self):
        """Test project setup guidance generation."""
        mcp_data = {
            "adk_query": {
                "setup_steps": [
                    {
                        "title": "Create Project",
                        "command": "cargo new test",
                        "description": "Initialize project"
                    }
                ]
            },
            "best_practices": {
                "prerequisites": ["Rust installed"]
            }
        }
        
        guidance = self.agent._generate_project_setup_guidance(
            "Set up new project",
            self.sample_context,
            mcp_data
        )
        
        self.assertIsInstance(guidance, ProjectSetupGuidance)
        self.assertEqual(guidance.setup_type, "ADK Application")
        self.assertIn("Rust toolchain", guidance.prerequisites[0])
        self.assertTrue(len(guidance.steps) > 0)
    
    async def test_generate_architectural_guidance(self):
        """Test architectural guidance generation."""
        mcp_data = {
            "architecture_validation": {
                "recommended_approach": "Microservices"
            },
            "best_practices": {
                "implementation_guidance": ["Start with monolith"]
            }
        }
        
        guidance = self.agent._generate_architectural_guidance(
            "Architecture advice",
            self.sample_context,
            mcp_data
        )
        
        self.assertIsInstance(guidance, ArchitecturalGuidance)
        self.assertEqual(guidance.recommended_approach, "Microservices")
        self.assertTrue(len(guidance.alternatives) > 0)
        self.assertIn("Start with monolith", guidance.implementation_guidance)
    
    async def test_generate_code_examples(self):
        """Test code examples generation."""
        mcp_data = {
            "adk_query": {
                "examples": [
                    {
                        "title": "Custom Example",
                        "code": "custom code",
                        "description": "Custom description",
                        "language": "rust",
                        "explanation": "Custom explanation",
                        "best_practices": ["Custom practice"],
                        "related_patterns": ["Custom pattern"]
                    }
                ]
            }
        }
        
        examples = self.agent._generate_code_examples(
            "Show me examples",
            self.sample_context,
            mcp_data
        )
        
        self.assertIsInstance(examples, list)
        self.assertTrue(len(examples) > 0)
        self.assertIsInstance(examples[0], CodeExample)
        
        # Check for custom example from MCP data
        custom_example = next((ex for ex in examples if ex.title == "Custom Example"), None)
        self.assertIsNotNone(custom_example)
        self.assertEqual(custom_example.code, "custom code")
    
    async def test_generate_troubleshooting_guidance(self):
        """Test troubleshooting guidance generation."""
        mcp_data = {
            "code_insights": {
                "common_issues": ["Dependency conflicts"],
                "solutions": [
                    {
                        "issue": "Build Error",
                        "solution": "Update Cargo.toml",
                        "command": "cargo update"
                    }
                ]
            }
        }
        
        guidance = self.agent._generate_troubleshooting_guidance(
            "Fix my build errors",
            self.sample_context,
            mcp_data
        )
        
        self.assertIsInstance(guidance, TroubleshootingGuidance)
        self.assertEqual(guidance.issue_description, "Fix my build errors")
        self.assertIn("Dependency conflicts", guidance.likely_causes)
        
        # Check for custom solution from MCP data
        build_error_solution = next((sol for sol in guidance.solutions if sol["issue"] == "Build Error"), None)
        self.assertIsNotNone(build_error_solution)
        self.assertEqual(build_error_solution["command"], "cargo update")
    
    async def test_generate_task_breakdown(self):
        """Test task breakdown generation."""
        guidance = self.agent._generate_task_breakdown(
            "Build a user service",
            self.sample_context,
            {}
        )
        
        self.assertIsInstance(guidance, TaskBreakdown)
        self.assertEqual(guidance.task_description, "Build a user service")
        self.assertEqual(guidance.complexity_level, "Medium")
        self.assertTrue(len(guidance.steps) > 0)
        self.assertTrue(len(guidance.prerequisites) > 0)
    
    async def test_provide_assistance_project_setup(self):
        """Test complete assistance provision for project setup."""
        result = await self.agent.provide_assistance(
            "How do I set up a new ADK project?",
            self.sample_context,
            AssistanceType.PROJECT_SETUP
        )
        
        self.assertIsInstance(result, ProjectAssistanceResult)
        self.assertEqual(result.assistance_type, AssistanceType.PROJECT_SETUP)
        self.assertIsInstance(result.primary_guidance, ProjectSetupGuidance)
        self.assertTrue(len(result.best_practices) > 0)
        self.assertTrue(len(result.references) > 0)
    
    async def test_provide_assistance_code_examples(self):
        """Test complete assistance provision for code examples."""
        result = await self.agent.provide_assistance(
            "Show me ADK component examples",
            self.sample_context,
            AssistanceType.CODE_EXAMPLES
        )
        
        self.assertIsInstance(result, ProjectAssistanceResult)
        self.assertEqual(result.assistance_type, AssistanceType.CODE_EXAMPLES)
        self.assertIsInstance(result.primary_guidance, list)
        self.assertTrue(len(result.primary_guidance) > 0)
        self.assertIsInstance(result.primary_guidance[0], CodeExample)
    
    async def test_provide_assistance_auto_detection(self):
        """Test assistance provision with automatic type detection."""
        result = await self.agent.provide_assistance(
            "How do I create a new ADK project?",
            self.sample_context
        )
        
        self.assertIsInstance(result, ProjectAssistanceResult)
        self.assertEqual(result.assistance_type, AssistanceType.PROJECT_SETUP)
    
    async def test_fallback_assistance(self):
        """Test fallback assistance when MCP fails."""
        result = await self.agent._fallback_assistance(
            "Help with ADK",
            self.sample_context,
            "MCP server connection failed"
        )
        
        self.assertIsInstance(result, ProjectAssistanceResult)
        # The assistance type should be determined by the request, not always GENERAL_GUIDANCE
        expected_type = self.agent._determine_assistance_type("Help with ADK", self.sample_context)
        self.assertEqual(result.assistance_type, expected_type)
        self.assertIn("Fallback ADK Project Assistance", result.primary_guidance)
        self.assertIn("MCP server connection failed", result.primary_guidance)
    
    async def test_mcp_tool_failure_handling(self):
        """Test handling of MCP tool failures."""
        # Mock a failing MCP client
        async def failing_call_tool(server_name, tool_name, arguments):
            raise Exception("MCP tool failed")
        
        self.mock_mcp_client.call_tool = failing_call_tool
        
        result = await self.agent.provide_assistance(
            "Help with project setup",
            self.sample_context,
            AssistanceType.PROJECT_SETUP
        )
        
        # Should fall back gracefully but maintain the requested assistance type
        self.assertIsInstance(result, ProjectAssistanceResult)
        self.assertEqual(result.assistance_type, AssistanceType.PROJECT_SETUP)


class TestDataClasses(unittest.TestCase):
    """Test data classes and structures."""
    
    def test_project_setup_guidance(self):
        """Test ProjectSetupGuidance data class."""
        guidance = ProjectSetupGuidance(
            setup_type="ADK Application",
            prerequisites=["Rust", "ADK SDK"],
            steps=[{"step": "1", "command": "cargo new", "description": "Create project"}],
            configuration_files=[{"file": "Cargo.toml", "purpose": "Dependencies"}],
            validation_steps=["cargo check"],
            next_steps=["Implement logic"]
        )
        
        self.assertEqual(guidance.setup_type, "ADK Application")
        self.assertEqual(len(guidance.prerequisites), 2)
        self.assertEqual(len(guidance.steps), 1)
    
    def test_code_example(self):
        """Test CodeExample data class."""
        example = CodeExample(
            title="Test Example",
            description="A test example",
            code="fn main() {}",
            language="rust",
            explanation="Simple main function",
            best_practices=["Use proper naming"],
            related_patterns=["Main Pattern"]
        )
        
        self.assertEqual(example.title, "Test Example")
        self.assertEqual(example.language, "rust")
        self.assertEqual(len(example.best_practices), 1)
    
    def test_project_assistance_result(self):
        """Test ProjectAssistanceResult data class."""
        result = ProjectAssistanceResult(
            assistance_type=AssistanceType.GENERAL_GUIDANCE,
            summary="Test assistance",
            primary_guidance="Test guidance content",
            additional_resources=["Resource 1"],
            best_practices=["Practice 1"],
            references=["Reference 1"],
            follow_up_suggestions=["Suggestion 1"]
        )
        
        self.assertEqual(result.assistance_type, AssistanceType.GENERAL_GUIDANCE)
        self.assertEqual(result.summary, "Test assistance")
        self.assertEqual(len(result.additional_resources), 1)


class TestFormatting(unittest.TestCase):
    """Test result formatting functions."""
    
    def test_format_project_assistance_result(self):
        """Test project assistance result formatting."""
        result = ProjectAssistanceResult(
            assistance_type=AssistanceType.GENERAL_GUIDANCE,
            summary="Test assistance summary",
            primary_guidance="Test guidance content",
            additional_resources=["Resource 1", "Resource 2"],
            best_practices=["Practice 1", "Practice 2"],
            references=["Reference 1"],
            follow_up_suggestions=["Suggestion 1"]
        )
        
        formatted = format_project_assistance_result(result)
        
        self.assertIn("ADK Project Assistant Results", formatted)
        self.assertIn("Test assistance summary", formatted)
        self.assertIn("General Guidance", formatted)
        self.assertIn("Test guidance content", formatted)
        self.assertIn("Best Practices", formatted)
        self.assertIn("Additional Resources", formatted)
        self.assertIn("Follow-up Suggestions", formatted)
        self.assertIn("References", formatted)
    
    def test_format_project_setup_guidance(self):
        """Test project setup guidance formatting."""
        from adk_project_assistant_agent import _format_project_setup_guidance
        
        guidance = ProjectSetupGuidance(
            setup_type="ADK Application",
            prerequisites=["Rust toolchain"],
            steps=[{
                "step": "1. Initialize Project",
                "command": "cargo new test",
                "description": "Create new project"
            }],
            configuration_files=[{
                "file": "Cargo.toml",
                "purpose": "Dependencies"
            }],
            validation_steps=["cargo check"],
            next_steps=["Add components"]
        )
        
        formatted = _format_project_setup_guidance(guidance)
        
        self.assertIn("ADK Application Setup", formatted[0])
        self.assertIn("Prerequisites:", formatted[2])
        self.assertIn("Rust toolchain", formatted[3])
        self.assertIn("Setup Steps:", formatted[5])
    
    def test_format_code_examples(self):
        """Test code examples formatting."""
        from adk_project_assistant_agent import _format_code_examples
        
        examples = [
            CodeExample(
                title="Test Example",
                description="A test example",
                code="fn main() { println!(\"Hello\"); }",
                language="rust",
                explanation="Simple hello world",
                best_practices=["Use proper formatting"],
                related_patterns=["Main Pattern"]
            )
        ]
        
        formatted = _format_code_examples(examples)
        
        self.assertIn("Example 1: Test Example", formatted[0])
        self.assertIn("A test example", formatted[2])
        self.assertIn("```rust", formatted[4])
        self.assertIn("fn main()", formatted[5])
        # Find the explanation line dynamically
        explanation_found = False
        for line in formatted:
            if "Simple hello world" in line:
                explanation_found = True
                break
        self.assertTrue(explanation_found, "Explanation 'Simple hello world' not found in formatted output")


class TestConfiguration(unittest.TestCase):
    """Test configuration file validation."""
    
    def test_agent_configuration_file_exists(self):
        """Test that the agent configuration file exists and is valid."""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'adk_project_assistant_agent.json')
        
        # Check if running from test directory
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.dirname(__file__), 'adk_project_assistant_agent.json')
        
        self.assertTrue(os.path.exists(config_path), 
                       f"Configuration file not found at {config_path}")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Validate required configuration fields
        self.assertIn('name', config)
        self.assertIn('version', config)
        self.assertIn('description', config)
        self.assertIn('configuration', config)
        self.assertIn('capabilities', config)
        
        # Validate MCP integration configuration
        mcp_config = config['configuration']
        self.assertEqual(mcp_config['mcpServer'], 'arkaft-google-adk')
        self.assertIn('adk_query', mcp_config['requiredTools'])
        self.assertIn('get_best_practices', mcp_config['requiredTools'])
        self.assertIn('validate_architecture', mcp_config['requiredTools'])
        self.assertIn('review_rust_file', mcp_config['requiredTools'])
        
        # Validate capabilities
        expected_capabilities = [
            'project-setup',
            'architecture-guidance',
            'code-examples',
            'troubleshooting',
            'task-breakdown',
            'comprehensive-assistance'
        ]
        for capability in expected_capabilities:
            self.assertIn(capability, config['capabilities'])


def run_tests():
    """Run all tests with detailed output."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestADKProjectAssistantAgent,
        TestADKProjectAssistantAgentAsync,
        TestDataClasses,
        TestFormatting,
        TestConfiguration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"ADK Project Assistant Agent Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*60}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("ADK Project Assistant Agent Test Suite")
    print("=" * 60)
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)