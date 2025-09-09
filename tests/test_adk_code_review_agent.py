#!/usr/bin/env python3
"""
Test script for ADK Code Review Agent

This script tests the agent implementation with sample code and mock MCP responses.
"""

import asyncio
import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))
from adk_code_review_agent import ADKCodeReviewAgent, format_review_result, Priority, ReviewFinding


class MockMCPClient:
    """Mock MCP client for testing the agent without actual MCP server."""
    
    def __init__(self, simulate_failure=False):
        self.simulate_failure = simulate_failure
        self.call_count = 0
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: dict):
        """Mock MCP tool calls with realistic responses."""
        self.call_count += 1
        
        if self.simulate_failure:
            raise Exception("Mock MCP server failure")
        
        if tool_name == "review_rust_file":
            return {
                "findings": [
                    {
                        "priority": "High",
                        "title": "Translation Support Missing",
                        "location": "Lines 3-4",
                        "description": "Hardcoded error messages should be externalized for translation",
                        "adk_impact": "Prevents proper internationalization and user experience localization",
                        "recommendation": "Use ADK translation APIs to externalize strings",
                        "example": 'return Err(translate!("errors.user_not_found"));'
                    },
                    {
                        "priority": "Medium",
                        "title": "Error Handling Enhancement",
                        "location": "Line 3",
                        "description": "Generic String error type could be more specific",
                        "adk_impact": "Reduces debugging capability and user-friendly error reporting",
                        "recommendation": "Use ADK-specific error types with proper context"
                    }
                ],
                "best_practices": {
                    "async_usage": True,
                    "error_handling": False,
                    "translation_support": False,
                    "code_organization": True
                },
                "references": [
                    "ADK Translation Guide",
                    "ADK Error Handling Best Practices"
                ]
            }
        
        elif tool_name == "validate_architecture":
            return {
                "findings": [
                    {
                        "priority": "Medium",
                        "title": "Component Interface Design",
                        "location": "Function signature",
                        "description": "Function could benefit from more structured error types",
                        "adk_impact": "Affects error handling consistency across the application",
                        "recommendation": "Consider using Result<T, AdkError> pattern"
                    }
                ],
                "best_practices": {
                    "separation_of_concerns": True,
                    "dependency_management": True,
                    "component_organization": True
                },
                "references": [
                    "ADK Architecture Patterns Guide"
                ]
            }
        
        elif tool_name == "get_best_practices":
            return {
                "compliance": {
                    "naming_conventions": True,
                    "documentation": False,
                    "testing": False
                },
                "recommendations": [
                    "Add comprehensive documentation comments",
                    "Implement unit tests for error scenarios"
                ],
                "references": [
                    "ADK Development Best Practices"
                ]
            }
        
        else:
            return {"error": f"Unknown tool: {tool_name}"}


async def test_successful_review():
    """Test successful code review with all MCP tools working."""
    print("=== Testing Successful Code Review ===")
    
    mock_client = MockMCPClient(simulate_failure=False)
    agent = ADKCodeReviewAgent(mock_client)
    
    sample_code = '''
pub fn get_user(id: u32) -> Result<User, String> {
    if id == 0 {
        return Err("User not found".to_string());
    }
    // TODO: Implement actual user lookup
    Ok(User { id, name: "Test User".to_string() })
}
'''
    
    result = await agent.review_file("src/user_service.rs", sample_code, {})
    formatted_output = format_review_result(result)
    
    print(formatted_output)
    print(f"\nMCP tool calls made: {mock_client.call_count}")
    print("✅ Successful review test completed\n")


async def test_mcp_failure_fallback():
    """Test graceful degradation when MCP server fails."""
    print("=== Testing MCP Failure Fallback ===")
    
    mock_client = MockMCPClient(simulate_failure=True)
    agent = ADKCodeReviewAgent(mock_client)
    
    sample_code = '''
pub fn risky_function() -> String {
    let data = get_data().unwrap(); // This could panic!
    println!("Debug: processing {}", data);
    data.to_string()
}
'''
    
    result = await agent.review_file("src/risky_code.rs", sample_code, {})
    formatted_output = format_review_result(result)
    
    print(formatted_output)
    print("✅ Fallback test completed\n")


async def test_architectural_validation():
    """Test architectural validation with complex code."""
    print("=== Testing Architectural Validation ===")
    
    mock_client = MockMCPClient(simulate_failure=False)
    agent = ADKCodeReviewAgent(mock_client)
    
    sample_code = '''
pub struct UserService {
    repository: Box<dyn UserRepository>,
}

impl UserService {
    pub fn new(repository: Box<dyn UserRepository>) -> Self {
        Self { repository }
    }
    
    pub async fn create_user(&self, user_data: CreateUserRequest) -> Result<User, ServiceError> {
        // Validate input
        if user_data.email.is_empty() {
            return Err(ServiceError::ValidationError("Email is required".to_string()));
        }
        
        // Create user
        self.repository.create(user_data).await
    }
}

pub trait UserRepository {
    async fn create(&self, user_data: CreateUserRequest) -> Result<User, RepositoryError>;
}
'''
    
    result = await agent.review_file("src/services/user_service.rs", sample_code, {})
    formatted_output = format_review_result(result)
    
    print(formatted_output)
    print(f"MCP tool calls made: {mock_client.call_count}")
    print("✅ Architectural validation test completed\n")


async def test_edge_cases():
    """Test edge cases and error conditions."""
    print("=== Testing Edge Cases ===")
    
    mock_client = MockMCPClient(simulate_failure=False)
    agent = ADKCodeReviewAgent(mock_client)
    
    # Test with empty file
    result = await agent.review_file("src/empty.rs", "", {})
    print("Empty file result:", result.summary)
    
    # Test with very simple file (no architectural patterns)
    simple_code = "const VERSION: &str = \"1.0.0\";"
    result = await agent.review_file("src/constants.rs", simple_code, {})
    print("Simple file result:", result.summary)
    
    print("✅ Edge cases test completed\n")


async def run_all_tests():
    """Run all test scenarios."""
    print("🚀 Starting ADK Code Review Agent Tests\n")
    
    try:
        await test_successful_review()
        await test_mcp_failure_fallback()
        await test_architectural_validation()
        await test_edge_cases()
        
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())