from flask import Flask, request, jsonify
import yt_dlp
import os
import json

app = Flask(__name__)

def get_full_video(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            formats = info.get('formats', [])
            # Get combined video+audio streams
            video_formats = [
                f for f in formats
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none'
            ]

            video_formats.sort(
                key=lambda f: (f.get('height') or 0, f.get('tbr') or 0),
                reverse=True
            )

            best_url = video_formats[0]['url'] if video_formats else None

            video_data = {
                "title": info.get('title'),
                "channel": info.get('uploader'),
                "views": info.get('view_count'),
                "duration": info.get('duration'),
                "best_direct_url": best_url,
                "youtube_url": url
            }

            # Optional: save to file
            with open(f"video_{video_id}.json", "w", encoding="utf-8") as f:
                json.dump(video_data, f, indent=4, ensure_ascii=False)

            return video_data

    except Exception as e:
        return {"error": str(e)}

@app.route("/video", methods=["GET"])
def video():
    video_id = request.args.get("videoId")
    if not video_id:
        return jsonify({"error": "Missing videoId"}), 400

    data = get_full_video(video_id)
    return jsonify(data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
