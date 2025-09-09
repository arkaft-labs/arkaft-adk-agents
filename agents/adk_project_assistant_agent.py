#!/usr/bin/env python3
"""
ADK Project Assistant Agent Implementation

This agent provides comprehensive project assistance for Google ADK projects using all
arkaft-mcp-google-adk MCP server tools for project setup, architectural guidance,
code examples, troubleshooting, and task breakdown.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class AssistanceType(Enum):
    PROJECT_SETUP = "project_setup"
    ARCHITECTURE_GUIDANCE = "architecture_guidance"
    CODE_EXAMPLES = "code_examples"
    TROUBLESHOOTING = "troubleshooting"
    TASK_BREAKDOWN = "task_breakdown"
    GENERAL_GUIDANCE = "general_guidance"


class Priority(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class ProjectSetupGuidance:
    """Project setup guidance with step-by-step instructions."""
    setup_type: str
    prerequisites: List[str]
    steps: List[Dict[str, str]]
    configuration_files: List[Dict[str, str]]
    validation_steps: List[str]
    next_steps: List[str]


@dataclass
class ArchitecturalGuidance:
    """Architectural decision guidance."""
    decision_context: str
    recommended_approach: str
    alternatives: List[Dict[str, str]]
    trade_offs: Dict[str, List[str]]
    implementation_guidance: List[str]
    validation_criteria: List[str]


@dataclass
class CodeExample:
    """Code example with context and explanation."""
    title: str
    description: str
    code: str
    language: str
    explanation: str
    best_practices: List[str]
    related_patterns: List[str]


@dataclass
class TroubleshootingGuidance:
    """Troubleshooting assistance with solutions."""
    issue_description: str
    likely_causes: List[str]
    diagnostic_steps: List[str]
    solutions: List[Dict[str, str]]
    prevention_tips: List[str]
    related_issues: List[str]


@dataclass
class TaskBreakdown:
    """Task breakdown with step-by-step guidance."""
    task_description: str
    complexity_level: str
    estimated_time: str
    prerequisites: List[str]
    steps: List[Dict[str, Any]]
    validation_points: List[str]
    success_criteria: List[str]


@dataclass
class ProjectAssistanceResult:
    """Complete project assistance result."""
    assistance_type: AssistanceType
    summary: str
    primary_guidance: Union[ProjectSetupGuidance, ArchitecturalGuidance, List[CodeExample], 
                           TroubleshootingGuidance, TaskBreakdown, str]
    additional_resources: List[str]
    best_practices: List[str]
    references: List[str]
    follow_up_suggestions: List[str]


class ADKProjectAssistantAgent:
    """
    ADK Project Assistant Agent that uses all MCP tools to provide comprehensive
    project assistance including setup, architecture, examples, troubleshooting,
    and task breakdown.
    """
    
    def __init__(self, mcp_client):
        """Initialize the agent with MCP client."""
        self.mcp_client = mcp_client
        self.mcp_server_name = "arkaft-google-adk"
        self.project_context = {}
        
    async def provide_assistance(
        self, 
        user_request: str, 
        project_context: Dict[str, Any],
        assistance_type: Optional[AssistanceType] = None
    ) -> ProjectAssistanceResult:
        """
        Main entry point for project assistance.
        
        Args:
            user_request: User's request for assistance
            project_context: Current project context
            assistance_type: Optional specific type of assistance requested
            
        Returns:
            ProjectAssistanceResult with comprehensive guidance
        """
        try:
            # Step 1: Determine assistance type if not specified
            if not assistance_type:
                assistance_type = self._determine_assistance_type(user_request, project_context)
            
            # Step 2: Gather comprehensive information using all MCP tools
            mcp_data = await self._gather_comprehensive_data(
                user_request, project_context, assistance_type
            )
            
            # Step 3: Generate specific guidance based on assistance type
            primary_guidance = await self._generate_primary_guidance(
                assistance_type, user_request, project_context, mcp_data
            )
            
            # Step 4: Compile comprehensive assistance result
            return await self._compile_assistance_result(
                assistance_type, user_request, primary_guidance, mcp_data
            )
            
        except Exception as e:
            # Graceful degradation on MCP failures
            return await self._fallback_assistance(user_request, project_context, str(e))
    
    def _determine_assistance_type(self, user_request: str, project_context: Dict[str, Any]) -> AssistanceType:
        """Determine the type of assistance needed based on user request and context."""
        request_lower = user_request.lower()
        
        # Project setup indicators (check first for specificity)
        setup_keywords = ["setup", "set up", "create", "initialize", "start", "new project", "scaffold"]
        if any(keyword in request_lower for keyword in setup_keywords):
            return AssistanceType.PROJECT_SETUP
        
        # Task breakdown indicators (check before code examples to avoid conflicts)
        task_keywords = ["break down", "steps", "plan", "roadmap", "guide", "process"]
        if any(keyword in request_lower for keyword in task_keywords):
            return AssistanceType.TASK_BREAKDOWN
        
        # Code examples indicators
        code_keywords = ["example", "code", "implement", "how to", "show me", "sample"]
        if any(keyword in request_lower for keyword in code_keywords):
            return AssistanceType.CODE_EXAMPLES
        
        # Troubleshooting indicators
        trouble_keywords = ["error", "issue", "problem", "fix", "debug", "not working", "help"]
        if any(keyword in request_lower for keyword in trouble_keywords):
            return AssistanceType.TROUBLESHOOTING
        
        # Architecture guidance indicators (check after more specific types)
        arch_keywords = ["architecture", "design", "structure", "organize", "pattern", "component"]
        if any(keyword in request_lower for keyword in arch_keywords):
            return AssistanceType.ARCHITECTURE_GUIDANCE
        
        return AssistanceType.GENERAL_GUIDANCE
    
    async def _gather_comprehensive_data(
        self, 
        user_request: str, 
        project_context: Dict[str, Any],
        assistance_type: AssistanceType
    ) -> Dict[str, Any]:
        """Gather data from all relevant MCP tools."""
        
        mcp_data = {}
        
        # Always get ADK query results for documentation and guidance
        mcp_data["adk_query"] = await self._query_adk_documentation(user_request, assistance_type)
        
        # Get best practices relevant to the assistance type
        mcp_data["best_practices"] = await self._get_relevant_best_practices(
            user_request, assistance_type, project_context
        )
        
        # Get architectural validation if relevant
        if assistance_type in [AssistanceType.ARCHITECTURE_GUIDANCE, AssistanceType.PROJECT_SETUP]:
            mcp_data["architecture_validation"] = await self._get_architectural_guidance(
                user_request, project_context
            )
        
        # Get code review insights if code-related
        if assistance_type in [AssistanceType.CODE_EXAMPLES, AssistanceType.TROUBLESHOOTING]:
            mcp_data["code_insights"] = await self._get_code_insights(
                user_request, project_context
            )
        
        return mcp_data
    
    async def _query_adk_documentation(self, user_request: str, assistance_type: AssistanceType) -> Dict[str, Any]:
        """Query ADK documentation using adk_query MCP tool."""
        try:
            # Enhance query based on assistance type
            enhanced_query = self._enhance_query_for_type(user_request, assistance_type)
            
            result = await self.mcp_client.call_tool(
                server_name=self.mcp_server_name,
                tool_name="adk_query",
                arguments={
                    "query": enhanced_query,
                    "include_examples": True,
                    "include_best_practices": True,
                    "version": "latest",
                    "context": {
                        "assistance_type": assistance_type.value,
                        "comprehensive_guidance": True
                    }
                }
            )
            return result
        except Exception as e:
            print(f"Warning: adk_query MCP tool failed: {e}")
            return {"error": str(e)}
    
    async def _get_relevant_best_practices(
        self, 
        user_request: str, 
        assistance_type: AssistanceType,
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get best practices using get_best_practices MCP tool."""
        try:
            scenario = self._determine_best_practices_scenario(assistance_type, user_request)
            
            result = await self.mcp_client.call_tool(
                server_name=self.mcp_server_name,
                tool_name="get_best_practices",
                arguments={
                    "scenario": scenario,
                    "context": {
                        "assistance_type": assistance_type.value,
                        "project_context": project_context,
                        "comprehensive_guidance": True
                    }
                }
            )
            return result
        except Exception as e:
            print(f"Warning: get_best_practices MCP tool failed: {e}")
            return {"error": str(e)}
    
    async def _get_architectural_guidance(
        self, 
        user_request: str, 
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get architectural guidance using validate_architecture MCP tool."""
        try:
            # Create a sample structure for validation if none exists
            sample_content = self._create_sample_content_for_validation(user_request, project_context)
            
            result = await self.mcp_client.call_tool(
                server_name=self.mcp_server_name,
                tool_name="validate_architecture",
                arguments={
                    "file_content": sample_content,
                    "file_path": "project_structure_analysis",
                    "validation_focus": [
                        "project_organization",
                        "component_design",
                        "dependency_management",
                        "adk_patterns"
                    ],
                    "guidance_mode": True
                }
            )
            return result
        except Exception as e:
            print(f"Warning: validate_architecture MCP tool failed: {e}")
            return {"error": str(e)}
    
    async def _get_code_insights(
        self, 
        user_request: str, 
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get code insights using review_rust_file MCP tool."""
        try:
            # Create sample code for analysis if none provided
            sample_code = self._create_sample_code_for_analysis(user_request, project_context)
            
            result = await self.mcp_client.call_tool(
                server_name=self.mcp_server_name,
                tool_name="review_rust_file",
                arguments={
                    "file_content": sample_code,
                    "file_path": "example_analysis.rs",
                    "focus_areas": [
                        "adk_patterns",
                        "best_practices",
                        "code_examples",
                        "implementation_guidance"
                    ],
                    "guidance_mode": True
                }
            )
            return result
        except Exception as e:
            print(f"Warning: review_rust_file MCP tool failed: {e}")
            return {"error": str(e)}
    
    async def _generate_primary_guidance(
        self,
        assistance_type: AssistanceType,
        user_request: str,
        project_context: Dict[str, Any],
        mcp_data: Dict[str, Any]
    ) -> Union[ProjectSetupGuidance, ArchitecturalGuidance, List[CodeExample], 
               TroubleshootingGuidance, TaskBreakdown, str]:
        """Generate primary guidance based on assistance type."""
        
        if assistance_type == AssistanceType.PROJECT_SETUP:
            return self._generate_project_setup_guidance(user_request, project_context, mcp_data)
        
        elif assistance_type == AssistanceType.ARCHITECTURE_GUIDANCE:
            return self._generate_architectural_guidance(user_request, project_context, mcp_data)
        
        elif assistance_type == AssistanceType.CODE_EXAMPLES:
            return self._generate_code_examples(user_request, project_context, mcp_data)
        
        elif assistance_type == AssistanceType.TROUBLESHOOTING:
            return self._generate_troubleshooting_guidance(user_request, project_context, mcp_data)
        
        elif assistance_type == AssistanceType.TASK_BREAKDOWN:
            return self._generate_task_breakdown(user_request, project_context, mcp_data)
        
        else:  # GENERAL_GUIDANCE
            return self._generate_general_guidance(user_request, project_context, mcp_data)
    
    def _generate_project_setup_guidance(
        self, 
        user_request: str, 
        project_context: Dict[str, Any], 
        mcp_data: Dict[str, Any]
    ) -> ProjectSetupGuidance:
        """Generate project setup guidance."""
        
        # Extract setup information from MCP data
        adk_info = mcp_data.get("adk_query", {})
        best_practices = mcp_data.get("best_practices", {})
        
        # Determine setup type
        setup_type = "ADK Application"
        if "service" in user_request.lower():
            setup_type = "ADK Service"
        elif "component" in user_request.lower():
            setup_type = "ADK Component"
        elif "library" in user_request.lower():
            setup_type = "ADK Library"
        
        # Generate prerequisites
        prerequisites = [
            "Rust toolchain (latest stable)",
            "Google ADK SDK access",
            "Development environment setup"
        ]
        
        if "prerequisites" in best_practices:
            prerequisites.extend(best_practices["prerequisites"])
        
        # Generate setup steps
        steps = [
            {
                "step": "1. Initialize Rust Project",
                "command": "cargo new my-adk-project --bin",
                "description": "Create a new Rust project with binary target"
            },
            {
                "step": "2. Configure Cargo.toml",
                "command": "# Add ADK dependencies to Cargo.toml",
                "description": "Add necessary ADK dependencies and configuration"
            },
            {
                "step": "3. Set up project structure",
                "command": "mkdir -p src/{components,services,models}",
                "description": "Create recommended directory structure"
            },
            {
                "step": "4. Initialize ADK configuration",
                "command": "# Create adk.toml configuration file",
                "description": "Set up ADK-specific configuration"
            }
        ]
        
        # Extract additional steps from MCP data
        if "setup_steps" in adk_info:
            for step in adk_info["setup_steps"]:
                steps.append({
                    "step": step.get("title", "Additional Step"),
                    "command": step.get("command", ""),
                    "description": step.get("description", "")
                })
        
        # Generate configuration files
        config_files = [
            {
                "file": "Cargo.toml",
                "purpose": "Project dependencies and metadata",
                "template": "ADK project template with required dependencies"
            },
            {
                "file": "adk.toml",
                "purpose": "ADK-specific configuration",
                "template": "ADK configuration template"
            }
        ]
        
        # Generate validation steps
        validation_steps = [
            "cargo check - Verify project compiles",
            "cargo test - Run initial tests",
            "ADK configuration validation",
            "Dependency resolution check"
        ]
        
        # Generate next steps
        next_steps = [
            "Implement core application logic",
            "Add ADK components and services",
            "Set up testing framework",
            "Configure deployment pipeline"
        ]
        
        return ProjectSetupGuidance(
            setup_type=setup_type,
            prerequisites=prerequisites,
            steps=steps,
            configuration_files=config_files,
            validation_steps=validation_steps,
            next_steps=next_steps
        )
    
    def _generate_architectural_guidance(
        self, 
        user_request: str, 
        project_context: Dict[str, Any], 
        mcp_data: Dict[str, Any]
    ) -> ArchitecturalGuidance:
        """Generate architectural decision guidance."""
        
        arch_data = mcp_data.get("architecture_validation", {})
        best_practices = mcp_data.get("best_practices", {})
        adk_info = mcp_data.get("adk_query", {})
        
        # Determine decision context
        decision_context = f"Architectural guidance for: {user_request}"
        
        # Generate recommended approach
        recommended_approach = "Component-based architecture with clear separation of concerns"
        if "recommended_approach" in arch_data:
            recommended_approach = arch_data["recommended_approach"]
        
        # Generate alternatives
        alternatives = [
            {
                "approach": "Monolithic Architecture",
                "description": "Single deployable unit with all functionality",
                "pros": ["Simple deployment", "Easy debugging"],
                "cons": ["Limited scalability", "Tight coupling"]
            },
            {
                "approach": "Microservices Architecture",
                "description": "Distributed services with independent deployment",
                "pros": ["High scalability", "Technology diversity"],
                "cons": ["Complex deployment", "Network overhead"]
            },
            {
                "approach": "Component-based Architecture (Recommended)",
                "description": "Modular components with clear interfaces",
                "pros": ["Good balance", "ADK-native", "Maintainable"],
                "cons": ["Initial complexity", "Interface design overhead"]
            }
        ]
        
        # Generate trade-offs
        trade_offs = {
            "Performance": ["Component overhead vs maintainability", "Network calls vs modularity"],
            "Scalability": ["Horizontal scaling vs complexity", "Resource utilization vs isolation"],
            "Maintainability": ["Code organization vs learning curve", "Testing complexity vs modularity"]
        }
        
        # Generate implementation guidance
        implementation_guidance = [
            "Start with core domain models and interfaces",
            "Implement components with clear boundaries",
            "Use dependency injection for loose coupling",
            "Follow ADK architectural patterns and conventions",
            "Implement proper error handling and logging"
        ]
        
        if "implementation_guidance" in best_practices:
            implementation_guidance.extend(best_practices["implementation_guidance"])
        
        # Generate validation criteria
        validation_criteria = [
            "Components have single responsibility",
            "Interfaces are well-defined and stable",
            "Dependencies flow in one direction",
            "Error handling is comprehensive",
            "Code follows ADK conventions"
        ]
        
        return ArchitecturalGuidance(
            decision_context=decision_context,
            recommended_approach=recommended_approach,
            alternatives=alternatives,
            trade_offs=trade_offs,
            implementation_guidance=implementation_guidance,
            validation_criteria=validation_criteria
        )
    
    def _generate_code_examples(
        self, 
        user_request: str, 
        project_context: Dict[str, Any], 
        mcp_data: Dict[str, Any]
    ) -> List[CodeExample]:
        """Generate code examples."""
        
        examples = []
        adk_info = mcp_data.get("adk_query", {})
        code_insights = mcp_data.get("code_insights", {})
        best_practices = mcp_data.get("best_practices", {})
        
        # Basic ADK component example
        examples.append(CodeExample(
            title="Basic ADK Component",
            description="A simple ADK component implementation",
            code='''use adk_core::{Component, ComponentContext, Result};

#[derive(Debug)]
pub struct MyComponent {
    name: String,
}

impl MyComponent {
    pub fn new(name: String) -> Self {
        Self { name }
    }
}

impl Component for MyComponent {
    fn initialize(&mut self, ctx: &ComponentContext) -> Result<()> {
        println!("Initializing component: {}", self.name);
        Ok(())
    }
    
    fn start(&mut self, ctx: &ComponentContext) -> Result<()> {
        println!("Starting component: {}", self.name);
        Ok(())
    }
    
    fn stop(&mut self, ctx: &ComponentContext) -> Result<()> {
        println!("Stopping component: {}", self.name);
        Ok(())
    }
}''',
            language="rust",
            explanation="This example shows the basic structure of an ADK component with lifecycle methods.",
            best_practices=[
                "Implement all lifecycle methods",
                "Use proper error handling with Result types",
                "Include meaningful logging and debugging information"
            ],
            related_patterns=["Component Lifecycle", "Dependency Injection", "Error Handling"]
        ))
        
        # Service implementation example
        examples.append(CodeExample(
            title="ADK Service Implementation",
            description="A service that handles business logic",
            code='''use adk_core::{Service, ServiceContext, Result};
use async_trait::async_trait;

pub struct UserService {
    repository: Box<dyn UserRepository>,
}

impl UserService {
    pub fn new(repository: Box<dyn UserRepository>) -> Self {
        Self { repository }
    }
}

#[async_trait]
impl Service for UserService {
    async fn handle_request(&self, request: ServiceRequest) -> Result<ServiceResponse> {
        match request.action.as_str() {
            "get_user" => {
                let user_id = request.params.get("id")
                    .ok_or_else(|| Error::MissingParameter("id"))?;
                
                let user = self.repository.find_by_id(user_id).await?;
                Ok(ServiceResponse::success(user))
            }
            _ => Err(Error::UnsupportedAction(request.action))
        }
    }
}''',
            language="rust",
            explanation="This example demonstrates a service implementation with async operations and error handling.",
            best_practices=[
                "Use async/await for I/O operations",
                "Implement proper error handling",
                "Use dependency injection for repositories",
                "Validate input parameters"
            ],
            related_patterns=["Service Pattern", "Repository Pattern", "Async Programming"]
        ))
        
        # Configuration example
        examples.append(CodeExample(
            title="ADK Configuration",
            description="Configuration setup for ADK applications",
            code='''[package]
name = "my-adk-app"
version = "0.1.0"
edition = "2021"

[dependencies]
adk-core = "0.1"
adk-runtime = "0.1"
adk-macros = "0.1"
tokio = { version = "1.0", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
tracing = "0.1"

[adk]
version = "0.1"
runtime = "tokio"
features = ["components", "services", "async"]

[adk.components]
auto_discovery = true
base_path = "src/components"

[adk.services]
auto_registration = true
base_path = "src/services"''',
            language="toml",
            explanation="This shows the recommended Cargo.toml configuration for ADK projects.",
            best_practices=[
                "Use specific ADK version constraints",
                "Enable required features only",
                "Configure auto-discovery for components",
                "Set up proper logging and tracing"
            ],
            related_patterns=["Configuration Management", "Dependency Management"]
        ))
        
        # Extract additional examples from MCP data
        if "examples" in adk_info:
            for example_data in adk_info["examples"]:
                examples.append(CodeExample(
                    title=example_data.get("title", "ADK Example"),
                    description=example_data.get("description", ""),
                    code=example_data.get("code", ""),
                    language=example_data.get("language", "rust"),
                    explanation=example_data.get("explanation", ""),
                    best_practices=example_data.get("best_practices", []),
                    related_patterns=example_data.get("related_patterns", [])
                ))
        
        return examples
    
    def _generate_troubleshooting_guidance(
        self, 
        user_request: str, 
        project_context: Dict[str, Any], 
        mcp_data: Dict[str, Any]
    ) -> TroubleshootingGuidance:
        """Generate troubleshooting guidance."""
        
        # Extract issue description from user request
        issue_description = user_request
        
        # Common ADK issues and solutions
        likely_causes = [
            "Missing or incorrect ADK dependencies",
            "Configuration file issues",
            "Component lifecycle problems",
            "Async/await usage errors",
            "Dependency injection configuration"
        ]
        
        diagnostic_steps = [
            "Check Cargo.toml for correct ADK dependencies",
            "Verify adk.toml configuration file",
            "Review component initialization order",
            "Check async runtime configuration",
            "Validate service registration"
        ]
        
        solutions = [
            {
                "issue": "Compilation Errors",
                "solution": "Update dependencies and check feature flags",
                "command": "cargo update && cargo check"
            },
            {
                "issue": "Runtime Errors",
                "solution": "Enable debug logging and check component lifecycle",
                "command": "RUST_LOG=debug cargo run"
            },
            {
                "issue": "Configuration Issues",
                "solution": "Validate configuration files and environment variables",
                "command": "cargo run -- --validate-config"
            }
        ]
        
        prevention_tips = [
            "Use cargo check regularly during development",
            "Implement comprehensive error handling",
            "Add unit tests for all components",
            "Use structured logging for debugging",
            "Follow ADK best practices and conventions"
        ]
        
        related_issues = [
            "Component initialization failures",
            "Service discovery problems",
            "Async runtime configuration",
            "Dependency resolution conflicts"
        ]
        
        # Extract additional troubleshooting info from MCP data
        code_insights = mcp_data.get("code_insights", {})
        if "common_issues" in code_insights:
            likely_causes.extend(code_insights["common_issues"])
        
        if "solutions" in code_insights:
            for solution in code_insights["solutions"]:
                solutions.append({
                    "issue": solution.get("issue", "Unknown Issue"),
                    "solution": solution.get("solution", ""),
                    "command": solution.get("command", "")
                })
        
        return TroubleshootingGuidance(
            issue_description=issue_description,
            likely_causes=likely_causes,
            diagnostic_steps=diagnostic_steps,
            solutions=solutions,
            prevention_tips=prevention_tips,
            related_issues=related_issues
        )
    
    def _generate_task_breakdown(
        self, 
        user_request: str, 
        project_context: Dict[str, Any], 
        mcp_data: Dict[str, Any]
    ) -> TaskBreakdown:
        """Generate task breakdown with step-by-step guidance."""
        
        # Determine complexity and time estimate
        complexity_level = "Medium"
        estimated_time = "2-4 hours"
        
        if any(word in user_request.lower() for word in ["simple", "basic", "quick"]):
            complexity_level = "Low"
            estimated_time = "30 minutes - 1 hour"
        elif any(word in user_request.lower() for word in ["complex", "advanced", "full"]):
            complexity_level = "High"
            estimated_time = "1-2 days"
        
        # Generate prerequisites
        prerequisites = [
            "ADK development environment set up",
            "Basic understanding of Rust and ADK concepts",
            "Project structure in place"
        ]
        
        # Generate detailed steps
        steps = [
            {
                "phase": "Planning",
                "step": "1. Analyze Requirements",
                "description": "Break down the task into smaller components",
                "estimated_time": "15-30 minutes",
                "deliverables": ["Requirements document", "Component list"]
            },
            {
                "phase": "Design",
                "step": "2. Design Architecture",
                "description": "Plan the component structure and interfaces",
                "estimated_time": "30-60 minutes",
                "deliverables": ["Architecture diagram", "Interface definitions"]
            },
            {
                "phase": "Implementation",
                "step": "3. Implement Core Logic",
                "description": "Write the main functionality",
                "estimated_time": "1-2 hours",
                "deliverables": ["Core implementation", "Unit tests"]
            },
            {
                "phase": "Integration",
                "step": "4. Integrate Components",
                "description": "Wire components together and test integration",
                "estimated_time": "30-60 minutes",
                "deliverables": ["Integrated system", "Integration tests"]
            },
            {
                "phase": "Validation",
                "step": "5. Test and Validate",
                "description": "Comprehensive testing and validation",
                "estimated_time": "30-45 minutes",
                "deliverables": ["Test results", "Validation report"]
            }
        ]
        
        # Generate validation points
        validation_points = [
            "Each component compiles without errors",
            "Unit tests pass for all components",
            "Integration tests validate component interaction",
            "Code follows ADK best practices",
            "Documentation is complete and accurate"
        ]
        
        # Generate success criteria
        success_criteria = [
            "All functionality works as specified",
            "Code quality meets project standards",
            "Performance requirements are met",
            "Error handling is comprehensive",
            "Documentation is complete"
        ]
        
        return TaskBreakdown(
            task_description=user_request,
            complexity_level=complexity_level,
            estimated_time=estimated_time,
            prerequisites=prerequisites,
            steps=steps,
            validation_points=validation_points,
            success_criteria=success_criteria
        )
    
    def _generate_general_guidance(
        self, 
        user_request: str, 
        project_context: Dict[str, Any], 
        mcp_data: Dict[str, Any]
    ) -> str:
        """Generate general guidance response."""
        
        adk_info = mcp_data.get("adk_query", {})
        best_practices = mcp_data.get("best_practices", {})
        
        guidance = f"## ADK Project Guidance\n\n"
        guidance += f"**Your Request**: {user_request}\n\n"
        
        # Add information from ADK query
        if "answer" in adk_info:
            guidance += f"**ADK Documentation Response**:\n{adk_info['answer']}\n\n"
        
        # Add best practices
        if "recommendations" in best_practices:
            guidance += "**Best Practices**:\n"
            for practice in best_practices["recommendations"]:
                guidance += f"- {practice}\n"
            guidance += "\n"
        
        # Add general ADK guidance
        guidance += "**General ADK Development Tips**:\n"
        guidance += "- Follow component-based architecture patterns\n"
        guidance += "- Use proper error handling with Result types\n"
        guidance += "- Implement comprehensive logging and monitoring\n"
        guidance += "- Write unit and integration tests\n"
        guidance += "- Follow ADK naming conventions and best practices\n\n"
        
        guidance += "**Next Steps**:\n"
        guidance += "- Review the official ADK documentation\n"
        guidance += "- Start with a simple component implementation\n"
        guidance += "- Gradually add complexity as you learn\n"
        guidance += "- Join the ADK developer community for support\n"
        
        return guidance
    
    async def _compile_assistance_result(
        self,
        assistance_type: AssistanceType,
        user_request: str,
        primary_guidance: Union[ProjectSetupGuidance, ArchitecturalGuidance, List[CodeExample], 
                               TroubleshootingGuidance, TaskBreakdown, str],
        mcp_data: Dict[str, Any]
    ) -> ProjectAssistanceResult:
        """Compile comprehensive assistance result."""
        
        # Create summary
        summary = f"Comprehensive {assistance_type.value.replace('_', ' ').title()} guidance for: {user_request}"
        
        # Collect additional resources
        additional_resources = [
            "Official Google ADK Documentation",
            "ADK Best Practices Guide",
            "ADK Community Forums",
            "ADK GitHub Repository"
        ]
        
        # Extract resources from MCP data
        for data in mcp_data.values():
            if isinstance(data, dict) and "resources" in data:
                additional_resources.extend(data["resources"])
        
        # Collect best practices
        best_practices = [
            "Follow ADK architectural patterns",
            "Implement proper error handling",
            "Use structured logging and monitoring",
            "Write comprehensive tests",
            "Document your code and APIs"
        ]
        
        # Extract best practices from MCP data
        for data in mcp_data.values():
            if isinstance(data, dict) and "best_practices" in data:
                if isinstance(data["best_practices"], list):
                    best_practices.extend(data["best_practices"])
        
        # Collect references
        references = [
            "Google ADK Official Documentation",
            "ADK Rust API Reference",
            "ADK Architecture Guide"
        ]
        
        # Extract references from MCP data
        for data in mcp_data.values():
            if isinstance(data, dict) and "references" in data:
                references.extend(data["references"])
        
        # Generate follow-up suggestions
        follow_up_suggestions = [
            "Review the provided guidance and examples",
            "Start with a simple implementation",
            "Test your implementation thoroughly",
            "Seek feedback from the ADK community",
            "Iterate and improve based on experience"
        ]
        
        # Customize follow-up based on assistance type
        if assistance_type == AssistanceType.PROJECT_SETUP:
            follow_up_suggestions.extend([
                "Set up your development environment",
                "Create a simple 'Hello World' ADK application",
                "Explore ADK component examples"
            ])
        elif assistance_type == AssistanceType.CODE_EXAMPLES:
            follow_up_suggestions.extend([
                "Try implementing the provided examples",
                "Modify examples to fit your use case",
                "Create your own variations"
            ])
        
        return ProjectAssistanceResult(
            assistance_type=assistance_type,
            summary=summary,
            primary_guidance=primary_guidance,
            additional_resources=list(set(additional_resources)),  # Remove duplicates
            best_practices=list(set(best_practices)),  # Remove duplicates
            references=list(set(references)),  # Remove duplicates
            follow_up_suggestions=follow_up_suggestions
        )
    
    async def _fallback_assistance(
        self, 
        user_request: str, 
        project_context: Dict[str, Any], 
        error_msg: str
    ) -> ProjectAssistanceResult:
        """Provide fallback assistance when MCP tools are unavailable."""
        
        # Determine the intended assistance type even in fallback mode
        intended_type = self._determine_assistance_type(user_request, project_context)
        
        fallback_guidance = f"""
# Fallback ADK Project Assistance

**Your Request**: {user_request}

**Notice**: The MCP server is currently unavailable ({error_msg}). Providing basic guidance based on general ADK knowledge.

## General ADK Guidance

### Getting Started
1. **Set up Rust Development Environment**
   - Install Rust toolchain (rustup)
   - Set up your IDE with Rust support
   - Install ADK CLI tools if available

2. **Create ADK Project**
   ```bash
   cargo new my-adk-project
   cd my-adk-project
   ```

3. **Add ADK Dependencies**
   ```toml
   [dependencies]
   adk-core = "0.1"
   adk-runtime = "0.1"
   tokio = {{ version = "1.0", features = ["full"] }}
   ```

### Basic ADK Patterns
- **Components**: Implement the Component trait for reusable functionality
- **Services**: Use the Service trait for business logic
- **Configuration**: Use adk.toml for ADK-specific settings
- **Error Handling**: Always use Result types for error handling

### Best Practices
- Follow Rust naming conventions
- Implement proper error handling
- Use async/await for I/O operations
- Write unit and integration tests
- Document your public APIs

### Next Steps
- Review official ADK documentation when MCP server is available
- Start with simple component implementations
- Join the ADK developer community
- Practice with example projects

**Recommendation**: Retry your request when the MCP server is available for comprehensive, up-to-date guidance.
"""
        
        return ProjectAssistanceResult(
            assistance_type=intended_type,  # Use the intended type, not always GENERAL_GUIDANCE
            summary=f"Fallback guidance for: {user_request} (MCP server unavailable)",
            primary_guidance=fallback_guidance,
            additional_resources=[
                "Official Google ADK Documentation (when available)",
                "Rust Programming Language Book",
                "Tokio Async Runtime Documentation"
            ],
            best_practices=[
                "Use proper error handling",
                "Follow Rust conventions",
                "Implement comprehensive testing",
                "Document your code"
            ],
            references=[
                "Manual ADK documentation review recommended",
                "Community forums and resources"
            ],
            follow_up_suggestions=[
                "Retry when MCP server is available",
                "Start with basic Rust ADK examples",
                "Review official documentation"
            ]
        )
    
    # Helper methods
    
    def _enhance_query_for_type(self, user_request: str, assistance_type: AssistanceType) -> str:
        """Enhance the user query based on assistance type."""
        
        enhancements = {
            AssistanceType.PROJECT_SETUP: "project setup, initialization, configuration, dependencies",
            AssistanceType.ARCHITECTURE_GUIDANCE: "architecture, design patterns, component organization, best practices",
            AssistanceType.CODE_EXAMPLES: "code examples, implementation patterns, sample code, tutorials",
            AssistanceType.TROUBLESHOOTING: "troubleshooting, error resolution, debugging, common issues",
            AssistanceType.TASK_BREAKDOWN: "step-by-step guide, implementation plan, task breakdown, roadmap",
            AssistanceType.GENERAL_GUIDANCE: "general guidance, best practices, recommendations"
        }
        
        enhancement = enhancements.get(assistance_type, "")
        return f"{user_request} - Focus on: {enhancement}"
    
    def _determine_best_practices_scenario(self, assistance_type: AssistanceType, user_request: str) -> str:
        """Determine the best practices scenario based on assistance type."""
        
        scenarios = {
            AssistanceType.PROJECT_SETUP: "project_initialization",
            AssistanceType.ARCHITECTURE_GUIDANCE: "architectural_design",
            AssistanceType.CODE_EXAMPLES: "implementation_patterns",
            AssistanceType.TROUBLESHOOTING: "error_handling",
            AssistanceType.TASK_BREAKDOWN: "development_process",
            AssistanceType.GENERAL_GUIDANCE: "general_development"
        }
        
        return scenarios.get(assistance_type, "general_development")
    
    def _create_sample_content_for_validation(self, user_request: str, project_context: Dict[str, Any]) -> str:
        """Create sample content for architectural validation."""
        
        return f"""
// Sample ADK project structure for validation
// Request: {user_request}

use adk_core::{{Component, Service, Result}};

pub struct SampleComponent {{
    name: String,
}}

impl Component for SampleComponent {{
    fn initialize(&mut self, ctx: &ComponentContext) -> Result<()> {{
        // Initialization logic
        Ok(())
    }}
}}

pub struct SampleService {{
    component: SampleComponent,
}}

impl Service for SampleService {{
    async fn handle_request(&self, request: ServiceRequest) -> Result<ServiceResponse> {{
        // Service logic
        Ok(ServiceResponse::success(()))
    }}
}}
"""
    
    def _create_sample_code_for_analysis(self, user_request: str, project_context: Dict[str, Any]) -> str:
        """Create sample code for analysis."""
        
        return f"""
// Sample ADK code for analysis
// Request: {user_request}

use adk_core::{{Component, Result, Error}};

pub struct ExampleComponent {{
    initialized: bool,
}}

impl ExampleComponent {{
    pub fn new() -> Self {{
        Self {{ initialized: false }}
    }}
}}

impl Component for ExampleComponent {{
    fn initialize(&mut self, _ctx: &ComponentContext) -> Result<()> {{
        self.initialized = true;
        println!("Component initialized");
        Ok(())
    }}
    
    fn start(&mut self, _ctx: &ComponentContext) -> Result<()> {{
        if !self.initialized {{
            return Err(Error::NotInitialized);
        }}
        println!("Component started");
        Ok(())
    }}
}}
"""


def format_project_assistance_result(result: ProjectAssistanceResult) -> str:
    """Format the project assistance result as markdown for display."""
    
    output = []
    output.append("# ADK Project Assistant Results\n")
    
    # Summary
    output.append("## Summary")
    output.append(result.summary)
    output.append(f"\n**Assistance Type**: {result.assistance_type.value.replace('_', ' ').title()}\n")
    
    # Primary Guidance (format based on type)
    output.append("## Primary Guidance\n")
    
    if isinstance(result.primary_guidance, ProjectSetupGuidance):
        output.extend(_format_project_setup_guidance(result.primary_guidance))
    elif isinstance(result.primary_guidance, ArchitecturalGuidance):
        output.extend(_format_architectural_guidance(result.primary_guidance))
    elif isinstance(result.primary_guidance, list) and result.primary_guidance and isinstance(result.primary_guidance[0], CodeExample):
        output.extend(_format_code_examples(result.primary_guidance))
    elif isinstance(result.primary_guidance, TroubleshootingGuidance):
        output.extend(_format_troubleshooting_guidance(result.primary_guidance))
    elif isinstance(result.primary_guidance, TaskBreakdown):
        output.extend(_format_task_breakdown(result.primary_guidance))
    else:
        output.append(str(result.primary_guidance))
    
    output.append("")
    
    # Best Practices
    if result.best_practices:
        output.append("## Best Practices")
        for practice in result.best_practices:
            output.append(f"- {practice}")
        output.append("")
    
    # Additional Resources
    if result.additional_resources:
        output.append("## Additional Resources")
        for resource in result.additional_resources:
            output.append(f"- {resource}")
        output.append("")
    
    # Follow-up Suggestions
    if result.follow_up_suggestions:
        output.append("## Follow-up Suggestions")
        for i, suggestion in enumerate(result.follow_up_suggestions, 1):
            output.append(f"{i}. {suggestion}")
        output.append("")
    
    # References
    if result.references:
        output.append("## References")
        for ref in result.references:
            if ref.startswith("http"):
                output.append(f"- [{ref}]({ref})")
            else:
                output.append(f"- {ref}")
    
    return "\n".join(output)


def _format_project_setup_guidance(guidance: ProjectSetupGuidance) -> List[str]:
    """Format project setup guidance."""
    output = []
    
    output.append(f"### {guidance.setup_type} Setup")
    output.append("")
    
    # Prerequisites
    output.append("**Prerequisites:**")
    for prereq in guidance.prerequisites:
        output.append(f"- {prereq}")
    output.append("")
    
    # Setup Steps
    output.append("**Setup Steps:**")
    for step in guidance.steps:
        output.append(f"**{step['step']}**")
        output.append(f"- Description: {step['description']}")
        if step['command']:
            output.append(f"- Command: `{step['command']}`")
        output.append("")
    
    # Configuration Files
    if guidance.configuration_files:
        output.append("**Configuration Files:**")
        for config in guidance.configuration_files:
            output.append(f"- **{config['file']}**: {config['purpose']}")
        output.append("")
    
    # Validation Steps
    output.append("**Validation Steps:**")
    for validation in guidance.validation_steps:
        output.append(f"- {validation}")
    output.append("")
    
    # Next Steps
    output.append("**Next Steps:**")
    for next_step in guidance.next_steps:
        output.append(f"- {next_step}")
    
    return output


def _format_architectural_guidance(guidance: ArchitecturalGuidance) -> List[str]:
    """Format architectural guidance."""
    output = []
    
    output.append("### Architectural Decision Guidance")
    output.append("")
    output.append(f"**Context**: {guidance.decision_context}")
    output.append("")
    output.append(f"**Recommended Approach**: {guidance.recommended_approach}")
    output.append("")
    
    # Alternatives
    output.append("**Alternative Approaches:**")
    for alt in guidance.alternatives:
        output.append(f"- **{alt['approach']}**: {alt['description']}")
        if 'pros' in alt:
            output.append(f"  - Pros: {', '.join(alt['pros'])}")
        if 'cons' in alt:
            output.append(f"  - Cons: {', '.join(alt['cons'])}")
    output.append("")
    
    # Trade-offs
    output.append("**Trade-offs:**")
    for category, trade_offs in guidance.trade_offs.items():
        output.append(f"- **{category}**: {', '.join(trade_offs)}")
    output.append("")
    
    # Implementation Guidance
    output.append("**Implementation Guidance:**")
    for impl_guide in guidance.implementation_guidance:
        output.append(f"- {impl_guide}")
    output.append("")
    
    # Validation Criteria
    output.append("**Validation Criteria:**")
    for criteria in guidance.validation_criteria:
        output.append(f"- {criteria}")
    
    return output


def _format_code_examples(examples: List[CodeExample]) -> List[str]:
    """Format code examples."""
    output = []
    
    for i, example in enumerate(examples, 1):
        output.append(f"### Example {i}: {example.title}")
        output.append("")
        output.append(example.description)
        output.append("")
        output.append(f"```{example.language}")
        output.append(example.code)
        output.append("```")
        output.append("")
        
        if example.explanation:
            output.append(f"**Explanation**: {example.explanation}")
            output.append("")
        
        if example.best_practices:
            output.append("**Best Practices:**")
            for practice in example.best_practices:
                output.append(f"- {practice}")
            output.append("")
        
        if example.related_patterns:
            output.append(f"**Related Patterns**: {', '.join(example.related_patterns)}")
            output.append("")
    
    return output


def _format_troubleshooting_guidance(guidance: TroubleshootingGuidance) -> List[str]:
    """Format troubleshooting guidance."""
    output = []
    
    output.append("### Troubleshooting Guidance")
    output.append("")
    output.append(f"**Issue**: {guidance.issue_description}")
    output.append("")
    
    # Likely Causes
    output.append("**Likely Causes:**")
    for cause in guidance.likely_causes:
        output.append(f"- {cause}")
    output.append("")
    
    # Diagnostic Steps
    output.append("**Diagnostic Steps:**")
    for i, step in enumerate(guidance.diagnostic_steps, 1):
        output.append(f"{i}. {step}")
    output.append("")
    
    # Solutions
    output.append("**Solutions:**")
    for solution in guidance.solutions:
        output.append(f"- **{solution['issue']}**: {solution['solution']}")
        if solution['command']:
            output.append(f"  - Command: `{solution['command']}`")
    output.append("")
    
    # Prevention Tips
    output.append("**Prevention Tips:**")
    for tip in guidance.prevention_tips:
        output.append(f"- {tip}")
    output.append("")
    
    # Related Issues
    if guidance.related_issues:
        output.append("**Related Issues:**")
        for issue in guidance.related_issues:
            output.append(f"- {issue}")
    
    return output


def _format_task_breakdown(breakdown: TaskBreakdown) -> List[str]:
    """Format task breakdown."""
    output = []
    
    output.append("### Task Breakdown")
    output.append("")
    output.append(f"**Task**: {breakdown.task_description}")
    output.append(f"**Complexity**: {breakdown.complexity_level}")
    output.append(f"**Estimated Time**: {breakdown.estimated_time}")
    output.append("")
    
    # Prerequisites
    output.append("**Prerequisites:**")
    for prereq in breakdown.prerequisites:
        output.append(f"- {prereq}")
    output.append("")
    
    # Steps
    output.append("**Implementation Steps:**")
    for step in breakdown.steps:
        output.append(f"**{step['step']}** ({step.get('phase', 'Implementation')})")
        output.append(f"- {step['description']}")
        if 'estimated_time' in step:
            output.append(f"- Time: {step['estimated_time']}")
        if 'deliverables' in step:
            output.append(f"- Deliverables: {', '.join(step['deliverables'])}")
        output.append("")
    
    # Validation Points
    output.append("**Validation Points:**")
    for point in breakdown.validation_points:
        output.append(f"- {point}")
    output.append("")
    
    # Success Criteria
    output.append("**Success Criteria:**")
    for criteria in breakdown.success_criteria:
        output.append(f"- {criteria}")
    
    return output


# Example usage and testing
async def main():
    """Example usage of the ADK Project Assistant Agent."""
    
    # Mock MCP client for testing
    class MockMCPClient:
        async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]):
            # Mock responses for different tools
            if tool_name == "adk_query":
                return {
                    "answer": "ADK components are the building blocks of ADK applications...",
                    "examples": [
                        {
                            "title": "Basic Component",
                            "code": "impl Component for MyComponent { ... }",
                            "description": "A simple component implementation"
                        }
                    ],
                    "best_practices": ["Use proper error handling", "Implement lifecycle methods"],
                    "references": ["ADK Component Guide"]
                }
            elif tool_name == "get_best_practices":
                return {
                    "recommendations": [
                        "Follow component-based architecture",
                        "Use dependency injection",
                        "Implement proper error handling"
                    ],
                    "references": ["ADK Best Practices Guide"]
                }
            elif tool_name == "validate_architecture":
                return {
                    "recommended_approach": "Component-based architecture with clear interfaces",
                    "findings": [],
                    "references": ["ADK Architecture Guide"]
                }
            elif tool_name == "review_rust_file":
                return {
                    "findings": [],
                    "best_practices": {"error_handling": True, "async_usage": True},
                    "references": ["Rust ADK Patterns"]
                }
            
            return {"error": "Unknown tool"}
    
    # Test the agent
    agent = ADKProjectAssistantAgent(MockMCPClient())
    
    # Test different assistance types
    test_requests = [
        ("How do I set up a new ADK project?", AssistanceType.PROJECT_SETUP),
        ("What's the best architecture for my ADK service?", AssistanceType.ARCHITECTURE_GUIDANCE),
        ("Show me how to implement an ADK component", AssistanceType.CODE_EXAMPLES),
        ("My ADK app won't compile, help!", AssistanceType.TROUBLESHOOTING),
        ("Break down the task of building a user service", AssistanceType.TASK_BREAKDOWN)
    ]
    
    for request, assistance_type in test_requests:
        print(f"\n{'='*60}")
        print(f"Testing: {request}")
        print(f"Type: {assistance_type.value}")
        print('='*60)
        
        result = await agent.provide_assistance(request, {}, assistance_type)
        formatted_output = format_project_assistance_result(result)
        print(formatted_output)


if __name__ == "__main__":
    asyncio.run(main())