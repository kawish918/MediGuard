from huggingface_hub import InferenceClient
import os

client = InferenceClient(
    token=os.environ["HUGGINGFACEHUB_API_TOKEN"],
)

def medasr_transcribe(audio_path: str) -> str:
    """Transcribe medical audio using ASR models"""
    try:
        with open(audio_path, "rb") as f:
            result = client.automatic_speech_recognition(
                f.read(),
                model="openai/whisper-large-v3"
            )
        
        # Handle different response formats
        if isinstance(result, dict):
            return result.get("text", "")
        elif isinstance(result, str):
            return result
        else:
            return str(result)
            
    except Exception as e:
        print(f"Warning: Audio transcription failed ({e})")
        return "[Audio transcription unavailable]"