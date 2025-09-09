#!/usr/bin/env python3
"""
ADK Agents Configuration Manager

Handles configuration validation, migration, and management for the ADK Agents system.
Provides utilities for loading, validating, and migrating configuration files.
"""

import json
import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
try:
    import jsonschema
    from jsonschema import validate, ValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    ValidationError = Exception


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass


class ADKConfigManager:
    """
    Manages ADK Agents configuration including validation, migration, and defaults.
    """
    
    def __init__(self, config_dir: str = "../../.kiro/settings"):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "adk-agents.json"
        self.schema_file = self.config_dir / "adk-agents.schema.json"
        self.backup_dir = self.config_dir / "backups"
        self.migration_dir = Path("../../.kiro/migrations/adk-agents")
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.migration_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def load_configuration(self) -> Dict[str, Any]:
        """
        Load and validate the configuration file.
        
        Returns:
            Validated configuration dictionary
            
        Raises:
            ConfigurationError: If configuration is invalid or missing
        """
        try:
            if not self.config_file.exists():
                self.logger.info("Configuration file not found, creating default configuration")
                return self.create_default_configuration()
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validate configuration
            self.validate_configuration(config)
            
            # Check if migration is needed
            if self.needs_migration(config):
                self.logger.info("Configuration migration required")
                config = self.migrate_configuration(config)
            
            return config
            
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """
        Validate configuration against JSON schema.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ConfigurationError: If validation fails
        """
        try:
            if not HAS_JSONSCHEMA:
                self.logger.warning("jsonschema package not available, performing basic validation only")
                self._basic_validation(config)
                return
            
            if not self.schema_file.exists():
                self.logger.warning("Schema file not found, performing basic validation only")
                self._basic_validation(config)
                return
            
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            validate(instance=config, schema=schema)
            self.logger.debug("Configuration validation successful")
            
        except ValidationError as e:
            error_path = " -> ".join(str(p) for p in e.path) if e.path else "root"
            raise ConfigurationError(f"Configuration validation failed at {error_path}: {e.message}")
        except Exception as e:
            raise ConfigurationError(f"Schema validation error: {e}")
    
    def _basic_validation(self, config: Dict[str, Any]) -> None:
        """
        Perform basic validation without jsonschema.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ConfigurationError: If basic validation fails
        """
        # Check required top-level fields
        required_fields = ["version", "agents", "hooks"]
        for field in required_fields:
            if field not in config:
                raise ConfigurationError(f"Missing required field: {field}")
        
        # Validate version format
        version = config.get("version", "")
        if not isinstance(version, str) or not version:
            raise ConfigurationError("Version must be a non-empty string")
        
        # Validate agents structure
        agents = config.get("agents", {})
        if not isinstance(agents, dict):
            raise ConfigurationError("Agents must be an object")
        
        for agent_name, agent_config in agents.items():
            if not isinstance(agent_config, dict):
                raise ConfigurationError(f"Agent '{agent_name}' configuration must be an object")
            
            agent_required = ["enabled", "mcpServer", "description"]
            for field in agent_required:
                if field not in agent_config:
                    raise ConfigurationError(f"Agent '{agent_name}' missing required field: {field}")
        
        # Validate hooks structure
        hooks = config.get("hooks", {})
        if not isinstance(hooks, dict):
            raise ConfigurationError("Hooks must be an object")
        
        for hook_name, hook_config in hooks.items():
            if not isinstance(hook_config, dict):
                raise ConfigurationError(f"Hook '{hook_name}' configuration must be an object")
            
            hook_required = ["enabled", "name", "description", "version"]
            for field in hook_required:
                if field not in hook_config:
                    raise ConfigurationError(f"Hook '{hook_name}' missing required field: {field}")
        
        self.logger.debug("Basic configuration validation successful")
    
    def create_default_configuration(self) -> Dict[str, Any]:
        """
        Create and save default configuration.
        
        Returns:
            Default configuration dictionary
        """
        default_config = {
            "version": "1.0.0",
            "agents": {
                "adk-project-assistant": {
                    "enabled": True,
                    "mcpServer": "arkaft-google-adk",
                    "description": "Comprehensive ADK project assistance using all MCP tools",
                    "preferences": {
                        "verbosity": "detailed",
                        "autoSuggest": True,
                        "adkVersion": "latest",
                        "includeExamples": True,
                        "linkToOfficial": True
                    },
                    "triggers": {
                        "manual": True,
                        "keywords": ["adk-help", "adk-assist", "adk-project"]
                    },
                    "tools": {
                        "adk_query": {"enabled": True, "priority": "high"},
                        "review_rust_file": {"enabled": True, "priority": "medium"},
                        "validate_architecture": {"enabled": True, "priority": "high"},
                        "get_best_practices": {"enabled": True, "priority": "high"}
                    }
                },
                "adk-code-review": {
                    "enabled": True,
                    "mcpServer": "arkaft-google-adk",
                    "description": "Automated code review for ADK compliance and improvements",
                    "preferences": {
                        "verbosity": "concise",
                        "focusAreas": ["translation", "error_handling", "architecture", "best_practices"],
                        "includeLineNumbers": True,
                        "prioritizeCritical": True
                    },
                    "triggers": {
                        "autoReview": True,
                        "fileSizeLimit": "50KB",
                        "filePatterns": ["*.rs", "src/**/*.rs"],
                        "excludePatterns": ["target/**", "*.test.rs", "**/*_test.rs"]
                    },
                    "tools": {
                        "review_rust_file": {"enabled": True, "priority": "high"},
                        "validate_architecture": {"enabled": True, "priority": "medium"}
                    },
                    "performance": {
                        "debounceMs": 2000,
                        "maxConcurrent": 3,
                        "timeout": 30000
                    }
                }
            },
            "hooks": {
                "adk-code-review": {
                    "enabled": True,
                    "name": "ADK Code Review",
                    "description": "Automatically reviews Rust files for ADK compliance",
                    "version": "1.0.0",
                    "sensitivity": "medium",
                    "debounceMs": 2000,
                    "when": {
                        "type": "fileEdited",
                        "patterns": ["*.rs", "src/**/*.rs"],
                        "conditions": {
                            "projectType": "adk",
                            "fileSize": "< 50KB",
                            "excludePatterns": ["target/**", "*.test.rs"]
                        }
                    },
                    "then": {
                        "type": "askAgent",
                        "agent": "adk-code-review-agent"
                    }
                }
            },
            "projectDetection": {
                "enabled": True,
                "criteria": {
                    "cargoToml": {
                        "dependencies": ["google-adk", "adk-*"],
                        "features": ["adk"]
                    },
                    "filePatterns": ["adk.toml", "adk-config.json", ".adk/**"],
                    "directoryStructure": ["src/adk/", "adk/"]
                }
            },
            "mcpIntegration": {
                "serverName": "arkaft-google-adk",
                "connectionTimeout": 10000,
                "retryAttempts": 3,
                "retryDelay": 1000,
                "healthCheck": {"enabled": True, "intervalMs": 30000},
                "fallback": {
                    "enabled": True,
                    "mode": "graceful",
                    "message": "ADK MCP server unavailable. Basic functionality only."
                }
            },
            "performance": {
                "global": {
                    "maxConcurrentAgents": 5,
                    "defaultTimeout": 30000,
                    "memoryLimit": "256MB"
                },
                "caching": {"enabled": True, "ttl": 300000, "maxSize": "50MB"},
                "monitoring": {"enabled": True, "logLevel": "info", "metricsCollection": True}
            },
            "migration": {
                "currentVersion": "1.0.0",
                "compatibleVersions": ["1.0.0"],
                "migrationPath": "../../.kiro/migrations/adk-agents/",
                "backupOnMigration": True
            }
        }
        
        self.save_configuration(default_config)
        self.logger.info("Default configuration created")
        return default_config
    
    def save_configuration(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
            
        Raises:
            ConfigurationError: If save fails
        """
        try:
            # Validate before saving
            self.validate_configuration(config)
            
            # Create backup if file exists
            if self.config_file.exists():
                self.create_backup()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Configuration saved successfully")
            
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def needs_migration(self, config: Dict[str, Any]) -> bool:
        """
        Check if configuration needs migration.
        
        Args:
            config: Configuration to check
            
        Returns:
            True if migration is needed
        """
        current_version = config.get("version", "0.0.0")
        target_version = "1.0.0"
        
        # Simple version comparison - in production, use proper semver
        return current_version != target_version
    
    def migrate_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate configuration to current version.
        
        Args:
            config: Configuration to migrate
            
        Returns:
            Migrated configuration
        """
        current_version = config.get("version", "0.0.0")
        self.logger.info(f"Migrating configuration from version {current_version} to 1.0.0")
        
        # Create backup before migration
        if config.get("migration", {}).get("backupOnMigration", True):
            self.create_backup(f"pre-migration-{current_version}")
        
        # Apply migrations based on current version
        migrated_config = self._apply_migrations(config, current_version)
        
        # Update version
        migrated_config["version"] = "1.0.0"
        
        # Save migrated configuration
        self.save_configuration(migrated_config)
        
        self.logger.info("Configuration migration completed")
        return migrated_config
    
    def _apply_migrations(self, config: Dict[str, Any], from_version: str) -> Dict[str, Any]:
        """
        Apply version-specific migrations.
        
        Args:
            config: Configuration to migrate
            from_version: Source version
            
        Returns:
            Migrated configuration
        """
        # Migration logic for different versions
        if from_version == "0.9.0":
            config = self._migrate_from_0_9_0(config)
        
        # Add more migration paths as needed
        
        return config
    
    def _migrate_from_0_9_0(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate from version 0.9.0 to 1.0.0.
        
        Args:
            config: Configuration to migrate
            
        Returns:
            Migrated configuration
        """
        # Example migration: add new performance settings
        if "performance" not in config:
            config["performance"] = {
                "global": {
                    "maxConcurrentAgents": 5,
                    "defaultTimeout": 30000,
                    "memoryLimit": "256MB"
                }
            }
        
        # Example: migrate old agent structure
        for agent_name, agent_config in config.get("agents", {}).items():
            if "tools" not in agent_config:
                agent_config["tools"] = {
                    "adk_query": {"enabled": True, "priority": "high"}
                }
        
        return config
    
    def create_backup(self, suffix: Optional[str] = None) -> str:
        """
        Create a backup of the current configuration.
        
        Args:
            suffix: Optional suffix for backup filename
            
        Returns:
            Path to backup file
        """
        if not self.config_file.exists():
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"adk-agents-{timestamp}"
        if suffix:
            backup_name += f"-{suffix}"
        backup_name += ".json"
        
        backup_path = self.backup_dir / backup_name
        shutil.copy2(self.config_file, backup_path)
        
        self.logger.info(f"Configuration backup created: {backup_path}")
        return str(backup_path)
    
    def get_agent_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent configuration or None if not found
        """
        config = self.load_configuration()
        return config.get("agents", {}).get(agent_name)
    
    def update_agent_config(self, agent_name: str, agent_config: Dict[str, Any]) -> None:
        """
        Update configuration for a specific agent.
        
        Args:
            agent_name: Name of the agent
            agent_config: New agent configuration
        """
        config = self.load_configuration()
        if "agents" not in config:
            config["agents"] = {}
        
        config["agents"][agent_name] = agent_config
        self.save_configuration(config)
    
    def is_agent_enabled(self, agent_name: str) -> bool:
        """
        Check if an agent is enabled.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            True if agent is enabled
        """
        agent_config = self.get_agent_config(agent_name)
        return agent_config.get("enabled", False) if agent_config else False
    
    def get_mcp_server_config(self) -> Dict[str, Any]:
        """
        Get MCP integration configuration.
        
        Returns:
            MCP integration configuration
        """
        config = self.load_configuration()
        return config.get("mcpIntegration", {})
    
    def validate_project_detection(self, project_path: str) -> bool:
        """
        Validate if a project matches ADK detection criteria.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            True if project matches ADK criteria
        """
        config = self.load_configuration()
        detection_config = config.get("projectDetection", {})
        
        if not detection_config.get("enabled", True):
            return False
        
        project_dir = Path(project_path)
        criteria = detection_config.get("criteria", {})
        
        # Check Cargo.toml dependencies
        cargo_toml = project_dir / "Cargo.toml"
        if cargo_toml.exists():
            try:
                import toml
                cargo_data = toml.load(cargo_toml)
                dependencies = cargo_data.get("dependencies", {})
                
                adk_deps = criteria.get("cargoToml", {}).get("dependencies", [])
                for dep_pattern in adk_deps:
                    if any(dep_pattern.replace("*", "") in dep for dep in dependencies.keys()):
                        return True
            except ImportError:
                self.logger.warning("toml package not available for Cargo.toml parsing")
        
        # Check file patterns
        file_patterns = criteria.get("filePatterns", [])
        for pattern in file_patterns:
            if list(project_dir.glob(pattern)):
                return True
        
        # Check directory structure
        dir_patterns = criteria.get("directoryStructure", [])
        for pattern in dir_patterns:
            if (project_dir / pattern).exists():
                return True
        
        return False


def main():
    """
    Command-line interface for configuration management.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="ADK Agents Configuration Manager")
    parser.add_argument("--validate", action="store_true", help="Validate configuration")
    parser.add_argument("--migrate", action="store_true", help="Migrate configuration")
    parser.add_argument("--backup", action="store_true", help="Create configuration backup")
    parser.add_argument("--reset", action="store_true", help="Reset to default configuration")
    parser.add_argument("--config-dir", default="../../.kiro/settings", help="Configuration directory")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    try:
        manager = ADKConfigManager(args.config_dir)
        
        if args.validate:
            config = manager.load_configuration()
            print("Configuration validation successful")
        
        elif args.migrate:
            config = manager.load_configuration()
            print("Configuration migration completed")
        
        elif args.backup:
            backup_path = manager.create_backup()
            print(f"Backup created: {backup_path}")
        
        elif args.reset:
            manager.create_default_configuration()
            print("Configuration reset to defaults")
        
        else:
            config = manager.load_configuration()
            print("Configuration loaded successfully")
            print(f"Version: {config.get('version')}")
            print(f"Agents: {len(config.get('agents', {}))}")
            print(f"Hooks: {len(config.get('hooks', {}))}")
    
    except ConfigurationError as e:
        print(f"Configuration error: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    main()