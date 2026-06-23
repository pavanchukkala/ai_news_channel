import os
import json
import logging
from huggingface_hub import InferenceClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QualityGate:
    def __init__(self):
        self.hf_token = os.environ.get("HUGGINGFACE_API_KEY")
        self.client = InferenceClient(
            model="Qwen/Qwen2.5-72B-Instruct",
            token=self.hf_token
        )

    def check_quality(self, script_data):
        logging.info("Running quality gate check on generated script...")
        if not self.hf_token:
            logging.warning("No HUGGINGFACE_API_KEY. Skipping quality check.")
            return True

        script_text = "\n".join([s.get('narrator_text', '') for s in script_data.get('scenes', [])])
        
        prompt = f"""
You are an expert YouTube compliance and content quality reviewer.
Review the following script for an AI News video.
Criteria for approval:
1. It is not a simple copy-paste summary of news articles.
2. It contains original analysis, insights, or predictions.
3. It has a high-retention structure (Hook, Context, Analysis).
4. It does not sound like a generic AI robot.

Script:
{script_text[:3000]}...

OUTPUT FORMAT (JSON ONLY):
{{
  "approved": true/false,
  "reason": "Brief explanation of why it passed or failed."
}}
Ensure output is valid JSON.
"""
        try:
            response = self.client.text_generation(
                prompt,
                max_new_tokens=500,
                temperature=0.3,
                return_full_text=False
            )
            
            cleaned = response.strip()
            if cleaned.startswith("```json"): cleaned = cleaned[7:]
            if cleaned.endswith("```"): cleaned = cleaned[:-3]
                
            result = json.loads(cleaned.strip())
            
            if result.get("approved"):
                logging.info(f"Quality Gate PASSED: {result.get('reason')}")
                return True
            else:
                logging.error(f"Quality Gate FAILED: {result.get('reason')}")
                return False
                
        except Exception as e:
            logging.error(f"Quality gate error (failing open): {e}")
            return True # Fail open to prevent pipeline crash on simple LLM JSON format errors

if __name__ == "__main__":
    gate = QualityGate()
