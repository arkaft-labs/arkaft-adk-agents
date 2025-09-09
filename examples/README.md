# ADK Agents Configuration Examples

This directory contains complete examples of custom agent configurations and workflows for the ADK Agents system.

## Examples Overview

### Configuration Examples

- **[basic-setup.json](basic-setup.json)**: Minimal configuration for getting started
- **[advanced-setup.json](advanced-setup.json)**: Full-featured configuration with all options
- **[performance-optimized.json](performance-optimized.json)**: Configuration optimized for performance
- **[team-collaboration.json](team-collaboration.json)**: Configuration for team development

### Custom Agent Examples

- **[custom-agent-example/](custom-agent-example/)**: Complete custom agent implementation
- **[specialized-review-agent/](specialized-review-agent/)**: Agent for specialized code review
- **[project-template-agent/](project-template-agent/)**: Agent for project template management

### Hook Examples

- **[advanced-hook-example/](advanced-hook-example/)**: Advanced hook with custom conditions
- **[workflow-hook-example/](workflow-hook-example/)**: Multi-step workflow hook
- **[conditional-hook-example/](conditional-hook-example/)**: Hook with complex conditions

### Workflow Examples

- **[new-component-workflow/](new-component-workflow/)**: Complete workflow for creating new components
- **[refactoring-workflow/](refactoring-workflow/)**: Workflow for guided refactoring
- **[testing-workflow/](testing-workflow/)**: Workflow for comprehensive testing

## Quick Start

1. **Choose a configuration example** that matches your needs
2. **Copy the configuration** to `.kiro/settings/adk-agents.json`
3. **Customize the settings** for your specific requirements
4. **Test the configuration** using the validation tools
5. **Iterate and refine** based on your development workflow

## Configuration Validation

Before using any example configuration:

```bash
# Validate configuration syntax
python .kiro/agents/validate_config.py --config examples/basic-setup.json

# Test with your project
cp examples/basic-setup.json .kiro/settings/adk-agents.json
python .kiro/agents/validate_config.py
```

## Customization Guidelines

1. **Start simple**: Begin with basic-setup.json and add features incrementally
2. **Test thoroughly**: Validate each change before adding more complexity
3. **Monitor performance**: Use performance-optimized.json as a reference for resource limits
4. **Team coordination**: Use team-collaboration.json for shared development environments

## Support

- See [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) for common issues
- Check [USER_GUIDE.md](../USER_GUIDE.md) for detailed configuration options
- Review [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md) for extending the system