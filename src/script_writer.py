import os
import json
import logging
from huggingface_hub import InferenceClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ScriptWriter:
    def __init__(self):
        self.hf_token = os.environ.get("HUGGINGFACE_API_KEY")
        if not self.hf_token:
            logging.warning("HUGGINGFACE_API_KEY not set. Script generation may fail.")
        # Using Qwen2.5-72B-Instruct as it's the latest flagship Qwen model usually available on HF Inference API
        self.client = InferenceClient(
            model="Qwen/Qwen2.5-72B-Instruct",
            token=self.hf_token
        )

    def generate_script(self, news_items):
        logging.info("Generating script from news items...")
        
        if not news_items:
            raise ValueError("No news items provided for script generation.")
            
        context = json.dumps(news_items, indent=2)
        
        prompt = f"""
You are a world-class AI systems architect and YouTube media analyst.
Your task is to write a highly engaging, 5-10 minute YouTube video script about the following AI news.

DO NOT just summarize. Provide original analysis, predictions, implications, and storytelling.
The script must never sound robotic or AI-generated. It must feel like a professional analyst speaking naturally.

Structure the script into scenes. For each scene, provide the narrator text and a highly detailed image generation prompt (for FLUX.1 Dev) that visually represents the scene.
Avoid generic robots in image prompts. Use specific, cinematic, and relevant imagery (e.g., datacenters, GPUs, software workflows).

Here is the news context:
{context}

OUTPUT FORMAT (JSON ONLY):
{{
  "title": "Proposed Video Title",
  "scenes": [
    {{
      "id": 1,
      "narrator_text": "The spoken text for this scene...",
      "image_prompt": "Ultra-detailed, cinematic, photorealistic image of..."
    }}
  ]
}}
Ensure the output is valid JSON.
"""
        try:
            response = self.client.text_generation(
                prompt,
                max_new_tokens=4000,
                temperature=0.7,
                return_full_text=False
            )
            
            # Clean up potential markdown formatting in JSON response
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
                
            script_data = json.loads(cleaned_response.strip())
            logging.info(f"Successfully generated script with {len(script_data.get('scenes', []))} scenes.")
            return script_data
            
        except Exception as e:
            logging.error(f"Failed to generate script: {e}")
            raise

if __name__ == "__main__":
    writer = ScriptWriter()
    test_news = [{"title": "OpenAI releases new model", "summary": "OpenAI has announced a breakthrough in reasoning models.", "source": "test"}]
    # print(json.dumps(writer.generate_script(test_news), indent=2))
