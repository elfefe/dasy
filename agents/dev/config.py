"""
Developer Agent Configuration
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentConfig:
    """Configuration for the Developer Agent"""
    
    # AI API Keys
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # GitHub Configuration
    github_token: Optional[str] = None
    github_webhook_secret: Optional[str] = None
    
    # RabbitMQ Configuration
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672"
    
    # Orchestrator Configuration
    orchestrator_url: str = "http://localhost:8000"
    
    # Agent Configuration
    agent_id: str = "dev-agent-001"
    agent_type: str = "developer"
    
    # Workspace Configuration
    workspace_dir: str = "/app/workspace"
    logs_dir: str = "/app/logs"
    
    # AI Model Configuration
    default_model: str = "gpt-4"
    temperature: float = 0.3
    max_tokens: int = 4000
    
    # Code Generation Settings
    supported_languages: list = None
    code_quality_checks: bool = True
    auto_format: bool = True
    
    def __post_init__(self):
        """Initialize configuration from environment variables"""
        
        # AI API Keys
        self.openai_api_key = os.getenv('OPENAI_API_KEY') or self.openai_api_key
        self.gemini_api_key = os.getenv('GEMINI_API_KEY') or self.gemini_api_key
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY') or self.anthropic_api_key
        
        # GitHub Configuration
        self.github_token = os.getenv('GITHUB_TOKEN') or self.github_token
        self.github_webhook_secret = os.getenv('GITHUB_WEBHOOK_SECRET') or self.github_webhook_secret
        
        # RabbitMQ Configuration
        self.rabbitmq_url = os.getenv('RABBITMQ_URL') or self.rabbitmq_url
        
        # Orchestrator Configuration
        self.orchestrator_url = os.getenv('ORCHESTRATOR_URL') or self.orchestrator_url
        
        # Agent Configuration
        self.agent_id = os.getenv('AGENT_ID') or self.agent_id
        self.agent_type = os.getenv('AGENT_TYPE') or self.agent_type
        
        # Workspace Configuration
        self.workspace_dir = os.getenv('WORKSPACE_DIR') or self.workspace_dir
        self.logs_dir = os.getenv('LOGS_DIR') or self.logs_dir
        
        # AI Model Configuration
        self.default_model = os.getenv('DEFAULT_MODEL') or self.default_model
        
        # Supported Languages
        if self.supported_languages is None:
            self.supported_languages = [
                'python', 'javascript', 'typescript', 'java', 'go', 
                'rust', 'php', 'ruby', 'c#', 'c++', 'html', 'css', 'sql'
            ]
        
        # Create directories if they don't exist
        os.makedirs(self.workspace_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def validate(self) -> bool:
        """Validate configuration"""
        errors = []
        
        # Check for required API keys
        if not self.openai_api_key and not self.gemini_api_key:
            errors.append("At least one AI API key (OpenAI or Gemini) must be provided")
        
        # Check RabbitMQ URL
        if not self.rabbitmq_url:
            errors.append("RabbitMQ URL is required")
        
        # Check orchestrator URL
        if not self.orchestrator_url:
            errors.append("Orchestrator URL is required")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        return True
    
    def get_ai_client_config(self) -> dict:
        """Get AI client configuration"""
        return {
            'openai': {
                'api_key': self.openai_api_key,
                'model': self.default_model,
                'temperature': self.temperature,
                'max_tokens': self.max_tokens
            },
            'gemini': {
                'api_key': self.gemini_api_key,
                'temperature': self.temperature
            },
            'anthropic': {
                'api_key': self.anthropic_api_key
            }
        }
    
    def __str__(self) -> str:
        """String representation (without sensitive data)"""
        return f"""
        Agent Configuration:
        - Agent ID: {self.agent_id}
        - Agent Type: {self.agent_type}
        - Workspace: {self.workspace_dir}
        - Default Model: {self.default_model}
        - Supported Languages: {', '.join(self.supported_languages)}
        - OpenAI Configured: {'Yes' if self.openai_api_key else 'No'}
        - Gemini Configured: {'Yes' if self.gemini_api_key else 'No'}
        - GitHub Configured: {'Yes' if self.github_token else 'No'}
        """