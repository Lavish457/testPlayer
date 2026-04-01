import yt_dlp
import webbrowser
import json
from urllib.parse import urlparse
 
def get_full_video(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    print("🔄 Extracting video details and streams...\n")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            print("="*90)
            print("🎵 VIDEO DETAILS".center(90))
            print("="*90)
            print(f"Title      : {info.get('title', 'N/A')}")
            print(f"Channel    : {info.get('uploader', 'N/A')}")
            print(f"Views      : {info.get('view_count', 0):,}")
            print(f"Duration   : {info.get('duration', 0)} seconds")
            print(f"Uploaded   : {info.get('upload_date', 'N/A')}")
            print("="*90)
            
            # ==================== FULL DESCRIPTION ====================
            print("\n📝 FULL DESCRIPTION")
            print("-" * 90)
            description = info.get('description', 'No description available.')
            print(description)
            print("-" * 90)
            
            # ==================== DIRECT PLAYABLE STREAMS ====================
            print("\n▶️  DIRECT PLAYABLE STREAMS")
            print("-" * 90)
            print("Opening the best quality link in your browser...\n")
            
            formats = info.get('formats', [])
            
            # Get combined video+audio formats (easiest for browser)
            video_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('acodec') != 'none']
            
            # Sort by resolution (highest first)
            video_formats.sort(key=lambda f: (f.get('height') or 0, f.get('tbr') or 0), reverse=True)
            
            best_url = None
            if video_formats:
                best_url = video_formats[0]['url']
                print(f"🎥 Best Quality: {video_formats[0].get('height')}p")
                print(f"🔗 Opening in browser: {best_url[:100]}...\n")
                
                # Open the best direct link in default browser
                webbrowser.open(best_url)
                
                # Show a few more options
                print("Other available qualities:")
                for f in video_formats[1:6]:   # Show next 5 qualities
                    if f.get('url'):
                        quality = f"{f.get('height')}p" if f.get('height') else "Unknown"
                        print(f"   • {quality}  →  {f['url'][:80]}...")
            else:
                print("No direct stream found. Opening original YouTube page instead.")
                webbrowser.open(url)
            
            save_data = {
                "title": info.get('title'),
                "channel": info.get('uploader'),
                "views": info.get('view_count'),
                "duration": info.get('duration'),
                "best_direct_url": best_url,
                "youtube_url": url
            }
            
            with open(f"video_{video_id}.txt", "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=4, ensure_ascii=False)
            
            print(f"\n✅ Details saved to: video_{video_id}.txt")
            print("💡 If the video doesn't play well in browser, copy any link and open in VLC Media Player.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Tip: Try running the script again.")
 

video_id = "iOgR7hi90Ac"  
 
get_full_video(video_id)