import os
import re
import yt_dlp
import requests

TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp_downloads")
os.makedirs(TEMP_DIR, exist_ok=True)

def format_duration(seconds: int) -> str:
    if not seconds:
        return "00:00"
    minutes = seconds // 60
    sec = seconds % 60
    return f"{minutes:02d}:{sec:02d}"

def clean_title(title: str) -> str:
    # Klip, Official, Premyera va boshqa ortiqcha so'zlarni tozalash
    title = re.sub(r'\[.*?\]|\(.*?\)', '', title)
    title = re.sub(r'(?i)(official video|video klip|premyera|official audio|klip|hd|4k)', '', title)
    return title.strip()

def search_music(query: str, limit: int = 6):
    """
    Qo'shiq nomini qidirish va topilgan ro'yxatni qaytarish
    """
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'noplaylist': True,
        'extract_flat': True,
        'default_search': f'ytsearch{limit}'
    }
    
    results = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch{limit}:{query}"
            info = ydl.extract_info(search_query, download=False)
            
            if 'entries' in info and info['entries']:
                for entry in info['entries']:
                    if not entry:
                        continue
                    v_id = entry.get('id')
                    title = entry.get('title', 'Noma\'lum qo\'shiq')
                    duration = entry.get('duration') or 0
                    channel = entry.get('channel') or entry.get('uploader') or ""
                    
                    results.append({
                        'id': v_id,
                        'title': title,
                        'clean_title': clean_title(title),
                        'performer': channel,
                        'duration': duration,
                        'duration_str': format_duration(duration),
                        'url': f"https://www.youtube.com/watch?v={v_id}"
                    })
    except Exception as e:
        print(f"Qidiruvda xatolik: {e}")
        
    return results

def download_audio_by_id(video_id: str):
    """
    YouTube video_id orqali audioni yuklab oladi va fayl yo'lini qaytaradi.
    """
    out_pattern = os.path.join(TEMP_DIR, f"{video_id}.%(ext)s")
    
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio',
        'outtmpl': out_pattern,
        'quiet': True,
        'noplaylist': True,
        'max_filesize': 49 * 1024 * 1024,  # Telegram bot uchun 50MB cheklov
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            url = f"https://www.youtube.com/watch?v={video_id}"
            info = ydl.extract_info(url, download=True)
            
            ext = info.get('ext', 'm4a')
            file_path = os.path.join(TEMP_DIR, f"{video_id}.{ext}")
            
            if not os.path.exists(file_path):
                # ba'zida boshqa kengaytma bilan saqlanishi mumkin
                for f in os.listdir(TEMP_DIR):
                    if f.startswith(video_id):
                        file_path = os.path.join(TEMP_DIR, f)
                        break

            title = info.get('title', 'Musiqa')
            performer = info.get('uploader') or info.get('artist') or "Music Bot"
            duration = info.get('duration') or 0
            
            # Thumbnail yuklab olish
            thumb_path = None
            thumbnail_url = info.get('thumbnail')
            if thumbnail_url:
                try:
                    thumb_resp = requests.get(thumbnail_url, timeout=5)
                    if thumb_resp.status_code == 200:
                        thumb_path = os.path.join(TEMP_DIR, f"{video_id}_thumb.jpg")
                        with open(thumb_path, 'wb') as tf:
                            tf.write(thumb_resp.content)
                except Exception:
                    thumb_path = None
            
            return {
                'success': True,
                'file_path': file_path,
                'title': title,
                'performer': performer,
                'duration': duration,
                'thumbnail_path': thumb_path
            }
    except Exception as e:
        print(f"Yuklab olishda xatolik: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def cleanup_files(*file_paths):
    """
    Yuborilgandan so'ng vaqtinchalik fayllarni o'chirish
    """
    for path in file_paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass
