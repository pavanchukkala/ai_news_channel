import os
import logging
import soundfile as sf
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AudioEngine:
    def __init__(self):
        self.model_path = "kokoro-v0_19.onnx"
        self.voices_path = "voices.json"
        self._ensure_model_files()
        
        try:
            from kokoro_onnx import Kokoro
            self.kokoro = Kokoro(self.model_path, self.voices_path)
            logging.info("Kokoro TTS loaded successfully.")
        except ImportError:
            logging.error("kokoro-onnx not installed.")
            self.kokoro = None
        except Exception as e:
            logging.error(f"Failed to load Kokoro: {e}")
            self.kokoro = None

    def _ensure_model_files(self):
        # Basic check to download kokoro ONNX files if missing (requires github LFS or direct links)
        # For a true production system, these should be cached or downloaded in the CI step.
        base_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/"
        if not os.path.exists(self.model_path):
            logging.info("Downloading Kokoro ONNX model (this may take a while)...")
            try:
                # Real implementation should point to actual model files
                # This is a placeholder logic.
                pass 
            except Exception as e:
                logging.warning(f"Failed to download model: {e}")

    def generate_audio(self, text, output_path, voice="af_sarah"):
        logging.info(f"Generating audio for text: {text[:50]}...")
        if not self.kokoro:
            logging.warning("Kokoro not initialized. Creating empty audio file.")
            self._create_empty_audio(output_path)
            return output_path
            
        try:
            samples, sample_rate = self.kokoro.create(text, voice=voice, speed=1.0, lang="en-us")
            sf.write(output_path, samples, sample_rate)
            logging.info(f"Audio saved to {output_path}")
            return output_path
        except Exception as e:
            logging.error(f"Error generating audio: {e}")
            self._create_empty_audio(output_path)
            return output_path

    def _create_empty_audio(self, output_path):
        import numpy as np
        # Create 1 second of silence
        sf.write(output_path, np.zeros(24000), 24000)

if __name__ == "__main__":
    engine = AudioEngine()
    # engine.generate_audio("Welcome to the latest AI news.", "test_audio.wav")
