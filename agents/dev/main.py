#!/usr/bin/env python3
"""
Dasy Developer Agent
Autonomous AI agent specialized in software development tasks
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

from agent_core import DeveloperAgent
from config import AgentConfig
from messaging import MessageConsumer
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

class DeveloperAgentRunner:
    def __init__(self):
        self.config = AgentConfig()
        self.agent = DeveloperAgent(self.config)
        self.consumer = MessageConsumer(
            rabbitmq_url=self.config.rabbitmq_url,
            queue_name='dev.tasks',
            callback=self.handle_task
        )
        self.running = False

    async def handle_task(self, task_data: dict):
        """Handle incoming development tasks"""
        try:
            logger.info(f"Received task: {task_data.get('id', 'unknown')}")
            
            # Process the task with the AI agent
            result = await self.agent.process_task(task_data)
            
            # Send result back to orchestrator
            await self.consumer.publish_result(result)
            
            logger.info(f"Task completed: {task_data.get('id', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error processing task: {e}")
            
            # Send error result back
            error_result = {
                'task_id': task_data.get('id'),
                'status': 'error',
                'error': str(e),
                'agent_type': 'developer'
            }
            await self.consumer.publish_result(error_result)

    async def start(self):
        """Start the agent"""
        logger.info("Starting Dasy Developer Agent...")
        
        # Initialize the AI agent
        await self.agent.initialize()
        
        # Start consuming messages
        self.running = True
        await self.consumer.start_consuming()
        
        logger.info("Developer Agent is running and ready to receive tasks")

    async def stop(self):
        """Stop the agent"""
        logger.info("Stopping Developer Agent...")
        self.running = False
        await self.consumer.stop()
        logger.info("Developer Agent stopped")

    async def health_check(self):
        """Health check for the agent"""
        return {
            'status': 'healthy' if self.running else 'stopped',
            'agent_type': 'developer',
            'capabilities': [
                'code_generation',
                'bug_fixing',
                'feature_implementation',
                'code_review',
                'testing',
                'documentation'
            ],
            'supported_languages': [
                'python',
                'javascript',
                'typescript',
                'java',
                'go',
                'rust',
                'php',
                'ruby',
                'c#',
                'c++',
                'html',
                'css',
                'sql'
            ]
        }

async def main():
    """Main entry point"""
    agent_runner = DeveloperAgentRunner()
    
    try:
        # Setup signal handlers for graceful shutdown
        import signal
        
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            asyncio.create_task(agent_runner.stop())
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Start the agent
        await agent_runner.start()
        
        # Keep running until stopped
        while agent_runner.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        await agent_runner.stop()

if __name__ == "__main__":
    asyncio.run(main())