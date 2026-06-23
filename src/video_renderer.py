import os
import logging
import ffmpeg
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VideoRenderer:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def render_scene(self, image_path, audio_path, scene_index):
        logging.info(f"Rendering scene {scene_index}...")
        out_path = os.path.join(self.output_dir, f"scene_{scene_index}.mp4")
        
        try:
            # Probe audio duration
            probe = ffmpeg.probe(audio_path)
            duration = float(probe['format']['duration'])
            
            # Create a simple Ken Burns effect using FFmpeg filters
            # Zoom in slowly over the duration of the audio
            # Scale to 1920x1080, zoom in by 1.1x slowly
            
            in_image = ffmpeg.input(image_path, loop=1, t=duration)
            in_audio = ffmpeg.input(audio_path)
            
            # Simple zoompan
            v = in_image.filter('zoompan', z='min(zoom+0.0015,1.1)', d=int(duration*25), s='1920x1080', fps=25)
            
            (
                ffmpeg
                .concat(v, in_audio, v=1, a=1)
                .output(out_path, vcodec='libx264', acodec='aac', pix_fmt='yuv420p', shortest=None)
                .overwrite_output()
                .run(quiet=True)
            )
            logging.info(f"Scene {scene_index} rendered: {out_path}")
            return out_path
            
        except Exception as e:
            logging.error(f"Error rendering scene {scene_index}: {e}")
            return None

    def concatenate_scenes(self, scene_files, final_output="final_video.mp4"):
        logging.info("Concatenating all scenes...")
        if not scene_files:
            logging.error("No scene files to concatenate.")
            return None
            
        list_file = os.path.join(self.output_dir, "scenes_list.txt")
        with open(list_file, 'w') as f:
            for sf in scene_files:
                # FFmpeg requires specific path formatting for concat demuxer
                f.write(f"file '{os.path.abspath(sf)}'\n")
                
        out_path = os.path.join(self.output_dir, final_output)
        
        try:
            (
                ffmpeg
                .input(list_file, format='concat', safe=0)
                .output(out_path, c='copy')
                .overwrite_output()
                .run(quiet=True)
            )
            logging.info(f"Final video rendered successfully at {out_path}")
            return out_path
        except Exception as e:
            logging.error(f"Error concatenating scenes: {e}")
            return None

if __name__ == "__main__":
    renderer = VideoRenderer()
    # renderer.render_scene("test_img.png", "test_audio.wav", 1)
