import os
import sys
import logging
from news_fetcher import NewsFetcher
from script_writer import ScriptWriter
from visual_engine import VisualEngine
from audio_engine import AudioEngine
from video_renderer import VideoRenderer
from seo_engine import SEOEngine
from quality_gate import QualityGate
from youtube_uploader import YouTubeUploader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Starting AI News YouTube Pipeline...")
    
    # 1. Fetch News
    fetcher = NewsFetcher()
    news_items = fetcher.fetch_news()
    if not news_items:
        logging.error("No relevant news found today. Exiting.")
        sys.exit(0)
        
    # 2. Write Script
    writer = ScriptWriter()
    script_data = writer.generate_script(news_items)
    
    # 3. Quality Gate
    gate = QualityGate()
    if not gate.check_quality(script_data):
        logging.error("Script failed quality gate. Exiting to prevent low-quality upload.")
        sys.exit(1)
        
    # 4. Generate SEO Metadata
    seo = SEOEngine()
    seo_data = seo.generate_seo_metadata(script_data)
    
    # 5. Visual and Audio Generation
    visual_engine = VisualEngine()
    audio_engine = AudioEngine()
    renderer = VideoRenderer()
    
    scene_files = []
    
    for i, scene in enumerate(script_data.get('scenes', [])):
        img_prompt = scene.get('image_prompt', 'AI technology background')
        text = scene.get('narrator_text', '')
        
        img_path = f"output/raw_img_{i}.png"
        audio_path = f"output/raw_audio_{i}.wav"
        
        # Generate Image
        visual_engine.generate_image(img_prompt, img_path)
        
        # Generate Audio
        audio_engine.generate_audio(text, audio_path)
        
        # Render Scene (combine image + audio + zoompan)
        scene_mp4 = renderer.render_scene(img_path, audio_path, i)
        if scene_mp4:
            scene_files.append(scene_mp4)
            
    # 6. Final Concatenation
    final_video = renderer.concatenate_scenes(scene_files)
    if not final_video:
        logging.error("Failed to render final video.")
        sys.exit(1)
        
    # 7. Upload to YouTube
    # Only upload if credentials exist, otherwise just save locally
    if os.environ.get("YOUTUBE_REFRESH_TOKEN"):
        uploader = YouTubeUploader()
        thumbnail_path = "output/raw_img_0.png" # Simple fallback thumbnail
        video_id = uploader.upload_video(final_video, seo_data, thumbnail_path)
        if video_id:
            logging.info(f"Pipeline completed successfully. Video uploaded: https://youtube.com/watch?v={video_id}")
        else:
            logging.error("Pipeline completed but upload failed.")
    else:
        logging.info(f"Pipeline completed successfully. Video saved locally at {final_video}. (YouTube credentials not set)")

if __name__ == "__main__":
    main()
