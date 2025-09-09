#!/usr/bin/env python3
"""
Custom Security Agent for ADK Projects

This agent performs security-focused analysis of ADK projects, identifying
potential vulnerabilities and suggesting improvements based on ADK security
best practices.
"""

import json
import re
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path

# Import base agent (in real implementation, adjust import path)
# from ..base_agent import BaseADKAgent
# For this example, we'll define a minimal base class
class BaseADKAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agent_name = "base-agent"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
    
    def get_fallback_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class CustomSecurityAgent(BaseADKAgent):
    """Custom agent for security analysis of ADK projects"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.agent_name = "custom-security-agent"
        self.description = "Security-focused analysis for ADK projects"
        
        # Load security patterns
        self.security_patterns = self._load_security_patterns()
        
        # Security configuration
        self.security_config = config.get('securityRules', {})
        self.strict_mode = self.security_config.get('strictMode', False)
        self.report_level = self.security_config.get('reportLevel', 'medium')
    
    def _load_security_patterns(self) -> Dict[str, Any]:
        """Load security patterns from configuration file"""
        try:
            patterns_file = Path(__file__).parent / "security_patterns.json"
            if patterns_file.exists():
                with open(patterns_file) as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load security patterns: {e}")
        
        # Default patterns if file not found
        return {
            "patterns": [
                {
                    "name": "hardcoded-secrets",
                    "pattern": r"(password|secret|key|token)\s*=\s*[\"'][^\"']+[\"']",
                    "severity": "high",
                    "message": "Potential hardcoded secret detected",
                    "suggestion": "Use environment variables or secure configuration"
                },
                {
                    "name": "sql-injection-risk",
                    "pattern": r"format!\s*\(\s*[\"'].*SELECT.*\{.*\}.*[\"']",
                    "severity": "high",
                    "message": "Potential SQL injection vulnerability",
                    "suggestion": "Use parameterized queries or prepared statements"
                },
                {
                    "name": "unsafe-deserialization",
                    "pattern": r"serde_json::from_str\s*\(\s*&?[^)]+\)",
                    "severity": "medium",
                    "message": "Unsafe deserialization detected",
                    "suggestion": "Validate input before deserialization"
                }
            ]
        }
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution logic for security analysis"""
        try:
            file_content = context.get('file_content', '')
            file_path = context.get('file_path', '')
            
            # Perform security analysis
            security_issues = await self._analyze_security(file_content, file_path)
            
            # Get ADK-specific security guidance using MCP tools
            adk_guidance = await self._get_adk_security_guidance(file_content, security_issues)
            
            # Generate recommendations
            recommendations = self._generate_security_recommendations(security_issues, adk_guidance)
            
            # Update shared context for coordination with other agents
            await self._update_shared_context(file_path, security_issues, recommendations)
            
            return {
                'success': True,
                'agent': self.agent_name,
                'analysis_type': 'security',
                'security_issues': security_issues,
                'recommendations': recommendations,
                'severity_summary': self._generate_severity_summary(security_issues),
                'adk_guidance': adk_guidance
            }
            
        except Exception as e:
            return await self.handle_error(e, context)
    
    async def _analyze_security(self, file_content: str, file_path: str) -> List[Dict[str, Any]]:
        """Analyze file content for security issues"""
        issues = []
        
        # Check against security patterns
        for pattern_config in self.security_patterns.get('patterns', []):
            pattern = pattern_config['pattern']
            matches = re.finditer(pattern, file_content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                line_number = file_content[:match.start()].count('\n') + 1
                
                issue = {
                    'type': 'security_pattern',
                    'name': pattern_config['name'],
                    'severity': pattern_config['severity'],
                    'message': pattern_config['message'],
                    'suggestion': pattern_config['suggestion'],
                    'line_number': line_number,
                    'matched_text': match.group(),
                    'file_path': file_path
                }
                
                issues.append(issue)
        
        # Additional security checks
        issues.extend(await self._check_adk_security_patterns(file_content, file_path))
        
        return issues
    
    async def _check_adk_security_patterns(self, file_content: str, file_path: str) -> List[Dict[str, Any]]:
        """Check for ADK-specific security patterns"""
        issues = []
        
        # Check for insecure ADK patterns
        adk_patterns = [
            {
                'pattern': r'\.unwrap\(\)',
                'severity': 'medium',
                'message': 'Use of unwrap() can cause panics',
                'suggestion': 'Use proper error handling with Result types'
            },
            {
                'pattern': r'unsafe\s*\{',
                'severity': 'high',
                'message': 'Unsafe code block detected',
                'suggestion': 'Ensure unsafe code is properly reviewed and documented'
            },
            {
                'pattern': r'std::process::Command::new\([^)]*\)\.arg\([^)]*user_input',
                'severity': 'high',
                'message': 'Potential command injection vulnerability',
                'suggestion': 'Sanitize user input before using in commands'
            }
        ]
        
        for pattern_config in adk_patterns:
            pattern = pattern_config['pattern']
            matches = re.finditer(pattern, file_content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                line_number = file_content[:match.start()].count('\n') + 1
                
                issue = {
                    'type': 'adk_security_pattern',
                    'name': f"adk-{pattern_config.get('name', 'security-issue')}",
                    'severity': pattern_config['severity'],
                    'message': pattern_config['message'],
                    'suggestion': pattern_config['suggestion'],
                    'line_number': line_number,
                    'matched_text': match.group(),
                    'file_path': file_path
                }
                
                issues.append(issue)
        
        return issues
    
    async def _get_adk_security_guidance(self, file_content: str, security_issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get ADK-specific security guidance using MCP tools"""
        try:
            # Simulate MCP tool call (in real implementation, use actual MCP client)
            # For this example, we'll return mock guidance
            
            guidance = {
                'best_practices': [
                    'Use Result<T, E> for error handling instead of unwrap()',
                    'Implement proper input validation for all user inputs',
                    'Use ADK security middleware for authentication and authorization',
                    'Follow ADK guidelines for secure data handling'
                ],
                'adk_specific_recommendations': [
                    'Consider using ADK security utilities for common security tasks',
                    'Implement ADK logging patterns for security events',
                    'Use ADK configuration management for sensitive settings'
                ],
                'documentation_links': [
                    'https://docs.google.com/adk/security/best-practices',
                    'https://docs.google.com/adk/security/authentication',
                    'https://docs.google.com/adk/security/data-protection'
                ]
            }
            
            # In real implementation:
            # guidance = await self.mcp_client.call_tool(
            #     'get_best_practices',
            #     {'category': 'security', 'context': 'adk_project'}
            # )
            
            return guidance
            
        except Exception as e:
            print(f"Warning: Could not get ADK security guidance: {e}")
            return {'error': 'MCP guidance unavailable'}
    
    def _generate_security_recommendations(self, security_issues: List[Dict[str, Any]], adk_guidance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable security recommendations"""
        recommendations = []
        
        # Group issues by severity
        high_severity_issues = [issue for issue in security_issues if issue['severity'] == 'high']
        medium_severity_issues = [issue for issue in security_issues if issue['severity'] == 'medium']
        low_severity_issues = [issue for issue in security_issues if issue['severity'] == 'low']
        
        # High priority recommendations
        if high_severity_issues:
            recommendations.append({
                'priority': 'high',
                'category': 'critical_security',
                'title': f'Address {len(high_severity_issues)} Critical Security Issues',
                'description': 'Critical security vulnerabilities that should be addressed immediately',
                'issues': high_severity_issues,
                'action_items': [
                    'Review and fix all high-severity security issues',
                    'Implement proper input validation',
                    'Use secure coding practices'
                ]
            })
        
        # Medium priority recommendations
        if medium_severity_issues:
            recommendations.append({
                'priority': 'medium',
                'category': 'security_improvements',
                'title': f'Improve {len(medium_severity_issues)} Security Practices',
                'description': 'Security improvements that enhance overall code security',
                'issues': medium_severity_issues,
                'action_items': [
                    'Review medium-severity security issues',
                    'Implement additional security measures',
                    'Follow ADK security best practices'
                ]
            })
        
        # ADK-specific recommendations
        if adk_guidance and 'best_practices' in adk_guidance:
            recommendations.append({
                'priority': 'medium',
                'category': 'adk_security_best_practices',
                'title': 'Follow ADK Security Best Practices',
                'description': 'Implement ADK-recommended security practices',
                'best_practices': adk_guidance['best_practices'],
                'action_items': adk_guidance.get('adk_specific_recommendations', [])
            })
        
        return recommendations
    
    def _generate_severity_summary(self, security_issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Generate summary of issues by severity"""
        summary = {'high': 0, 'medium': 0, 'low': 0}
        
        for issue in security_issues:
            severity = issue.get('severity', 'low')
            if severity in summary:
                summary[severity] += 1
        
        return summary
    
    async def _update_shared_context(self, file_path: str, security_issues: List[Dict[str, Any]], recommendations: List[Dict[str, Any]]):
        """Update shared context for coordination with other agents"""
        # In real implementation, use actual context manager
        context_update = {
            'agent': self.agent_name,
            'analysis_type': 'security',
            'issues_found': len(security_issues),
            'high_severity_count': len([i for i in security_issues if i['severity'] == 'high']),
            'recommendations_count': len(recommendations),
            'timestamp': 'current_timestamp'  # In real implementation, use actual timestamp
        }
        
        # await self.context_manager.update_context(file_path, context_update)
        print(f"Context updated for {file_path}: {context_update}")
    
    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle errors with fallback response"""
        print(f"Security agent error: {error}")
        
        return {
            'success': False,
            'agent': self.agent_name,
            'error': str(error),
            'fallback_response': self.get_fallback_response(context)
        }
    
    def get_fallback_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback security guidance when MCP is unavailable"""
        return {
            'message': 'MCP server unavailable - using fallback security guidance',
            'fallback_recommendations': [
                {
                    'priority': 'high',
                    'category': 'general_security',
                    'title': 'Manual Security Review Required',
                    'description': 'Perform manual security review of the code',
                    'action_items': [
                        'Review code for hardcoded secrets',
                        'Check for proper input validation',
                        'Ensure error handling is secure',
                        'Verify authentication and authorization',
                        'Check for SQL injection vulnerabilities'
                    ]
                }
            ],
            'security_checklist': [
                'No hardcoded passwords or secrets',
                'Proper input validation implemented',
                'Secure error handling (no information leakage)',
                'Authentication and authorization checks',
                'Protection against common vulnerabilities (OWASP Top 10)'
            ]
        }


# Test function for standalone execution
async def test_security_agent():
    """Test the security agent with sample code"""
    config = {
        'mcpServer': 'arkaft-google-adk',
        'securityRules': {
            'strictMode': True,
            'reportLevel': 'detailed'
        }
    }
    
    agent = CustomSecurityAgent(config)
    
    # Test with code containing security issues
    test_code = '''
fn main() {
    let password = "hardcoded_password_123";
    let query = format!("SELECT * FROM users WHERE id = {}", user_id);
    let result = serde_json::from_str(&untrusted_input).unwrap();
    
    unsafe {
        // Some unsafe code
        let ptr = std::ptr::null_mut();
    }
}
'''
    
    context = {
        'file_content': test_code,
        'file_path': 'src/main.rs'
    }
    
    result = await agent.execute(context)
    
    print("Security Analysis Result:")
    print(json.dumps(result, indent=2))
    
    return result


if __name__ == "__main__":
    # Run test when executed directly
    asyncio.run(test_security_agent())