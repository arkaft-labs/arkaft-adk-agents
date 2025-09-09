# ADK Agents User Guide

This guide covers how to customize agent behavior, configure hooks, and optimize the ADK Agents system for your specific development needs.

## Table of Contents

- [Agent Configuration](#agent-configuration)
- [Hook Customization](#hook-customization)
- [Performance Tuning](#performance-tuning)
- [Custom Workflows](#custom-workflows)
- [Advanced Configuration](#advanced-configuration)

## Agent Configuration

### Basic Agent Settings

Each agent can be individually configured in `../.kiro/settings/adk-agents.json`:

```json
{
  "agents": {
    "adk-code-review": {
      "enabled": true,
      "mcpServer": "arkaft-google-adk",
      "triggers": {
        "autoReview": true,
        "fileSizeLimit": "50KB",
        "excludePatterns": ["target/**", "*.test.rs", "examples/**"]
      },
      "preferences": {
        "verbosity": "detailed",
        "focusAreas": ["translation", "architecture", "performance"],
        "includeExamples": true
      }
    }
  }
}
```

### Agent-Specific Configuration

#### ADK Code Review Agent

```json
"adk-code-review": {
  "enabled": true,
  "triggers": {
    "autoReview": true,
    "fileSizeLimit": "50KB",
    "excludePatterns": ["target/**", "*.test.rs"],
    "includePatterns": ["src/**/*.rs"],
    "debounceMs": 2000
  },
  "analysis": {
    "checkTranslation": true,
    "validateArchitecture": true,
    "enforceStyle": false,
    "suggestOptimizations": true
  },
  "output": {
    "verbosity": "detailed",
    "includeExamples": true,
    "linkToDocumentation": true,
    "groupSuggestions": true
  }
}
```

#### ADK Architecture Agent

```json
"adk-architecture": {
  "enabled": true,
  "validation": {
    "strictMode": false,
    "customPatterns": [
      {
        "name": "custom-service-pattern",
        "description": "Custom service organization pattern",
        "rules": ["services must be in src/services/", "each service must have tests"]
      }
    ],
    "ignorePatterns": ["legacy/**", "deprecated/**"]
  },
  "reporting": {
    "includeCompliance": true,
    "suggestRefactoring": true,
    "prioritizeIssues": true
  }
}
```

#### ADK Documentation Agent

```json
"adk-documentation": {
  "enabled": true,
  "preferences": {
    "includeExamples": true,
    "linkToOfficial": true,
    "contextDepth": "detailed",
    "cacheResponses": true
  },
  "sources": {
    "officialDocs": true,
    "communityExamples": false,
    "internalKnowledge": true
  }
}
```

#### ADK Project Assistant Agent

```json
"adk-project-assistant": {
  "enabled": true,
  "assistance": {
    "projectSetup": true,
    "architecturalGuidance": true,
    "troubleshooting": true,
    "taskBreakdown": true
  },
  "preferences": {
    "verbosity": "detailed",
    "autoSuggest": true,
    "adkVersion": "latest",
    "includeAlternatives": true
  }
}
```

## Hook Customization

### Hook Configuration

Hooks are configured in individual `.kiro.hook` files and can be customized through the main configuration:

```json
{
  "hooks": {
    "adk-code-review": {
      "enabled": true,
      "sensitivity": "medium",
      "debounceMs": 2000,
      "conditions": {
        "minFileSize": "100B",
        "maxFileSize": "50KB",
        "projectTypes": ["adk"],
        "excludePaths": ["target/**", "*.test.rs"]
      }
    },
    "adk-architecture-validator": {
      "enabled": true,
      "triggerOnSave": true,
      "watchFiles": ["src/lib.rs", "src/main.rs", "Cargo.toml"],
      "debounceMs": 1000
    },
    "adk-docs-assistant": {
      "enabled": true,
      "contextAware": true,
      "triggers": ["adk-help", "adk-docs", "adk-question"],
      "priority": "high"
    }
  }
}
```

### Custom Hook Triggers

You can create custom triggers for specific workflows:

```json
{
  "hooks": {
    "custom-adk-review": {
      "enabled": true,
      "name": "Custom ADK Review",
      "description": "Custom review for specific file patterns",
      "when": {
        "type": "fileEdited",
        "patterns": ["src/custom/**/*.rs"],
        "conditions": {
          "projectType": "adk",
          "customMarker": "// @adk-review"
        }
      },
      "then": {
        "type": "askAgent",
        "agent": "adk-code-review-agent",
        "prompt": "Custom review prompt for specialized components"
      }
    }
  }
}
```

## Performance Tuning

### Debouncing and Rate Limiting

Control how frequently agents are triggered:

```json
{
  "performance": {
    "debouncing": {
      "codeReview": 2000,
      "architecture": 1000,
      "documentation": 500
    },
    "rateLimiting": {
      "maxConcurrentAgents": 2,
      "cooldownPeriod": 5000,
      "maxRequestsPerMinute": 30
    },
    "resourceLimits": {
      "maxFileSize": "50KB",
      "timeoutMs": 30000,
      "maxRetries": 3
    }
  }
}
```

### Caching Configuration

Optimize performance with intelligent caching:

```json
{
  "caching": {
    "enabled": true,
    "strategies": {
      "mcpResponses": {
        "ttl": 3600,
        "maxSize": 100,
        "keyStrategy": "content-hash"
      },
      "projectAnalysis": {
        "ttl": 1800,
        "invalidateOnChange": true
      }
    }
  }
}
```

## Custom Workflows

### Creating Custom Agent Workflows

Define custom workflows for specific development scenarios:

```json
{
  "workflows": {
    "new-component-workflow": {
      "name": "New ADK Component Creation",
      "description": "Comprehensive workflow for creating new ADK components",
      "steps": [
        {
          "agent": "adk-project-assistant",
          "action": "validate-component-name",
          "prompt": "Validate the proposed component name and structure"
        },
        {
          "agent": "adk-architecture",
          "action": "check-architecture-compliance",
          "prompt": "Ensure the component fits the overall architecture"
        },
        {
          "agent": "adk-code-review",
          "action": "review-implementation",
          "prompt": "Review the initial implementation for best practices"
        }
      ],
      "triggers": ["new-component", "create-component"]
    }
  }
}
```

### Project-Specific Customization

Customize agents for specific project requirements:

```json
{
  "projectCustomization": {
    "patterns": {
      "microservice-project": {
        "detection": {
          "markers": ["microservice.toml", "service-config.yaml"],
          "structure": ["src/services/", "src/handlers/"]
        },
        "agentOverrides": {
          "adk-architecture": {
            "validation": {
              "enforceServiceBoundaries": true,
              "checkApiConsistency": true
            }
          }
        }
      }
    }
  }
}
```

## Advanced Configuration

### Error Handling Customization

Configure error handling behavior:

```json
{
  "errorHandling": {
    "circuitBreaker": {
      "failureThreshold": 5,
      "recoveryTimeout": 60000,
      "halfOpenMaxCalls": 3
    },
    "retryPolicy": {
      "maxAttempts": 3,
      "backoffMultiplier": 2,
      "initialDelay": 1000,
      "maxDelay": 10000
    },
    "fallbackBehavior": {
      "enableFallbacks": true,
      "cacheResponses": true,
      "providePlaceholderGuidance": true
    }
  }
}
```

### Agent Coordination

Configure how agents coordinate with each other:

```json
{
  "coordination": {
    "conflictResolution": {
      "strategy": "priority-based",
      "allowConcurrent": false,
      "maxConcurrentAgents": 2
    },
    "contextSharing": {
      "enabled": true,
      "shareAnalysisResults": true,
      "contextTtl": 1800
    },
    "messaging": {
      "consistencyChecks": true,
      "avoidContradictions": true,
      "consolidateRecommendations": true
    }
  }
}
```

### Extensibility Configuration

Configure the system for custom extensions:

```json
{
  "extensibility": {
    "customAgents": {
      "allowCustomAgents": true,
      "customAgentPath": "../.kiro/custom-agents/",
      "inheritFromBase": true
    },
    "customHooks": {
      "allowCustomHooks": true,
      "customHookPath": "../.kiro/custom-hooks/",
      "validateSchema": true
    },
    "plugins": {
      "enablePluginSystem": false,
      "pluginPath": "../.kiro/plugins/",
      "sandboxPlugins": true
    }
  }
}
```

## Configuration Validation

### Schema Validation

The system validates all configuration against JSON schemas:

```bash
# Validate configuration
python agents/adk_config_manager.py

# Check specific configuration section
python agents/adk_config_manager.py --section agents
python agents/adk_config_manager.py --section hooks
```

### Configuration Migration

When updating the system, configurations are automatically migrated:

```json
{
  "migration": {
    "autoMigrate": true,
    "backupBeforeMigration": true,
    "migrationPath": "../.kiro/config-backups/",
    "validateAfterMigration": true
  }
}
```

## Best Practices

### Configuration Management

1. **Start with defaults**: Use the default configuration as a starting point
2. **Incremental changes**: Make small, incremental changes and test each one
3. **Version control**: Keep your configuration in version control
4. **Environment-specific**: Use different configurations for different environments
5. **Regular validation**: Regularly validate your configuration for errors

### Performance Optimization

1. **Appropriate debouncing**: Set debouncing values based on your development style
2. **File size limits**: Set reasonable file size limits to prevent performance issues
3. **Exclude patterns**: Use exclude patterns to avoid analyzing unnecessary files
4. **Monitor resource usage**: Keep an eye on CPU and memory usage

### Agent Coordination

1. **Avoid conflicts**: Configure agents to avoid conflicting recommendations
2. **Prioritize manual triggers**: Give higher priority to manually triggered agents
3. **Share context**: Enable context sharing for consistent recommendations
4. **Monitor coordination**: Watch for coordination issues and adjust settings

## Examples

See the [examples/](examples/) directory for complete configuration examples:

- `basic-setup.json`: Basic configuration for getting started
- `advanced-setup.json`: Advanced configuration with all features enabled
- `performance-optimized.json`: Configuration optimized for performance
- `team-collaboration.json`: Configuration for team development environments