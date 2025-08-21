"""
Developer Agent Core
Main AI logic for development tasks
"""

import asyncio
import json
import os
import tempfile
from typing import Dict, List, Optional, Any
from pathlib import Path

import openai
import google.generativeai as genai
from git import Repo
from github import Github

from config import AgentConfig
from utils.code_analyzer import CodeAnalyzer
from utils.project_manager import ProjectManager
from utils.logger import get_logger

logger = get_logger(__name__)

class DeveloperAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.openai_client = None
        self.gemini_client = None
        self.github_client = None
        self.code_analyzer = CodeAnalyzer()
        self.project_manager = ProjectManager()
        
    async def initialize(self):
        """Initialize AI clients and tools"""
        try:
            # Initialize OpenAI client
            if self.config.openai_api_key:
                self.openai_client = openai.OpenAI(
                    api_key=self.config.openai_api_key
                )
                logger.info("OpenAI client initialized")
            
            # Initialize Gemini client
            if self.config.gemini_api_key:
                genai.configure(api_key=self.config.gemini_api_key)
                self.gemini_client = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini client initialized")
            
            # Initialize GitHub client
            if self.config.github_token:
                self.github_client = Github(self.config.github_token)
                logger.info("GitHub client initialized")
                
        except Exception as e:
            logger.error(f"Failed to initialize AI clients: {e}")
            raise

    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a development task"""
        task_type = task_data.get('type', 'unknown')
        task_id = task_data.get('id', 'unknown')
        
        logger.info(f"Processing {task_type} task: {task_id}")
        
        try:
            if task_type == 'code_generation':
                result = await self._handle_code_generation(task_data)
            elif task_type == 'bug_fix':
                result = await self._handle_bug_fix(task_data)
            elif task_type == 'feature_implementation':
                result = await self._handle_feature_implementation(task_data)
            elif task_type == 'code_review':
                result = await self._handle_code_review(task_data)
            elif task_type == 'test_generation':
                result = await self._handle_test_generation(task_data)
            elif task_type == 'documentation':
                result = await self._handle_documentation(task_data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            return {
                'task_id': task_id,
                'status': 'completed',
                'result': result,
                'agent_type': 'developer',
                'timestamp': self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {e}")
            raise

    async def _handle_code_generation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on requirements"""
        requirements = task_data.get('requirements', '')
        language = task_data.get('language', 'python')
        framework = task_data.get('framework', '')
        
        # Create prompt for code generation
        prompt = self._create_code_generation_prompt(requirements, language, framework)
        
        # Generate code using AI
        generated_code = await self._generate_with_ai(prompt)
        
        # Analyze and improve the code
        analyzed_code = await self.code_analyzer.analyze_and_improve(
            generated_code, 
            language
        )
        
        return {
            'generated_code': analyzed_code,
            'language': language,
            'framework': framework,
            'files_created': self._extract_files_from_code(analyzed_code),
            'recommendations': await self._get_code_recommendations(analyzed_code, language)
        }

    async def _handle_bug_fix(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix bugs in existing code"""
        bug_description = task_data.get('bug_description', '')
        code_snippet = task_data.get('code', '')
        error_logs = task_data.get('error_logs', '')
        
        # Analyze the bug
        bug_analysis = await self._analyze_bug(bug_description, code_snippet, error_logs)
        
        # Generate fix
        fixed_code = await self._generate_bug_fix(bug_analysis, code_snippet)
        
        return {
            'bug_analysis': bug_analysis,
            'fixed_code': fixed_code,
            'explanation': bug_analysis.get('explanation', ''),
            'test_suggestions': await self._suggest_tests_for_fix(fixed_code)
        }

    async def _handle_feature_implementation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement new features"""
        feature_description = task_data.get('feature_description', '')
        existing_codebase = task_data.get('existing_code', '')
        architecture = task_data.get('architecture', {})
        
        # Plan the feature implementation
        implementation_plan = await self._plan_feature_implementation(
            feature_description, 
            existing_codebase, 
            architecture
        )
        
        # Implement the feature
        feature_code = await self._implement_feature(implementation_plan)
        
        return {
            'implementation_plan': implementation_plan,
            'feature_code': feature_code,
            'integration_points': implementation_plan.get('integration_points', []),
            'testing_strategy': implementation_plan.get('testing_strategy', {})
        }

    async def _handle_code_review(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Review code for quality and best practices"""
        code_to_review = task_data.get('code', '')
        language = task_data.get('language', 'python')
        review_type = task_data.get('review_type', 'comprehensive')
        
        # Perform code review
        review_result = await self._perform_code_review(
            code_to_review, 
            language, 
            review_type
        )
        
        return review_result

    async def _handle_test_generation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tests for code"""
        code_to_test = task_data.get('code', '')
        language = task_data.get('language', 'python')
        test_framework = task_data.get('test_framework', 'pytest')
        
        # Generate tests
        generated_tests = await self._generate_tests(
            code_to_test, 
            language, 
            test_framework
        )
        
        return {
            'generated_tests': generated_tests,
            'test_framework': test_framework,
            'coverage_analysis': await self._analyze_test_coverage(generated_tests, code_to_test)
        }

    async def _handle_documentation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation"""
        code_to_document = task_data.get('code', '')
        doc_type = task_data.get('doc_type', 'api')  # api, user, technical
        format_type = task_data.get('format', 'markdown')
        
        # Generate documentation
        documentation = await self._generate_documentation(
            code_to_document, 
            doc_type, 
            format_type
        )
        
        return {
            'documentation': documentation,
            'doc_type': doc_type,
            'format': format_type
        }

    async def _generate_with_ai(self, prompt: str, model: str = 'gpt-4') -> str:
        """Generate response using AI model"""
        try:
            if model.startswith('gpt') and self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an expert software developer."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=4000
                )
                return response.choices[0].message.content
                
            elif model.startswith('gemini') and self.gemini_client:
                response = self.gemini_client.generate_content(prompt)
                return response.text
                
            else:
                raise ValueError("No suitable AI model available")
                
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            raise

    def _create_code_generation_prompt(self, requirements: str, language: str, framework: str) -> str:
        """Create prompt for code generation"""
        return f"""
        Generate high-quality {language} code that meets the following requirements:

        Requirements: {requirements}
        Language: {language}
        Framework: {framework}

        Please provide:
        1. Clean, well-structured code
        2. Proper error handling
        3. Comprehensive comments
        4. Following best practices for {language}
        5. Unit tests where appropriate

        Format the response with clear file separations and explanations.
        """

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    def _extract_files_from_code(self, code: str) -> List[str]:
        """Extract file names from generated code"""
        # This is a simplified implementation
        # In practice, you'd parse the code structure more carefully
        import re
        
        file_patterns = [
            r'# File: ([^\n]+)',
            r'// File: ([^\n]+)',
            r'<!-- File: ([^\n]+)',
        ]
        
        files = []
        for pattern in file_patterns:
            matches = re.findall(pattern, code)
            files.extend(matches)
        
        return files

    async def _get_code_recommendations(self, code: str, language: str) -> List[str]:
        """Get recommendations for improving code"""
        # Simplified implementation
        recommendations = [
            "Consider adding more comprehensive error handling",
            "Add logging for better debugging",
            "Implement proper input validation",
            f"Follow {language} coding standards and conventions",
            "Add performance optimizations where applicable"
        ]
        return recommendations

    async def _analyze_bug(self, description: str, code: str, logs: str) -> Dict[str, Any]:
        """Analyze a bug and provide insights"""
        prompt = f"""
        Analyze the following bug:
        
        Description: {description}
        Code: {code}
        Error Logs: {logs}
        
        Provide:
        1. Root cause analysis
        2. Affected components
        3. Potential fix strategies
        4. Prevention measures
        """
        
        analysis = await self._generate_with_ai(prompt)
        
        return {
            'analysis': analysis,
            'severity': 'medium',  # This could be determined by AI
            'category': 'logic',   # This could be categorized by AI
            'explanation': analysis
        }

    async def _generate_bug_fix(self, analysis: Dict[str, Any], code: str) -> str:
        """Generate a fix for the bug"""
        prompt = f"""
        Based on the analysis: {analysis.get('analysis', '')}
        
        Fix the following code:
        {code}
        
        Provide the corrected code with explanations of changes made.
        """
        
        return await self._generate_with_ai(prompt)