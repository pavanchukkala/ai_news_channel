import os
import logging
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class YouTubeUploader:
    def __init__(self):
        self.client_secrets_file = "client_secret.json"
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        self.credentials = None

    def _authenticate(self):
        # In a fully autonomous GitHub Actions setup, we'd use a refresh token stored in GitHub Secrets.
        # This implementation expects `YOUTUBE_REFRESH_TOKEN`, `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET` in env vars.
        
        client_id = os.environ.get("YOUTUBE_CLIENT_ID")
        client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
        refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
        
        if not all([client_id, client_secret, refresh_token]):
            logging.error("Missing YouTube OAuth environment variables.")
            return False
            
        try:
            self.credentials = google.oauth2.credentials.Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=self.scopes
            )
            # Refresh the token
            self.credentials.refresh(Request())
            logging.info("YouTube authentication successful.")
            return True
        except Exception as e:
            logging.error(f"YouTube authentication failed: {e}")
            return False

    def upload_video(self, video_path, seo_data, thumbnail_path=None):
        logging.info("Preparing to upload video to YouTube...")
        if not self._authenticate():
            return False
            
        youtube = build("youtube", "v3", credentials=self.credentials)
        
        body = {
            "snippet": {
                "title": seo_data.get("title", "AI News"),
                "description": seo_data.get("description", ""),
                "tags": seo_data.get("tags", []),
                "categoryId": "28" # Science & Technology
            },
            "status": {
                "privacyStatus": "public", # Set to private for testing, public for prod
                "selfDeclaredMadeForKids": False
            }
        }
        
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        
        try:
            request = youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logging.info(f"Uploaded {int(status.progress() * 100)}%")
            
            video_id = response.get("id")
            logging.info(f"Video uploaded successfully! Video ID: {video_id}")
            
            if thumbnail_path and os.path.exists(thumbnail_path):
                self._upload_thumbnail(youtube, video_id, thumbnail_path)
                
            return video_id
        except Exception as e:
            logging.error(f"Error uploading video: {e}")
            return None

    def _upload_thumbnail(self, youtube, video_id, thumbnail_path):
        logging.info("Uploading thumbnail...")
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            logging.info("Thumbnail uploaded successfully.")
        except Exception as e:
            logging.error(f"Error uploading thumbnail: {e}")

if __name__ == "__main__":
    uploader = YouTubeUploader()
