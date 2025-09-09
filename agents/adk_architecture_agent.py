#!/usr/bin/env python3
"""
ADK Architecture Agent Implementation

This agent provides architectural validation for Google ADK projects using the
arkaft-mcp-google-adk MCP server tools.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class Priority(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class ArchitecturalFinding:
    """Represents a single architectural validation finding."""
    priority: Priority
    component_name: str
    location: str
    current_state: str
    adk_compliance: str
    issues_identified: str
    recommendations: str
    impact: str
    example: Optional[str] = None


@dataclass
class DependencyAnalysis:
    """Analysis of project dependencies."""
    compliant_dependencies: List[str]
    version_issues: List[str]
    missing_dependencies: List[str]
    recommendations: List[str]


@dataclass
class PatternCompliance:
    """ADK pattern compliance assessment."""
    compliant_patterns: List[str]
    non_compliant_patterns: List[str]
    missing_patterns: List[str]
    recommendations: List[str]


@dataclass
class ArchitecturalValidationResult:
    """Complete architectural validation result."""
    summary: str
    compliance_level: str
    findings: List[ArchitecturalFinding]
    dependency_analysis: DependencyAnalysis
    pattern_compliance: PatternCompliance
    coordination_notes: List[str]
    references: List[str]


class ADKArchitectureAgent:
    """
    ADK Architecture Agent that uses MCP tools to validate architectural patterns
    and component organization for ADK compliance.
    """
    
    def __init__(self, mcp_client):
        """Initialize the agent with MCP client."""
        self.mcp_client = mcp_client
        self.mcp_server_name = "arkaft-google-adk"
        self.coordination_context = {}
        
    async def validate_architecture(
        self, 
        file_path: str, 
        file_content: str, 
        project_context: Dict[str, Any]
    ) -> ArchitecturalValidationResult:
        """
        Main entry point for architectural validation.
        
        Args:
            file_path: Path to the file being validated
            file_content: Content of the file
            project_context: Additional project context
            
        Returns:
            ArchitecturalValidationResult with comprehensive analysis
        """
        try:
            # Step 1: Determine validation scope based on file type
            validation_scope = self._determine_validation_scope(file_path, file_content)
            
            # Step 2: Primary architectural validation
            architectural_analysis = await self._validate_with_architecture_tool(
                file_content, file_path, validation_scope, project_context
            )
            
            # Step 3: Get best practices for architectural scenarios
            best_practices = await self._get_architectural_best_practices(
                file_path, validation_scope, architectural_analysis
            )
            
            # Step 4: Analyze dependencies if relevant
            dependency_analysis = await self._analyze_dependencies_if_needed(
                file_path, file_content, project_context
            )
            
            # Step 5: Query ADK-specific architectural guidance
            adk_guidance = await self._get_adk_architectural_guidance(
                validation_scope, architectural_analysis
            )
            
            # Step 6: Compile comprehensive validation result
            return await self._compile_validation_result(
                file_path, architectural_analysis, best_practices, 
                dependency_analysis, adk_guidance, validation_scope
            )
            
        except Exception as e:
            # Graceful degradation on MCP failures
            return await self._fallback_validation(file_path, file_content, str(e))
    
    def _determine_validation_scope(self, file_path: str, file_content: str) -> Dict[str, Any]:
        """Determine what aspects of architecture to validate based on file type."""
        scope = {
            "file_type": self._get_architectural_file_type(file_path),
            "validation_areas": [],
            "priority_focus": []
        }
        
        if file_path.endswith("lib.rs"):
            scope["validation_areas"] = [
                "public_api_design", "module_organization", "component_interfaces"
            ]
            scope["priority_focus"] = ["api_design", "encapsulation"]
            
        elif file_path.endswith("main.rs"):
            scope["validation_areas"] = [
                "application_structure", "initialization_patterns", "dependency_injection"
            ]
            scope["priority_focus"] = ["startup_sequence", "configuration"]
            
        elif file_path.endswith("mod.rs"):
            scope["validation_areas"] = [
                "module_interfaces", "component_boundaries", "encapsulation"
            ]
            scope["priority_focus"] = ["interface_design", "abstraction"]
            
        elif file_path.endswith("Cargo.toml"):
            scope["validation_areas"] = [
                "dependency_management", "feature_organization", "version_compatibility"
            ]
            scope["priority_focus"] = ["dependencies", "features"]
            
        elif any(config in file_path for config in ["adk.toml", "adk-config.json"]):
            scope["validation_areas"] = [
                "configuration_management", "adk_compliance", "environment_handling"
            ]
            scope["priority_focus"] = ["configuration", "compliance"]
            
        else:
            scope["validation_areas"] = [
                "component_design", "architectural_patterns"
            ]
            scope["priority_focus"] = ["patterns", "organization"]
        
        return scope
    
    async def _validate_with_architecture_tool(
        self, 
        file_content: str, 
        file_path: str, 
        validation_scope: Dict[str, Any],
        project_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use validate_architecture MCP tool for primary validation."""
        try:
            result = await self.mcp_client.call_tool(
                server_name=self.mcp_server_name,
                tool_name="validate_architecture",
                arguments={
                    "file_content": file_content,
                    "file_path": file_path,
                    "validation_focus": validation_scope["validation_areas"],
                    "priority_areas": validation_scope["priority_focus"],
                    "project_context": project_context,
                    "check_patterns": [
                        "component_organization",
                        "dependency_management", 
                        "separation_of_concerns",
                        "adk_patterns",
                        "interface_design"
                    ]
                }
            )
            return result
        except Exception as e:
            print(f"Warning: validate_architecture MCP tool failed: {e}")
            return {"error": str(e), "fallback": True}
    
    async def _get_architectural_best_practices(
        self, 
        file_path: str, 
        validation_scope: Dict[str, Any],
        architectural_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get architectural best practices using get_best_practices MCP tool."""
        try:
            scenario = self._determine_architectural_scenario(file_path, validation_scope)
            
            result = await self.mcp_client.call_tool(
                server_name=self.mcp_server_name,
                tool_name="get_best_practices",
                arguments={
                    "scenario": scenario,
                    "context": {
                        "architectural_focus": True,
                        "file_type": validation_scope["file_type"],
                        "validation_areas": validation_scope["validation_areas"],
                        "current_patterns": architectural_analysis.get("detected_patterns", [])
                    }
                }
            )
            return result
        except Exception as e:
            print(f"Warning: get_best_practices MCP tool failed: {e}")
            return {"error": str(e)}
    
    async def _analyze_dependencies_if_needed(
        self, 
        file_path: str, 
        file_content: str, 
        project_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Analyze dependencies if the file affects dependency management."""
        
        if not (file_path.endswith("Cargo.toml") or "dependencies" in file_content.lower()):
            return None
            
        try:
            # Use validate_architecture with dependency focus
            result = await self.mcp_client.call_tool(
                server_name=self.mcp_server_name,
                tool_name="validate_architecture",
                arguments={
                    "file_content": file_content,
                    "file_path": file_path,
                    "validation_focus": ["dependency_analysis"],
                    "check_patterns": [
                        "dependency_management",
                        "version_compatibility",
                        "circular_dependencies",
                        "adk_dependency_patterns"
                    ]
                }
            )
            return result
        except Exception as e:
            print(f"Warning: dependency analysis failed: {e}")
            return None
    
    async def _get_adk_architectural_guidance(
        self, 
        validation_scope: Dict[str, Any],
        architectural_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get ADK-specific architectural guidance using adk_query MCP tool."""
        try:
            # Determine what ADK guidance to request based on findings
            query_topics = []
            
            if "component_organization" in validation_scope["validation_areas"]:
                query_topics.append("component architecture patterns")
            if "dependency_management" in validation_scope["validation_areas"]:
                query_topics.append("dependency injection best practices")
            if "configuration_management" in validation_scope["validation_areas"]:
                query_topics.append("configuration management patterns")
            
            # Add topics based on detected issues
            if "issues" in architectural_analysis:
                for issue in architectural_analysis["issues"]:
                    if "dependency" in issue.lower():
                        query_topics.append("dependency management troubleshooting")
                    if "component" in issue.lower():
                        query_topics.append("component design patterns")
            
            if not query_topics:
                query_topics = ["general architecture best practices"]
            
            result = await self.mcp_client.call_tool(
                server_name=self.mcp_server_name,
                tool_name="adk_query",
                arguments={
                    "query": f"ADK architectural guidance for: {', '.join(query_topics)}",
                    "context": {
                        "architectural_focus": True,
                        "validation_scope": validation_scope
                    }
                }
            )
            return result
        except Exception as e:
            print(f"Warning: adk_query MCP tool failed: {e}")
            return {"error": str(e)}
    
    async def _compile_validation_result(
        self,
        file_path: str,
        architectural_analysis: Dict[str, Any],
        best_practices: Dict[str, Any],
        dependency_analysis: Optional[Dict[str, Any]],
        adk_guidance: Dict[str, Any],
        validation_scope: Dict[str, Any]
    ) -> ArchitecturalValidationResult:
        """Compile all analysis results into a comprehensive validation result."""
        
        findings = []
        
        # Process architectural findings
        if "findings" in architectural_analysis:
            for finding in architectural_analysis["findings"]:
                findings.append(self._create_architectural_finding(finding))
        
        # Process dependency findings if available
        if dependency_analysis and "findings" in dependency_analysis:
            for finding in dependency_analysis["findings"]:
                findings.append(self._create_dependency_finding(finding))
        
        # Determine compliance level
        compliance_level = self._determine_compliance_level(findings, architectural_analysis)
        
        # Create summary
        summary = self._create_architectural_summary(file_path, findings, compliance_level)
        
        # Analyze dependencies
        dep_analysis = self._extract_dependency_analysis(
            architectural_analysis, dependency_analysis
        )
        
        # Extract pattern compliance
        pattern_compliance = self._extract_pattern_compliance(
            architectural_analysis, best_practices, adk_guidance
        )
        
        # Generate coordination notes
        coordination_notes = self._generate_coordination_notes(
            findings, validation_scope, architectural_analysis
        )
        
        # Collect references
        references = self._collect_architectural_references(
            architectural_analysis, best_practices, adk_guidance
        )
        
        return ArchitecturalValidationResult(
            summary=summary,
            compliance_level=compliance_level,
            findings=findings,
            dependency_analysis=dep_analysis,
            pattern_compliance=pattern_compliance,
            coordination_notes=coordination_notes,
            references=references
        )
    
    async def _fallback_validation(
        self, 
        file_path: str, 
        file_content: str, 
        error_msg: str
    ) -> ArchitecturalValidationResult:
        """Provide basic architectural validation when MCP tools are unavailable."""
        
        findings = []
        
        # Basic static analysis for common architectural issues
        if file_path.endswith("lib.rs"):
            if "pub mod" not in file_content:
                findings.append(ArchitecturalFinding(
                    priority=Priority.MEDIUM,
                    component_name="Module Organization",
                    location="lib.rs structure",
                    current_state="No public modules declared",
                    adk_compliance="Partially compliant - may need module organization",
                    issues_identified="Library structure unclear without module declarations",
                    recommendations="Consider organizing code into logical modules with clear public interfaces",
                    impact="Affects code organization and maintainability"
                ))
        
        if file_path.endswith("Cargo.toml"):
            if "google-adk" not in file_content and "adk-" not in file_content:
                findings.append(ArchitecturalFinding(
                    priority=Priority.HIGH,
                    component_name="ADK Dependencies",
                    location="Cargo.toml dependencies",
                    current_state="No ADK dependencies detected",
                    adk_compliance="Non-compliant - missing ADK dependencies",
                    issues_identified="Project may not be properly configured for ADK usage",
                    recommendations="Add appropriate ADK dependencies to Cargo.toml",
                    impact="Critical for ADK functionality and compliance"
                ))
        
        return ArchitecturalValidationResult(
            summary=f"Fallback architectural validation for {file_path} (MCP server unavailable: {error_msg})",
            compliance_level="Unknown - Limited Analysis",
            findings=findings,
            dependency_analysis=DependencyAnalysis([], [], [], ["Retry when MCP server is available"]),
            pattern_compliance=PatternCompliance([], [], [], ["Manual validation recommended"]),
            coordination_notes=["MCP server unavailable - limited validation performed"],
            references=["Manual ADK architecture documentation review recommended"]
        )
    
    def _create_architectural_finding(self, finding_data: Dict[str, Any]) -> ArchitecturalFinding:
        """Convert MCP architectural analysis result to ArchitecturalFinding."""
        return ArchitecturalFinding(
            priority=Priority(finding_data.get("priority", "Medium")),
            component_name=finding_data.get("component", "Architectural Component"),
            location=finding_data.get("location", "Unknown"),
            current_state=finding_data.get("current_state", ""),
            adk_compliance=finding_data.get("adk_compliance", ""),
            issues_identified=finding_data.get("issues", ""),
            recommendations=finding_data.get("recommendations", ""),
            impact=finding_data.get("impact", ""),
            example=finding_data.get("example")
        )
    
    def _create_dependency_finding(self, finding_data: Dict[str, Any]) -> ArchitecturalFinding:
        """Convert dependency analysis result to ArchitecturalFinding."""
        return ArchitecturalFinding(
            priority=Priority(finding_data.get("priority", "Medium")),
            component_name=f"Dependency: {finding_data.get('dependency', 'Unknown')}",
            location=finding_data.get("location", "Cargo.toml"),
            current_state=finding_data.get("current_state", ""),
            adk_compliance=finding_data.get("adk_compliance", "Affects dependency compliance"),
            issues_identified=finding_data.get("issues", ""),
            recommendations=finding_data.get("recommendations", ""),
            impact=finding_data.get("impact", "Affects project dependencies"),
            example=finding_data.get("example")
        )
    
    def _determine_compliance_level(
        self, 
        findings: List[ArchitecturalFinding], 
        analysis: Dict[str, Any]
    ) -> str:
        """Determine overall compliance level based on findings."""
        
        if any(f.priority == Priority.CRITICAL for f in findings):
            return "Non-Compliant - Critical Issues"
        elif any(f.priority == Priority.HIGH for f in findings):
            return "Partially Compliant - High Priority Issues"
        elif any(f.priority == Priority.MEDIUM for f in findings):
            return "Good - Minor Improvements Recommended"
        elif len(findings) == 0:
            return "Excellent - Fully Compliant"
        else:
            return "Good - Low Priority Improvements Available"
    
    def _create_architectural_summary(
        self, 
        file_path: str, 
        findings: List[ArchitecturalFinding], 
        compliance_level: str
    ) -> str:
        """Create a summary of the architectural validation results."""
        file_name = file_path.split('/')[-1]
        finding_count = len(findings)
        
        if finding_count == 0:
            return f"Validated architectural changes in `{file_name}` - Excellent compliance with ADK patterns and best practices."
        
        return f"Validated architectural changes in `{file_name}` - {finding_count} finding(s) identified. {compliance_level}."
    
    def _extract_dependency_analysis(
        self, 
        architectural_analysis: Dict[str, Any],
        dependency_analysis: Optional[Dict[str, Any]]
    ) -> DependencyAnalysis:
        """Extract dependency analysis from MCP results."""
        
        compliant = []
        issues = []
        missing = []
        recommendations = []
        
        # Extract from architectural analysis
        if "dependencies" in architectural_analysis:
            dep_data = architectural_analysis["dependencies"]
            compliant.extend(dep_data.get("compliant", []))
            issues.extend(dep_data.get("issues", []))
            missing.extend(dep_data.get("missing", []))
            recommendations.extend(dep_data.get("recommendations", []))
        
        # Extract from dedicated dependency analysis
        if dependency_analysis:
            compliant.extend(dependency_analysis.get("compliant_dependencies", []))
            issues.extend(dependency_analysis.get("version_issues", []))
            missing.extend(dependency_analysis.get("missing_dependencies", []))
            recommendations.extend(dependency_analysis.get("recommendations", []))
        
        return DependencyAnalysis(compliant, issues, missing, recommendations)
    
    def _extract_pattern_compliance(
        self,
        architectural_analysis: Dict[str, Any],
        best_practices: Dict[str, Any],
        adk_guidance: Dict[str, Any]
    ) -> PatternCompliance:
        """Extract pattern compliance information from all analyses."""
        
        compliant = []
        non_compliant = []
        missing = []
        recommendations = []
        
        # Extract from architectural analysis
        if "patterns" in architectural_analysis:
            pattern_data = architectural_analysis["patterns"]
            compliant.extend(pattern_data.get("compliant", []))
            non_compliant.extend(pattern_data.get("non_compliant", []))
            missing.extend(pattern_data.get("missing", []))
        
        # Extract from best practices
        if "pattern_compliance" in best_practices:
            bp_patterns = best_practices["pattern_compliance"]
            compliant.extend(bp_patterns.get("followed", []))
            non_compliant.extend(bp_patterns.get("violated", []))
            recommendations.extend(bp_patterns.get("recommendations", []))
        
        # Extract from ADK guidance
        if "recommended_patterns" in adk_guidance:
            missing.extend(adk_guidance["recommended_patterns"])
        
        return PatternCompliance(compliant, non_compliant, missing, recommendations)
    
    def _generate_coordination_notes(
        self,
        findings: List[ArchitecturalFinding],
        validation_scope: Dict[str, Any],
        architectural_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate notes for coordination with other agents."""
        
        notes = []
        
        # Note architectural focus
        notes.append("Architectural validation focused on structural and organizational concerns")
        
        # Note coordination with code review agent
        if any(f.priority in [Priority.HIGH, Priority.CRITICAL] for f in findings):
            notes.append("High priority architectural issues identified - coordinate with code review for implementation details")
        
        # Note shared context
        if "shared_context" in architectural_analysis:
            notes.append(f"Shared context: {architectural_analysis['shared_context']}")
        
        # Note validation scope for other agents
        scope_note = f"Validation scope: {', '.join(validation_scope.get('validation_areas', []))}"
        notes.append(scope_note)
        
        # Note consistency requirements
        notes.append("Recommendations should be consistent with previous architectural decisions")
        
        return notes
    
    def _collect_architectural_references(
        self,
        architectural_analysis: Dict[str, Any],
        best_practices: Dict[str, Any],
        adk_guidance: Dict[str, Any]
    ) -> List[str]:
        """Collect architectural documentation references from all analyses."""
        
        references = []
        
        # Standard ADK architectural references
        references.extend([
            "ADK Architecture Guide",
            "ADK Component Design Patterns",
            "ADK Dependency Management Best Practices"
        ])
        
        # Collect from analyses
        for analysis in [architectural_analysis, best_practices, adk_guidance]:
            if "references" in analysis:
                references.extend(analysis["references"])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_references = []
        for ref in references:
            if ref not in seen:
                seen.add(ref)
                unique_references.append(ref)
        
        return unique_references
    
    def _determine_architectural_scenario(
        self, 
        file_path: str, 
        validation_scope: Dict[str, Any]
    ) -> str:
        """Determine the architectural scenario for best practices lookup."""
        
        if "dependency_management" in validation_scope["validation_areas"]:
            return "dependency_architecture"
        elif "component_interfaces" in validation_scope["validation_areas"]:
            return "component_design"
        elif "application_structure" in validation_scope["validation_areas"]:
            return "application_architecture"
        elif "configuration_management" in validation_scope["validation_areas"]:
            return "configuration_architecture"
        else:
            return "general_architecture"
    
    def _get_architectural_file_type(self, file_path: str) -> str:
        """Determine architectural file type from path."""
        
        if file_path.endswith("lib.rs"):
            return "library_root"
        elif file_path.endswith("main.rs"):
            return "application_root"
        elif file_path.endswith("mod.rs"):
            return "module_interface"
        elif file_path.endswith("Cargo.toml"):
            return "project_configuration"
        elif "adk" in file_path and any(ext in file_path for ext in [".toml", ".json", ".yaml"]):
            return "adk_configuration"
        else:
            return "component_file"


def format_architectural_validation_result(result: ArchitecturalValidationResult) -> str:
    """Format the architectural validation result as markdown for display."""
    
    output = []
    output.append("# ADK Architecture Validation Results\n")
    
    # Architectural Summary
    output.append("## Architectural Summary")
    output.append(result.summary)
    output.append(f"\n**Compliance Level**: {result.compliance_level}\n")
    
    # Component Analysis
    if result.findings:
        output.append("## Component Analysis\n")
        for finding in result.findings:
            output.append(f"**[{finding.priority.value}] {finding.component_name}**")
            output.append(f"- **Location**: {finding.location}")
            output.append(f"- **Current State**: {finding.current_state}")
            output.append(f"- **ADK Compliance**: {finding.adk_compliance}")
            output.append(f"- **Issues Identified**: {finding.issues_identified}")
            output.append(f"- **Recommendations**: {finding.recommendations}")
            output.append(f"- **Impact**: {finding.impact}")
            if finding.example:
                output.append(f"- **Example**: \n```rust\n{finding.example}\n```")
            output.append("")
    
    # Dependency Validation
    if (result.dependency_analysis.compliant_dependencies or 
        result.dependency_analysis.version_issues or 
        result.dependency_analysis.missing_dependencies):
        
        output.append("## Dependency Validation")
        
        for dep in result.dependency_analysis.compliant_dependencies:
            output.append(f"✅ {dep}")
        
        for issue in result.dependency_analysis.version_issues:
            output.append(f"⚠️ {issue}")
        
        for missing in result.dependency_analysis.missing_dependencies:
            output.append(f"❌ Missing: {missing}")
        
        if result.dependency_analysis.recommendations:
            output.append("\n**Recommendations**:")
            for i, rec in enumerate(result.dependency_analysis.recommendations, 1):
                output.append(f"{i}. {rec}")
        
        output.append("")
    
    # Pattern Compliance
    if (result.pattern_compliance.compliant_patterns or 
        result.pattern_compliance.non_compliant_patterns or 
        result.pattern_compliance.missing_patterns):
        
        output.append("## Pattern Compliance")
        
        for pattern in result.pattern_compliance.compliant_patterns:
            output.append(f"✅ {pattern}")
        
        for pattern in result.pattern_compliance.non_compliant_patterns:
            output.append(f"⚠️ {pattern}")
        
        for pattern in result.pattern_compliance.missing_patterns:
            output.append(f"❌ Missing: {pattern}")
        
        if result.pattern_compliance.recommendations:
            output.append("\n**Key Patterns to Implement**:")
            for i, rec in enumerate(result.pattern_compliance.recommendations, 1):
                output.append(f"{i}. **{rec.split(':')[0] if ':' in rec else rec}**: {rec.split(':', 1)[1] if ':' in rec else 'Implementation recommended'}")
        
        output.append("")
    
    # Coordination Notes
    if result.coordination_notes:
        output.append("## Coordination Notes")
        for note in result.coordination_notes:
            output.append(f"- {note}")
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


# Example usage and testing
async def main():
    """Example usage of the ADK Architecture Agent."""
    
    # Mock MCP client for testing
    class MockMCPClient:
        async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]):
            # Mock response for testing
            if tool_name == "validate_architecture":
                return {
                    "findings": [
                        {
                            "priority": "Medium",
                            "component": "Module Organization",
                            "location": "src/lib.rs, module declarations",
                            "current_state": "Modules are functional but could benefit from better organization",
                            "adk_compliance": "Partially compliant - follows basic patterns but misses some ADK conventions",
                            "issues": "Some modules expose too much internal structure",
                            "recommendations": "Implement proper facade pattern for module interfaces",
                            "impact": "Improves maintainability and follows ADK encapsulation best practices",
                            "example": "pub use internal_service::PublicInterface;"
                        }
                    ],
                    "patterns": {
                        "compliant": ["Basic ADK component structure"],
                        "non_compliant": ["Dependency injection pattern"],
                        "missing": ["Configuration management pattern"]
                    },
                    "dependencies": {
                        "compliant": ["ADK core dependencies properly configured"],
                        "issues": ["Optional dependencies could be better organized"],
                        "recommendations": ["Group related optional dependencies using Cargo features"]
                    }
                }
            elif tool_name == "get_best_practices":
                return {
                    "pattern_compliance": {
                        "followed": ["Proper async/await usage"],
                        "violated": ["Dependency injection"],
                        "recommendations": ["ADK Dependency Injection: Use ADK's DI container"]
                    },
                    "references": ["ADK Dependency Injection Patterns"]
                }
            else:  # adk_query
                return {
                    "recommended_patterns": ["Component Lifecycle pattern"],
                    "references": ["ADK Component Lifecycle Guide"]
                }
    
    # Test the agent
    agent = ADKArchitectureAgent(MockMCPClient())
    
    sample_lib_rs = '''
    pub mod user_service;
    pub mod data_models;
    
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


if __name__ == "__main__":
    asyncio.run(main())