# Autonomous AI News YouTube System

A fully automated, zero-cost, production-grade AI News YouTube pipeline triggered daily via GitHub Actions.

This system collects the latest AI news, generates an engaging script using Qwen3, creates cinematic visuals using FLUX.1 Dev, generates natural voice narration using Kokoro TTS, edits the video with FFmpeg, and uploads it to YouTube directly.

## Features
- **Zero Cost**: Utilizes Hugging Face's Free Serverless Inference API and GitHub Actions.
- **Autonomous**: Runs daily on a cron schedule with zero manual intervention.
- **High Quality**: Uses top-tier models (Qwen2.5-72B-Instruct, FLUX.1 Dev, Kokoro TTS).
- **Monetization Safe**: Includes an LLM quality gate to ensure original analysis and compliance with YouTube guidelines.

## Architecture

1. **News Collection** (`news_fetcher.py`): Scrapes RSS feeds and filters top news.
2. **Script Generation** (`script_writer.py`): Qwen generates a 5-10 minute script with scene-by-scene prompts.
3. **Quality Gate** (`quality_gate.py`): Ensures the script is analytical, not just a summary.
4. **Visual Engine** (`visual_engine.py`): FLUX.1 generates 16:9 images for each scene.
5. **Audio Engine** (`audio_engine.py`): Kokoro TTS converts text to speech locally.
6. **Video Renderer** (`video_renderer.py`): FFmpeg stitches audio and images with a Ken Burns effect.
7. **SEO Engine** (`seo_engine.py`): Qwen generates high-CTR titles, descriptions, and tags.
8. **YouTube Uploader** (`youtube_uploader.py`): Uploads video and applies SEO metadata.

---

## Installation Guide (Local Testing)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai_news_channel.git
   cd ai_news_channel
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   sudo apt-get install -y ffmpeg espeak-ng  # Linux/WSL
   ```

3. Download Kokoro ONNX model files to the root directory:
   ```bash
   wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.onnx
   wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.json
   ```

4. Create a `.env` file in the root directory:
   ```env
   HUGGINGFACE_API_KEY=your_hf_token
   YOUTUBE_CLIENT_ID=your_client_id
   YOUTUBE_CLIENT_SECRET=your_client_secret
   YOUTUBE_REFRESH_TOKEN=your_refresh_token
   ```

5. Run locally:
   ```bash
   python src/main.py
   ```

---

## Deployment Guide (GitHub Actions)

To deploy this as a fully autonomous system, follow these steps:

### 1. Get a Hugging Face Token (Free)
1. Go to [Hugging Face](https://huggingface.co/) and create a free account.
2. Go to **Settings > Access Tokens** and create a new **Write** token.

### 2. Get YouTube API Credentials
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project and enable the **YouTube Data API v3**.
3. Go to **Credentials** -> **Create Credentials** -> **OAuth client ID**.
4. Set Application type to **Desktop app**.
5. Download the JSON. You have your `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET`.
6. Use a tool like [google-oauth2-tool](https://github.com/google/oauth2l) or write a quick script to authenticate once locally and get your `YOUTUBE_REFRESH_TOKEN`.

### 3. Configure GitHub Secrets
1. Push this code to a new private GitHub repository.
2. Go to your repository **Settings > Secrets and variables > Actions**.
3. Add the following repository secrets:
   - `HUGGINGFACE_API_KEY`
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`
   - `YOUTUBE_REFRESH_TOKEN`

### 4. Enable GitHub Actions
The pipeline is defined in `.github/workflows/daily_video_pipeline.yml`. It will run automatically every day at 8:00 AM UTC. You can also trigger it manually from the "Actions" tab.

---

## Monitoring and Scaling Guide

### Monitoring
- **GitHub Actions Logs**: If the pipeline fails, GitHub Actions will send you an email. You can check the detailed logs in the Actions tab.
- **Artifacts**: If the pipeline fails mid-render, it uploads the `output/` folder as a ZIP artifact so you can debug generated images or audio.

### Error Handling & Fallbacks
- If FLUX.1 fails (due to HF rate limits), it falls back to a black placeholder image to prevent pipeline crashes.
- If Kokoro TTS fails, it creates 1 second of silence.
- If the LLM output is malformed, the pipeline fails gracefully.

### Scaling Up
If you eventually decide to scale and spend money for higher quality or speed:
1. **Self-Hosted Runners**: Connect a PC with an RTX 4090 to GitHub Actions to run FLUX and Qwen locally.
2. **Paid APIs**: Swap Hugging Face Free API with Together AI (for faster Qwen inference) and Replicate (for faster FLUX inference).
3. **Upscaling**: Add an integration with Real-ESRGAN or Topaz Video AI in the rendering step.
