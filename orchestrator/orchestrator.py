"""
AI Orchestrator for workflow management and intent classification
"""

import logging
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class WorkflowIntent(str, Enum):
    """Detected workflow intents"""
    PODCAST_PRODUCTION = "podcast_production"
    VOICE_ENHANCEMENT = "voice_enhancement"
    MUSIC_PRODUCTION = "music_production"
    TRANSCRIPTION_ONLY = "transcription_only"
    VOICE_CLONING = "voice_cloning"
    CUSTOM = "custom"


class Orchestrator:
    """
    AI Agent that classifies intent and orchestrates audio processing workflows
    
    The orchestrator analyzes the incoming request and determines the optimal
    sequence of audio processing steps based on the detected intent and context.
    """
    
    def __init__(self):
        self.workflow_definitions = self._load_workflow_definitions()
    
    def _load_workflow_definitions(self) -> Dict[str, List[str]]:
        """Load predefined workflow definitions"""
        return {
            WorkflowIntent.PODCAST_PRODUCTION: [
                "denoise",
                "trim",
                "transcribe",
                "sentiment",
            ],
            WorkflowIntent.VOICE_ENHANCEMENT: [
                "denoise",
                "trim",
            ],
            WorkflowIntent.MUSIC_PRODUCTION: [
                "separate",
                "denoise",
            ],
            WorkflowIntent.TRANSCRIPTION_ONLY: [
                "transcribe",
            ],
            WorkflowIntent.VOICE_CLONING: [
                "denoise",
                "tts",
            ],
        }
    
    def classify_intent(
        self,
        audio_metadata: Dict[str, Any],
        user_hints: Optional[Dict[str, Any]] = None
    ) -> WorkflowIntent:
        """
        Classify the intent based on audio metadata and user hints
        
        Args:
            audio_metadata: Information about the audio file
            user_hints: Optional hints from the user about desired processing
            
        Returns:
            Detected workflow intent
        """
        # Simple rule-based classification (can be replaced with ML model)
        if user_hints:
            requested_operation = user_hints.get("operation")
            
            if requested_operation == "transcribe":
                return WorkflowIntent.TRANSCRIPTION_ONLY
            elif requested_operation == "separate":
                return WorkflowIntent.MUSIC_PRODUCTION
            elif requested_operation == "tts":
                return WorkflowIntent.VOICE_CLONING
        
        # Default to voice enhancement for speech audio
        file_duration = audio_metadata.get("duration", 0)
        
        if file_duration > 300:  # > 5 minutes, likely podcast
            return WorkflowIntent.PODCAST_PRODUCTION
        else:
            return WorkflowIntent.VOICE_ENHANCEMENT
    
    def create_workflow(
        self,
        intent: WorkflowIntent,
        customizations: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Create a workflow plan based on intent
        
        Args:
            intent: Detected workflow intent
            customizations: Optional customizations to the workflow
            
        Returns:
            List of processing steps with configurations
        """
        workflow_steps = []
        operations = self.workflow_definitions.get(intent, ["denoise"])
        
        for operation in operations:
            step = {
                "operation": operation,
                "config": self._get_default_config(operation),
            }
            
            # Apply customizations if provided
            if customizations and operation in customizations:
                step["config"].update(customizations[operation])
            
            workflow_steps.append(step)
        
        logger.info(f"Created workflow for intent {intent}: {[s['operation'] for s in workflow_steps]}")
        return workflow_steps
    
    def _get_default_config(self, operation: str) -> Dict[str, Any]:
        """Get default configuration for an operation"""
        defaults = {
            "denoise": {
                "noise_reduction_level": 0.8,
                "enhance_speech": True,
            },
            "transcribe": {
                "enable_diarization": False,
                "timestamps": True,
                "model": "base",
            },
            "trim": {
                "silence_threshold_db": -40.0,
                "min_silence_duration": 0.5,
                "remove_silence": True,
            },
            "separate": {
                "separation_type": "vocals",
                "model": "htdemucs",
            },
            "sentiment": {
                "include_emotions": True,
                "confidence_threshold": 0.5,
            },
            "tts": {
                "language": "en",
                "speed": 1.0,
            },
        }
        
        return defaults.get(operation, {})
    
    def should_run_parallel(self, operation: str, next_operation: str) -> bool:
        """
        Determine if two operations can run in parallel
        
        Args:
            operation: Current operation
            next_operation: Next operation
            
        Returns:
            True if operations can run in parallel
        """
        # Transcribe and sentiment can run in parallel
        parallel_ops = {
            ("transcribe", "sentiment"),
            ("sentiment", "transcribe"),
        }
        
        return (operation, next_operation) in parallel_ops
    
    def optimize_workflow(
        self,
        workflow_steps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Optimize workflow by identifying parallelizable steps
        
        Args:
            workflow_steps: Original workflow steps
            
        Returns:
            Optimized workflow with parallel execution hints
        """
        optimized = []
        
        for i, step in enumerate(workflow_steps):
            optimized_step = step.copy()
            
            # Check if next step can run in parallel
            if i < len(workflow_steps) - 1:
                next_step = workflow_steps[i + 1]
                if self.should_run_parallel(step["operation"], next_step["operation"]):
                    optimized_step["parallel_with_next"] = True
            
            optimized.append(optimized_step)
        
        return optimized
    
    async def execute_workflow(
        self,
        workflow_steps: List[Dict[str, Any]],
        audio_file_path: str,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a complete workflow
        
        Args:
            workflow_steps: List of processing steps
            audio_file_path: Path to audio file
            callback_url: Optional callback URL for notifications
            
        Returns:
            Workflow execution results
        """
        results = {
            "workflow_id": f"workflow_{id(workflow_steps)}",
            "steps_completed": [],
            "outputs": {},
            "errors": [],
        }
        
        current_file = audio_file_path
        
        for step in workflow_steps:
            operation = step["operation"]
            config = step["config"]
            
            try:
                logger.info(f"Executing step: {operation}")
                
                # Here you would call the actual processing functions
                # For now, just record the step
                results["steps_completed"].append(operation)
                
                # Simulate output
                results["outputs"][operation] = {
                    "status": "completed",
                    "file_path": current_file,
                }
                
            except Exception as e:
                logger.error(f"Error in step {operation}: {e}")
                results["errors"].append({
                    "operation": operation,
                    "error": str(e),
                })
                break
        
        return results
