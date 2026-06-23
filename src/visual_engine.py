import os
import requests
import logging
from PIL import Image
import io

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VisualEngine:
    def __init__(self):
        self.hf_token = os.environ.get("HUGGINGFACE_API_KEY")
        # Using FLUX.1-schnell or dev depending on API availability/speed
        self.api_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
        self.headers = {"Authorization": f"Bearer {self.hf_token}"}
        
    def generate_image(self, prompt, output_path):
        logging.info(f"Generating image for prompt: {prompt[:50]}...")
        if not self.hf_token:
            logging.warning("No HUGGINGFACE_API_KEY. Using placeholder image.")
            self._create_placeholder(output_path)
            return output_path
            
        payload = {"inputs": prompt, "parameters": {"num_inference_steps": 25, "guidance_scale": 7.5}}
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=120)
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                # Ensure 16:9 aspect ratio by cropping or generating at specific resolution if API supports it
                # FLUX outputs 1024x1024 by default via standard HF API unless resolution is specified.
                # Let's crop it to 16:9 (1024x576) for YouTube
                width, height = image.size
                new_height = int(width * (9/16))
                top = (height - new_height) // 2
                bottom = top + new_height
                image = image.crop((0, top, width, bottom))
                
                image.save(output_path)
                logging.info(f"Image saved to {output_path}")
                return output_path
            else:
                logging.error(f"Image API Error: {response.status_code} - {response.text}")
                self._create_placeholder(output_path)
                return output_path
        except Exception as e:
            logging.error(f"Exception generating image: {e}")
            self._create_placeholder(output_path)
            return output_path

    def _create_placeholder(self, output_path):
        # Create a black 1920x1080 image as fallback
        img = Image.new('RGB', (1920, 1080), color = 'black')
        img.save(output_path)
        logging.info(f"Created placeholder image at {output_path}")

if __name__ == "__main__":
    engine = VisualEngine()
    # engine.generate_image("A futuristic data center glowing with neon blue lights, ultra detailed", "test_img.png")
