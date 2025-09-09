#!/usr/bin/env python3
"""
ADK Code Review Agent Implementation

This agent provides automated code review for Google ADK projects using the
arkaft-mcp-google-adk MCP server tools.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class Priority(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class ReviewFinding:
    """Represents a single code review finding."""
    priority: Priority
    title: str
    location: str
    description: str
    adk_impact: str
    recommendation: str
    example: Optional[str] = None


@dataclass
class ReviewResult:
    """Complete code review result."""
    summary: str
    priority: Priority
    findings: List[ReviewFinding]
    best_practices_status: Dict[str, bool]
    action_items: List[str]
    references: List[str]


class ADKCodeReviewAgent:
    """
    ADK Code Review Agent that uses MCP tools to analyze Rust code files
    for ADK compliance and best practices.
    """
    
    def __init__(self, mcp_client):
        """Initialize the agent with MCP client."""
        self.mcp_client = mcp_client
        self.mcp_server_name = "arkaft-google-adk"
        
    async def review_file(self, file_path: str, file_content: str, project_context: Dict[str, Any]) -> ReviewResult:
        """
        Main entry point for file review.
        
        Args:
            file_path: Path to the file being reviewed
            file_content: Content of the file
            project_context: Additional project context
            
        Returns:
            ReviewResult with comprehensive analysis
        """
        try:
            # Step 1: Primary analysis using review_rust_file
            primary_analysis = await self._analyze_with_review_tool(file_content, file_path)
            
            # Step 2: Architectural validation if patterns detected
            architectural_analysis = await self._validate_architecture_if_needed(
                file_content, file_path, primary_analysis
            )
            
            # Step 3: Get best practices recommendations
            best_practices = await self._get_best_practices_guidance(file_path, primary_analysis)
            
            # Step 4: Compile comprehensive review result
            return await self._compile_review_result(
                file_path, primary_analysis, architectural_analysis, best_practices
            )
            
        except Exception as e:
            # Graceful degradation on MCP failures
            return await self._fallback_review(file_path, file_content, str(e))
    
    async def _analyze_with_review_tool(self, file_content: str, file_path: str) -> Dict[str, Any]:
        """Use review_rust_file MCP tool for primary analysis."""
        try:
            result = await self.mcp_client.call_tool(
                server_name=self.mcp_server_name,
                tool_name="review_rust_file",
                arguments={
                    "file_content": file_content,
                    "file_path": file_path,
                    "focus_areas": [
                        "translation_opportunities",
                        "error_handling",
                        "adk_compliance",
                        "performance",
                        "code_quality"
                    ]
                }
            )
            return result
        except Exception as e:
            print(f"Warning: review_rust_file MCP tool failed: {e}")
            return {"error": str(e), "fallback": True}
    
    async def _validate_architecture_if_needed(
        self, file_content: str, file_path: str, primary_analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Use validate_architecture MCP tool if architectural patterns detected."""
        
        # Check if architectural validation is needed
        architectural_indicators = [
            "impl", "trait", "struct", "enum", "mod", "pub struct", "pub trait"
        ]
        
        if not any(indicator in file_content for indicator in architectural_indicators):
            return None
            
        try:
            result = await self.mcp_client.call_tool(
                server_name=self.mcp_server_name,
                tool_name="validate_architecture",
                arguments={
                    "file_content": file_content,
                    "file_path": file_path,
                    "validation_focus": [
                        "component_organization",
                        "dependency_management",
                        "separation_of_concerns",
                        "adk_patterns"
                    ]
                }
            )
            return result
        except Exception as e:
            print(f"Warning: validate_architecture MCP tool failed: {e}")
            return None
    
    async def _get_best_practices_guidance(
        self, file_path: str, primary_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get best practices recommendations using get_best_practices MCP tool."""
        try:
            # Determine scenario based on file path and analysis
            scenario = self._determine_best_practices_scenario(file_path, primary_analysis)
            
            result = await self.mcp_client.call_tool(
                server_name=self.mcp_server_name,
                tool_name="get_best_practices",
                arguments={
                    "scenario": scenario,
                    "context": {
                        "file_type": self._get_file_type(file_path),
                        "component_type": self._detect_component_type(primary_analysis)
                    }
                }
            )
            return result
        except Exception as e:
            print(f"Warning: get_best_practices MCP tool failed: {e}")
            return {"error": str(e)}
    
    async def _compile_review_result(
        self,
        file_path: str,
        primary_analysis: Dict[str, Any],
        architectural_analysis: Optional[Dict[str, Any]],
        best_practices: Dict[str, Any]
    ) -> ReviewResult:
        """Compile all analysis results into a comprehensive review."""
        
        findings = []
        
        # Process primary analysis findings
        if "findings" in primary_analysis:
            for finding in primary_analysis["findings"]:
                findings.append(self._create_finding_from_analysis(finding))
        
        # Process architectural findings if available
        if architectural_analysis and "findings" in architectural_analysis:
            for finding in architectural_analysis["findings"]:
                findings.append(self._create_architectural_finding(finding))
        
        # Determine overall priority
        overall_priority = self._determine_overall_priority(findings)
        
        # Create summary
        summary = self._create_summary(file_path, findings, overall_priority)
        
        # Extract best practices status
        best_practices_status = self._extract_best_practices_status(
            primary_analysis, architectural_analysis, best_practices
        )
        
        # Generate action items
        action_items = self._generate_action_items(findings)
        
        # Collect references
        references = self._collect_references(primary_analysis, architectural_analysis, best_practices)
        
        return ReviewResult(
            summary=summary,
            priority=overall_priority,
            findings=findings,
            best_practices_status=best_practices_status,
            action_items=action_items,
            references=references
        )
    
    async def _fallback_review(self, file_path: str, file_content: str, error_msg: str) -> ReviewResult:
        """Provide basic review when MCP tools are unavailable."""
        
        # Basic static analysis
        findings = []
        
        # Check for common issues
        if "unwrap()" in file_content:
            findings.append(ReviewFinding(
                priority=Priority.MEDIUM,
                title="Potential Panic with unwrap()",
                location="Multiple locations",
                description="Found usage of unwrap() which can cause panics",
                adk_impact="May cause application crashes in production",
                recommendation="Use proper error handling with Result types or expect() with descriptive messages"
            ))
        
        if "println!" in file_content and "debug" not in file_path:
            findings.append(ReviewFinding(
                priority=Priority.LOW,
                title="Debug Print Statements",
                location="Multiple locations",
                description="Found println! statements in non-debug code",
                adk_impact="May clutter production logs",
                recommendation="Use proper logging framework or remove debug prints"
            ))
        
        return ReviewResult(
            summary=f"Fallback review for {file_path} (MCP server unavailable: {error_msg})",
            priority=Priority.LOW if not findings else Priority.MEDIUM,
            findings=findings,
            best_practices_status={"mcp_available": False},
            action_items=["Retry review when MCP server is available"],
            references=["Manual ADK documentation review recommended"]
        )
    
    def _create_finding_from_analysis(self, finding_data: Dict[str, Any]) -> ReviewFinding:
        """Convert MCP analysis result to ReviewFinding."""
        return ReviewFinding(
            priority=Priority(finding_data.get("priority", "Medium")),
            title=finding_data.get("title", "Code Review Finding"),
            location=finding_data.get("location", "Unknown"),
            description=finding_data.get("description", ""),
            adk_impact=finding_data.get("adk_impact", ""),
            recommendation=finding_data.get("recommendation", ""),
            example=finding_data.get("example")
        )
    
    def _create_architectural_finding(self, finding_data: Dict[str, Any]) -> ReviewFinding:
        """Convert architectural analysis result to ReviewFinding."""
        return ReviewFinding(
            priority=Priority(finding_data.get("priority", "Medium")),
            title=f"Architecture: {finding_data.get('title', 'Architectural Finding')}",
            location=finding_data.get("location", "Component level"),
            description=finding_data.get("description", ""),
            adk_impact=finding_data.get("adk_impact", "Affects architectural compliance"),
            recommendation=finding_data.get("recommendation", ""),
            example=finding_data.get("example")
        )
    
    def _determine_overall_priority(self, findings: List[ReviewFinding]) -> Priority:
        """Determine overall priority based on individual findings."""
        if any(f.priority == Priority.HIGH for f in findings):
            return Priority.HIGH
        elif any(f.priority == Priority.MEDIUM for f in findings):
            return Priority.MEDIUM
        else:
            return Priority.LOW
    
    def _create_summary(self, file_path: str, findings: List[ReviewFinding], priority: Priority) -> str:
        """Create a summary of the review results."""
        file_name = file_path.split('/')[-1]
        finding_count = len(findings)
        
        if finding_count == 0:
            return f"Reviewed `{file_name}` - No issues found. Code follows ADK best practices."
        
        priority_text = "No critical issues" if priority != Priority.HIGH else "Critical issues found"
        
        return f"Reviewed `{file_name}` - {finding_count} finding(s) identified. {priority_text}, review recommended improvements."
    
    def _extract_best_practices_status(
        self,
        primary_analysis: Dict[str, Any],
        architectural_analysis: Optional[Dict[str, Any]],
        best_practices: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Extract best practices compliance status."""
        status = {}
        
        # Extract from primary analysis
        if "best_practices" in primary_analysis:
            status.update(primary_analysis["best_practices"])
        
        # Extract from architectural analysis
        if architectural_analysis and "best_practices" in architectural_analysis:
            status.update(architectural_analysis["best_practices"])
        
        # Extract from best practices guidance
        if "compliance" in best_practices:
            status.update(best_practices["compliance"])
        
        return status
    
    def _generate_action_items(self, findings: List[ReviewFinding]) -> List[str]:
        """Generate prioritized action items from findings."""
        action_items = []
        
        # Group by priority
        high_priority = [f for f in findings if f.priority == Priority.HIGH]
        medium_priority = [f for f in findings if f.priority == Priority.MEDIUM]
        low_priority = [f for f in findings if f.priority == Priority.LOW]
        
        # Add high priority items
        for finding in high_priority:
            action_items.append(f"**High Priority**: {finding.title}")
        
        # Add medium priority items
        for finding in medium_priority:
            action_items.append(f"**Medium Priority**: {finding.title}")
        
        # Add low priority items
        for finding in low_priority:
            action_items.append(f"**Low Priority**: {finding.title}")
        
        return action_items
    
    def _collect_references(
        self,
        primary_analysis: Dict[str, Any],
        architectural_analysis: Optional[Dict[str, Any]],
        best_practices: Dict[str, Any]
    ) -> List[str]:
        """Collect documentation references from all analyses."""
        references = []
        
        # Collect from primary analysis
        if "references" in primary_analysis:
            references.extend(primary_analysis["references"])
        
        # Collect from architectural analysis
        if architectural_analysis and "references" in architectural_analysis:
            references.extend(architectural_analysis["references"])
        
        # Collect from best practices
        if "references" in best_practices:
            references.extend(best_practices["references"])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_references = []
        for ref in references:
            if ref not in seen:
                seen.add(ref)
                unique_references.append(ref)
        
        return unique_references
    
    def _determine_best_practices_scenario(self, file_path: str, analysis: Dict[str, Any]) -> str:
        """Determine the best practices scenario based on file and analysis."""
        if "service" in file_path.lower():
            return "service_implementation"
        elif "component" in file_path.lower():
            return "component_development"
        elif "model" in file_path.lower() or "entity" in file_path.lower():
            return "data_modeling"
        elif "lib.rs" in file_path or "main.rs" in file_path:
            return "application_structure"
        else:
            return "general_development"
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type from path."""
        if file_path.endswith("lib.rs"):
            return "library"
        elif file_path.endswith("main.rs"):
            return "binary"
        elif "test" in file_path:
            return "test"
        elif "example" in file_path:
            return "example"
        else:
            return "module"
    
    def _detect_component_type(self, analysis: Dict[str, Any]) -> str:
        """Detect component type from analysis."""
        if "component_type" in analysis:
            return analysis["component_type"]
        else:
            return "unknown"


def format_review_result(result: ReviewResult) -> str:
    """Format the review result as markdown for display."""
    
    output = []
    output.append("# ADK Code Review Results\n")
    
    # Summary
    output.append("## Summary")
    output.append(result.summary)
    output.append(f"\n**Priority**: {result.priority.value}\n")
    
    # Detailed Findings
    if result.findings:
        output.append("## Detailed Findings\n")
        for finding in result.findings:
            output.append(f"**[{finding.priority.value}] {finding.title}**")
            output.append(f"- **Location**: {finding.location}")
            output.append(f"- **Description**: {finding.description}")
            output.append(f"- **ADK Impact**: {finding.adk_impact}")
            output.append(f"- **Recommendation**: {finding.recommendation}")
            if finding.example:
                output.append(f"- **Example**: \n```rust\n{finding.example}\n```")
            output.append("")
    
    # Best Practices Validation
    if result.best_practices_status:
        output.append("## Best Practices Validation")
        for practice, status in result.best_practices_status.items():
            icon = "✅" if status else "⚠️"
            practice_name = practice.replace("_", " ").title()
            output.append(f"{icon} {practice_name}")
        output.append("")
    
    # Action Items
    if result.action_items:
        output.append("## Action Items")
        for i, item in enumerate(result.action_items, 1):
            output.append(f"{i}. {item}")
        output.append("")
    
    # References
    if result.references:
        output.append("## References")
        for ref in result.references:
            output.append(f"- {ref}")
    
    return "\n".join(output)


# Example usage and testing
async def main():
    """Example usage of the ADK Code Review Agent."""
    
    # Mock MCP client for testing
    class MockMCPClient:
        async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]):
            # Mock response for testing
            return {
                "findings": [
                    {
                        "priority": "High",
                        "title": "Translation Support Missing",
                        "location": "Lines 45-52",
                        "description": "Hardcoded error messages should be externalized",
                        "adk_impact": "Prevents proper internationalization",
                        "recommendation": "Use ADK translation APIs",
                        "example": 'return Err(translate!("errors.user_not_found"));'
                    }
                ],
                "best_practices": {
                    "async_usage": True,
                    "error_handling": False,
                    "translation_support": False
                },
                "references": [
                    "ADK Translation Guide",
                    "ADK Error Handling Best Practices"
                ]
            }
    
    # Test the agent
    agent = ADKCodeReviewAgent(MockMCPClient())
    
    sample_code = '''
    pub fn get_user(id: u32) -> Result<User, String> {
        if id == 0 {
            return Err("User not found".to_string());
        }
        // ... rest of implementation
        Ok(user)
    }
    '''
    
    result = await agent.review_file("src/user_service.rs", sample_code, {})
    formatted_output = format_review_result(result)
    print(formatted_output)


if __name__ == "__main__":
    asyncio.run(main())