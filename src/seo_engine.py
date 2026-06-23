import os
import json
import logging
from huggingface_hub import InferenceClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SEOEngine:
    def __init__(self):
        self.hf_token = os.environ.get("HUGGINGFACE_API_KEY")
        self.client = InferenceClient(
            model="Qwen/Qwen2.5-7B-Instruct",
            token=self.hf_token
        )

    def generate_seo_metadata(self, script_data):
        logging.info("Generating SEO metadata...")
        
        if not self.hf_token:
            logging.warning("No HUGGINGFACE_API_KEY. Using default SEO data.")
            return self._default_seo()
            
        prompt = f"""
You are an expert YouTube SEO strategist.
Based on the following video script data, generate high-CTR and algorithm-friendly SEO metadata.
The metadata should target search traffic and suggested videos.

Video Title Idea: {script_data.get('title')}
First Scene Text: {script_data.get('scenes', [{{}}])[0].get('narrator_text', '')}

OUTPUT FORMAT (JSON ONLY):
{{
  "title": "A highly clickable, emotionally triggering YouTube title (under 70 chars)",
  "description": "A 3-paragraph SEO-optimized description with timestamps and links.",
  "tags": ["tag1", "tag2", "tag3"],
  "hashtags": ["#AI", "#Tech"],
  "pinned_comment": "An engaging question to ask viewers in the pinned comment.",
  "thumbnail_prompt": "A specific prompt for an AI image generator to create a high-CTR, curiosity-inducing thumbnail."
}}
Ensure the output is valid JSON.
"""
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.text_generation(
                    prompt,
                    max_new_tokens=1500,
                    temperature=0.7,
                    return_full_text=False
                )
                
                cleaned_response = response.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]
                    
                seo_data = json.loads(cleaned_response.strip())
                logging.info("SEO metadata generated successfully.")
                return seo_data
                
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed to generate SEO: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    logging.error("Max retries reached. Using default SEO data.")
                    return self._default_seo()

    def _default_seo(self):
        return {
            "title": "Latest AI News Updates",
            "description": "The latest updates in Artificial Intelligence.",
            "tags": ["AI", "Artificial Intelligence", "Technology"],
            "hashtags": ["#AI"],
            "pinned_comment": "What do you think about these updates?",
            "thumbnail_prompt": "A futuristic glowing AI brain, cinematic lighting."
        }

if __name__ == "__main__":
    seo = SEOEngine()
