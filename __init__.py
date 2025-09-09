"""
Arkaft ADK Agents

A comprehensive suite of Google ADK-specific development agents providing
automated code review, architecture validation, documentation assistance,
and project management capabilities.

This package is organized into the following modules:
- agents: Core ADK agent implementations
- config: Agent configuration files
- tests: Comprehensive test suites
- docs: Agent-specific documentation
- examples: Usage examples and templates
- multi_tool_agent: Multi-tool agent implementations
"""

__version__ = "1.0.0"
__author__ = "Arkaft Development Team"
__description__ = "Google ADK Development Agents Suite"

# Import main agent modules for easy access
from . import agents
from . import multi_tool_agent

__all__ = [
    "agents",
    "multi_tool_agent"
]