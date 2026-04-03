import os
import yt_dlp
import json
from http.server import BaseHTTPRequestHandler
import socketserver
from urllib.parse import urlparse, parse_qs

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 8000))

# 👇 Set your Render service URL here (or via environment variable)
BASE_URL = os.environ.get("BASE_URL", "https://your-app-name.onrender.com")

class VideoHandler(BaseHTTPRequestHandler):
    timeout = 90

    def do_GET(self):
        try:
            parsed = urlparse(self.path)

            if parsed.path == "/play":
                video_id = parse_qs(parsed.query).get("video_id", [None])[0]
                if not video_id:
                    self.send_error(400, "Missing video_id")
                    return
                self.process_video(video_id)

            else:
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()

                message = f"""
Server is running ✅

Use endpoint:
{BASE_URL}/play?video_id=VIDEO_ID

Example:
{BASE_URL}/play?video_id=dQw4w9WgXcQ
"""
                self.wfile.write(message.encode("utf-8"))

        except Exception as e:
            print(f"Request error: {e}")
            self.send_error(500, str(e))

    def process_video(self, video_id):
        url = f"https://www.youtube.com/watch?v={video_id}"

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'web', 'android_embedded']
                }
            },
            'format': 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best',
            'socket_timeout': 6,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])

                combined = [
                    f for f in formats
                    if f.get('vcodec') != 'none'
                    and f.get('acodec') != 'none'
                    and f.get('ext') == 'mp4'
                ]

                if combined:
                    combined.sort(
                        key=lambda f: (f.get('height') or 0, f.get('tbr') or 0),
                        reverse=True
                    )
                    best = combined[0]
                    direct_url = best['url']
                    quality = f"{best.get('height')}p"
                else:
                    best_list = ydl._format_selector(info)
                    best = best_list[0] if best_list else None
                    direct_url = best['url'] if best else None
                    quality = "fallback"

                response_data = {
                    "success": True,
                    "video_id": video_id,
                    "title": info.get('title'),
                    "direct_url": direct_url,
                    "quality": quality,
                    "thumbnail": info.get('thumbnail')
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()

                self.wfile.write(
                    json.dumps(response_data, indent=2, ensure_ascii=False).encode('utf-8')
                )

                print(f"✅ Served {video_id} | {quality}")

        except Exception as e:
            print(f"❌ Failed {video_id}: {e}")
            error_data = {
                "success": False,
                "video_id": video_id,
                "error": str(e)[:300]
            }

            try:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()

                self.wfile.write(json.dumps(error_data).encode('utf-8'))
            except:
                pass


def run():
    with socketserver.ThreadingTCPServer((HOST, PORT), VideoHandler) as server:
        print(f"🚀 Server running on port {PORT}")
        server.serve_forever()


if __name__ == "__main__":
    run()
