"""
Example client usage for WaveQ SDK
"""

import sys
from pathlib import Path

# Add waveq to path (in production, install via pip)
sys.path.insert(0, str(Path(__file__).parent.parent))

from waveq import WaveQClient
from waveq.exceptions import WaveQException


def main():
    """Example usage of WaveQ SDK"""
    
    # Initialize client with API key
    api_key = "waveq_demo_key_123"  # Replace with your actual API key
    client = WaveQClient(
        api_key=api_key,
        base_url="http://localhost:8000"
    )
    
    print("=" * 60)
    print("WaveQ AI Audio Agent SDK - Example Client")
    print("=" * 60)
    
    try:
        # Example 1: Denoise Audio
        print("\n1. Denoising audio...")
        audio_file = "path/to/noisy_audio.wav"  # Replace with actual file
        
        # Note: This will fail without actual file, showing example only
        try:
            result = client.denoise_audio(
                audio=audio_file,
                noise_reduction_level=0.8,
                enhance_speech=True
            )
            print(f"   Task ID: {result.task_id}")
            print(f"   Status: {result.status}")
        except Exception as e:
            print(f"   (Example only - file not found: {e})")
        
        # Example 2: Transcribe Audio with Diarization
        print("\n2. Transcribing audio with speaker diarization...")
        try:
            result = client.transcribe_audio(
                audio="path/to/meeting.mp3",
                enable_diarization=True,
                language="en",
                model="base"
            )
            print(f"   Task ID: {result.task_id}")
            print(f"   Status: {result.status}")
        except Exception as e:
            print(f"   (Example only - file not found: {e})")
        
        # Example 3: Smart Trimming
        print("\n3. Smart trimming and silence removal...")
        try:
            result = client.trim_audio(
                audio="path/to/audio.wav",
                silence_threshold_db=-40.0,
                min_silence_duration=0.5,
                remove_silence=True
            )
            print(f"   Task ID: {result.task_id}")
            print(f"   Status: {result.status}")
        except Exception as e:
            print(f"   (Example only - file not found: {e})")
        
        # Example 4: Source Separation
        print("\n4. Separating vocals from music...")
        try:
            result = client.separate_audio(
                audio="path/to/song.mp3",
                separation_type="vocals",
                model="htdemucs"
            )
            print(f"   Task ID: {result.task_id}")
            print(f"   Status: {result.status}")
        except Exception as e:
            print(f"   (Example only - file not found: {e})")
        
        # Example 5: Sentiment Analysis
        print("\n5. Analyzing audio sentiment...")
        try:
            result = client.analyze_sentiment(
                audio="path/to/speech.wav",
                include_emotions=True,
                confidence_threshold=0.5
            )
            print(f"   Task ID: {result.task_id}")
            print(f"   Status: {result.status}")
        except Exception as e:
            print(f"   (Example only - file not found: {e})")
        
        # Example 6: Text-to-Speech
        print("\n6. Converting text to speech...")
        result = client.text_to_speech(
            text="Hello! This is a demo of the WaveQ text-to-speech system.",
            language="en",
            speed=1.0
        )
        print(f"   Task ID: {result.task_id}")
        print(f"   Status: {result.status}")
        
        # Example 7: Check Task Status
        print("\n7. Checking task status...")
        task_status = client.get_task_status(result.task_id)
        print(f"   Task: {task_status.task_id}")
        print(f"   Status: {task_status.status}")
        
        # Example 8: Using Context Manager
        print("\n8. Using context manager...")
        with WaveQClient(api_key=api_key) as client:
            result = client.text_to_speech(
                text="Using context manager for automatic cleanup.",
                language="en"
            )
            print(f"   Task created: {result.task_id}")
        
        print("\n" + "=" * 60)
        print("Examples completed!")
        print("=" * 60)
        
    except WaveQException as e:
        print(f"\nWaveQ Error: {e.message}")
        if e.status_code:
            print(f"Status Code: {e.status_code}")
    except Exception as e:
        print(f"\nUnexpected Error: {e}")


if __name__ == "__main__":
    main()
