"""
Audio Sentiment Analysis
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from transformers import pipeline
import torch

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Audio sentiment analysis combining speech-to-text and NLP
    
    Transcribes audio and analyzes the emotional content and sentiment
    using transformer models.
    """
    
    def __init__(self, device: str = "cpu"):
        """
        Initialize the sentiment analyzer
        
        Args:
            device: Device to run on (cpu or cuda)
        """
        self.device = device
        self.sentiment_model = None
        self.emotion_model = None
        
        # Import transcriber
        from audio_tools.transcription import AudioTranscriber
        self.transcriber = AudioTranscriber(model_name="base", device=device)
    
    def _load_models(self):
        """Lazy load sentiment analysis models"""
        if self.sentiment_model is None:
            logger.info("Loading sentiment analysis model...")
            self.sentiment_model = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=0 if self.device == "cuda" else -1,
            )
        
        if self.emotion_model is None:
            logger.info("Loading emotion detection model...")
            # Using a more detailed emotion model
            try:
                self.emotion_model = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    device=0 if self.device == "cuda" else -1,
                    top_k=None,
                )
            except Exception as e:
                logger.warning(f"Could not load emotion model: {e}")
                self.emotion_model = None
    
    def analyze(
        self,
        audio_path: Path,
        include_emotions: bool = True,
        confidence_threshold: float = 0.5,
        transcript: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze sentiment in audio
        
        Args:
            audio_path: Path to audio file
            include_emotions: Include detailed emotion detection
            confidence_threshold: Minimum confidence for predictions
            transcript: Optional pre-computed transcript
            
        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            logger.info(f"Analyzing sentiment: {audio_path}")
            
            # Get transcript if not provided
            if transcript is None:
                logger.info("Transcribing audio...")
                transcription_result = self.transcriber.transcribe(
                    audio_path,
                    enable_diarization=False,
                    timestamps=False,
                )
                
                if transcription_result["status"] != "success":
                    return {
                        "status": "failed",
                        "error": "Transcription failed",
                    }
                
                transcript = transcription_result["transcript"]
            
            if not transcript or len(transcript.strip()) == 0:
                return {
                    "status": "failed",
                    "error": "Empty transcript",
                }
            
            # Load models
            self._load_models()
            
            # Analyze sentiment
            sentiment_result = self.sentiment_model(transcript)[0]
            sentiment_label = sentiment_result["label"].lower()
            sentiment_score = sentiment_result["score"]
            
            # Map labels
            if sentiment_label in ["positive", "pos"]:
                sentiment = "positive"
            elif sentiment_label in ["negative", "neg"]:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            result = {
                "status": "success",
                "sentiment": sentiment,
                "sentiment_score": sentiment_score,
                "transcript": transcript,
            }
            
            # Analyze emotions if requested
            if include_emotions and self.emotion_model is not None:
                logger.info("Analyzing emotions...")
                emotion_results = self.emotion_model(transcript)[0]
                
                # Filter by confidence threshold
                emotions = {
                    item["label"]: item["score"]
                    for item in emotion_results
                    if item["score"] >= confidence_threshold
                }
                
                # Sort by score
                emotions = dict(
                    sorted(emotions.items(), key=lambda x: x[1], reverse=True)
                )
                
                result["emotions"] = emotions
                
                if emotions:
                    result["dominant_emotion"] = list(emotions.keys())[0]
            
            logger.info(f"Sentiment: {sentiment} ({sentiment_score:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
            }
    
    def analyze_text(
        self,
        text: str,
        include_emotions: bool = True,
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of text directly
        
        Args:
            text: Text to analyze
            include_emotions: Include emotion detection
            
        Returns:
            Dictionary with sentiment analysis
        """
        try:
            # Load models
            self._load_models()
            
            # Analyze
            sentiment_result = self.sentiment_model(text)[0]
            sentiment = sentiment_result["label"].lower()
            score = sentiment_result["score"]
            
            result = {
                "status": "success",
                "sentiment": sentiment,
                "sentiment_score": score,
            }
            
            if include_emotions and self.emotion_model is not None:
                emotion_results = self.emotion_model(text)[0]
                emotions = {
                    item["label"]: item["score"]
                    for item in emotion_results
                }
                result["emotions"] = emotions
            
            return result
            
        except Exception as e:
            logger.error(f"Text sentiment analysis failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
            }
