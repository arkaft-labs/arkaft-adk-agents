#!/usr/bin/env python3
"""
Test suite for ADK Architecture Agent

This script tests the ADK Architecture Agent functionality with various
architectural scenarios and validates the MCP integration.
"""

import asyncio
import json
from typing import Dict, Any
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))
from adk_architecture_agent import ADKArchitectureAgent, format_architectural_validation_result


class MockMCPClient:
    """Mock MCP client for testing the architecture agent."""
    
    def __init__(self, scenario: str = "default"):
        self.scenario = scenario
        self.call_count = 0
        
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]):
        """Mock MCP tool calls with different scenarios."""
        self.call_count += 1
        
        if self.scenario == "mcp_failure":
            raise Exception("MCP server unavailable")
        
        if tool_name == "validate_architecture":
            return self._mock_validate_architecture(arguments)
        elif tool_name == "get_best_practices":
            return self._mock_get_best_practices(arguments)
        elif tool_name == "adk_query":
            return self._mock_adk_query(arguments)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    def _mock_validate_architecture(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Mock validate_architecture tool response."""
        file_path = arguments.get("file_path", "")
        
        if "lib.rs" in file_path:
            return {
                "findings": [
                    {
                        "priority": "Medium",
                        "component": "Module Organization",
                        "location": "src/lib.rs, module declarations",
                        "current_state": "Modules are functional but could benefit from better organization",
                        "adk_compliance": "Partially compliant - follows basic patterns but misses some ADK conventions",
                        "issues": "Some modules expose too much internal structure, reducing encapsulation",
                        "recommendations": "Implement proper facade pattern for module interfaces, hide internal implementation details",
                        "impact": "Improves maintainability and follows ADK encapsulation best practices",
                        "example": "pub use internal_service::PublicInterface;"
                    },
                    {
                        "priority": "High",
                        "component": "Dependency Injection Pattern",
                        "location": "Component initialization in main.rs",
                        "current_state": "Direct instantiation without proper dependency injection",
                        "adk_compliance": "Non-compliant - ADK recommends dependency injection for testability",
                        "issues": "Hard-coded dependencies make testing and configuration difficult",
                        "recommendations": "Implement ADK dependency injection container pattern",
                        "impact": "Critical for proper ADK application architecture and testing",
                        "example": "Use ADK's built-in DI container for component management"
                    }
                ],
                "patterns": {
                    "compliant": ["Basic ADK component structure", "Proper async/await usage"],
                    "non_compliant": ["Dependency injection pattern"],
                    "missing": ["Configuration management pattern"]
                },
                "dependencies": {
                    "compliant": ["ADK core dependencies properly configured", "Version compatibility maintained"],
                    "issues": ["Optional dependencies could be better organized"],
                    "recommendations": ["Group related optional dependencies using Cargo features", "Leverage ADK's built-in dependency resolution capabilities"]
                },
                "references": ["ADK Architecture Guide", "ADK Component Design Patterns"]
            }
        
        elif "Cargo.toml" in file_path:
            return {
                "findings": [
                    {
                        "priority": "Medium",
                        "component": "Feature Organization",
                        "location": "Cargo.toml [features] section",
                        "current_state": "Features are defined but could be better organized",
                        "adk_compliance": "Partially compliant - basic feature usage but missing ADK patterns",
                        "issues": "Related features not grouped, missing ADK-specific feature flags",
                        "recommendations": "Group related features and add ADK-recommended feature flags",
                        "impact": "Improves build flexibility and ADK integration",
                        "example": '[features]\ndefault = ["adk-runtime"]\nadk-full = ["adk-runtime", "adk-ui", "adk-networking"]'
                    }
                ],
                "patterns": {
                    "compliant": ["Basic dependency management"],
                    "non_compliant": [],
                    "missing": ["ADK feature organization pattern"]
                },
                "dependencies": {
                    "compliant": ["google-adk", "adk-core"],
                    "issues": [],
                    "missing": ["adk-testing"],
                    "recommendations": ["Add adk-testing for comprehensive test support"]
                }
            }
        
        else:
            return {
                "findings": [],
                "patterns": {"compliant": [], "non_compliant": [], "missing": []},
                "dependencies": {"compliant": [], "issues": [], "recommendations": []}
            }
    
    def _mock_get_best_practices(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Mock get_best_practices tool response."""
        scenario = arguments.get("scenario", "general_architecture")
        
        return {
            "pattern_compliance": {
                "followed": ["Proper async/await usage in architectural context"],
                "violated": ["Dependency injection pattern needs implementation"],
                "recommendations": [
                    "ADK Dependency Injection: Use ADK's DI container for component management",
                    "Configuration Management: Implement ADK's configuration validation patterns",
                    "Component Lifecycle: Follow ADK component initialization and cleanup patterns"
                ]
            },
            "architectural_guidance": [
                "Implement proper separation of concerns between components",
                "Use ADK's built-in patterns for component communication",
                "Follow ADK naming conventions for architectural elements"
            ],
            "references": [
                "ADK Dependency Injection Patterns",
                "ADK Configuration Management",
                "ADK Component Lifecycle"
            ]
        }
    
    def _mock_adk_query(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Mock adk_query tool response."""
        query = arguments.get("query", "")
        
        return {
            "guidance": f"ADK architectural guidance for: {query}",
            "recommended_patterns": [
                "Component Lifecycle pattern for proper initialization",
                "Configuration Validation pattern for robust config handling"
            ],
            "examples": [
                "Use ADK's ComponentManager for lifecycle management",
                "Implement ConfigValidator for configuration validation"
            ],
            "references": [
                "https://docs.google.com/adk/architecture",
                "https://docs.google.com/adk/component-lifecycle"
            ]
        }


async def test_lib_rs_validation():
    """Test architectural validation for lib.rs file."""
    print("=== Testing lib.rs Architectural Validation ===")
    
    agent = ADKArchitectureAgent(MockMCPClient("default"))
    
    sample_lib_rs = '''
pub mod user_service;
pub mod data_models;
pub mod internal_service {
    pub struct InternalData {
        pub value: String,
    }
    pub fn internal_function() -> String {
        "internal".to_string()
    }
}

pub use user_service::UserService;
pub use data_models::User;

pub fn initialize_app() -> Result<(), Box<dyn std::error::Error>> {
    // Direct instantiation without DI
    let service = UserService::new();
    Ok(())
}
'''
    
    result = await agent.validate_architecture(
        "src/lib.rs", 
        sample_lib_rs, 
        {"project_type": "adk", "dependencies": ["google-adk"]}
    )
    
    formatted_output = format_architectural_validation_result(result)
    print(formatted_output)
    print("\n" + "="*80 + "\n")


async def test_cargo_toml_validation():
    """Test architectural validation for Cargo.toml file."""
    print("=== Testing Cargo.toml Architectural Validation ===")
    
    agent = ADKArchitectureAgent(MockMCPClient("default"))
    
    sample_cargo_toml = '''
[package]
name = "my-adk-app"
version = "0.1.0"
edition = "2021"

[dependencies]
google-adk = "1.0"
adk-core = "1.0"
tokio = { version = "1.0", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }

[features]
default = []
ui = ["adk-ui"]
networking = ["adk-networking"]
'''
    
    result = await agent.validate_architecture(
        "Cargo.toml", 
        sample_cargo_toml, 
        {"project_type": "adk", "has_ui": True}
    )
    
    formatted_output = format_architectural_validation_result(result)
    print(formatted_output)
    print("\n" + "="*80 + "\n")


async def test_mcp_failure_scenario():
    """Test graceful degradation when MCP server fails."""
    print("=== Testing MCP Failure Scenario ===")
    
    agent = ADKArchitectureAgent(MockMCPClient("mcp_failure"))
    
    sample_code = '''
pub struct MyComponent {
    data: String,
}

impl MyComponent {
    pub fn new() -> Self {
        Self {
            data: "test".to_string(),
        }
    }
}
'''
    
    result = await agent.validate_architecture(
        "src/components/my_component.rs", 
        sample_code, 
        {"project_type": "adk"}
    )
    
    formatted_output = format_architectural_validation_result(result)
    print(formatted_output)
    print("\n" + "="*80 + "\n")


async def test_validation_scope_determination():
    """Test validation scope determination for different file types."""
    print("=== Testing Validation Scope Determination ===")
    
    agent = ADKArchitectureAgent(MockMCPClient("default"))
    
    test_cases = [
        ("src/lib.rs", "Library root file"),
        ("src/main.rs", "Application root file"),
        ("src/components/mod.rs", "Module interface file"),
        ("Cargo.toml", "Project configuration file"),
        ("adk.toml", "ADK configuration file"),
        ("src/services/user_service.rs", "Component file")
    ]
    
    for file_path, description in test_cases:
        scope = agent._determine_validation_scope(file_path, "sample content")
        print(f"**{description}** (`{file_path}`):")
        print(f"  - File Type: {scope['file_type']}")
        print(f"  - Validation Areas: {', '.join(scope['validation_areas'])}")
        print(f"  - Priority Focus: {', '.join(scope['priority_focus'])}")
        print()
    
    print("="*80 + "\n")


async def test_coordination_features():
    """Test agent coordination and consistency features."""
    print("=== Testing Agent Coordination Features ===")
    
    agent = ADKArchitectureAgent(MockMCPClient("default"))
    
    # Test coordination context
    agent.coordination_context = {
        "previous_recommendations": ["Implement proper error handling"],
        "shared_decisions": ["Use ADK dependency injection pattern"],
        "consistency_requirements": ["Maintain architectural alignment"]
    }
    
    result = await agent.validate_architecture(
        "src/lib.rs", 
        "pub mod test;", 
        {"project_type": "adk", "coordination_context": agent.coordination_context}
    )
    
    print("**Coordination Notes:**")
    for note in result.coordination_notes:
        print(f"- {note}")
    
    print(f"\n**Compliance Level:** {result.compliance_level}")
    print(f"**Summary:** {result.summary}")
    
    print("\n" + "="*80 + "\n")


async def run_all_tests():
    """Run all test scenarios."""
    print("ADK Architecture Agent Test Suite")
    print("=" * 80)
    print()
    
    await test_lib_rs_validation()
    await test_cargo_toml_validation()
    await test_mcp_failure_scenario()
    await test_validation_scope_determination()
    await test_coordination_features()
    
    print("All tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(run_all_tests())