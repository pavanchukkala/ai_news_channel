import os
# Force HF Inference Endpoint to use the router
os.environ["HF_INFERENCE_ENDPOINT"] = "https://router.huggingface.co"

# Globally disable IPv6 for urllib3 to prevent NameResolutionError on environments with broken IPv6 DNS lookup
try:
    import urllib3.util.connection as urllib3_cn
    urllib3_cn.HAS_IPV6 = False
except ImportError:
    pass

import logging
from PIL import Image
import io
from huggingface_hub import InferenceClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VisualEngine:
    def __init__(self):
        self.hf_token = os.environ.get("HUGGINGFACE_API_KEY")
        self.client = InferenceClient(token=self.hf_token)
        
    def generate_image(self, prompt, output_path):
        logging.info(f"Generating image for prompt: {prompt[:50]}...")
        if not self.hf_token:
            logging.warning("No HUGGINGFACE_API_KEY. Using placeholder image.")
            self._create_placeholder(output_path)
            return output_path
            
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Use client.text_to_image which routes correctly
                image = self.client.text_to_image(prompt, model="black-forest-labs/FLUX.1-dev")
                
                # Ensure 16:9 aspect ratio by cropping
                width, height = image.size
                new_height = int(width * (9/16))
                top = (height - new_height) // 2
                bottom = top + new_height
                image = image.crop((0, top, width, bottom))
                
                image.save(output_path)
                logging.info(f"Image saved to {output_path}")
                return output_path
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} Exception generating image: {e}")
                if attempt < max_retries - 1:
                    time.sleep(10)
                else:
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
