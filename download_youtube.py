from flask import Flask, render_template, request, send_from_directory
import yt_dlp
import os
import imageio_ffmpeg # Library tambahan agar FFmpeg terbaca otomatis

app = Flask(__name__)

# Tentukan folder download yang aman untuk Render
DOWNLOAD_FOLDER = "/tmp"

# Ambil path FFmpeg secara otomatis dari library imageio-ffmpeg
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def download_youtube_to_mpeg(url):
    ydl_opts = {
        'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'concurrent_fragment_downloads': 5,
        'merge_output_format': 'mp4',
        # PERBAIKAN: Beritahu yt-dlp di mana lokasi FFmpeg berada
        'ffmpeg_location': FFMPEG_PATH, 
        'postprocessors': [
            {
                'key': 'FFmpegVideoRemuxer',
                'preferedformat': 'mp4',
            },
            {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }
        ],
        'postprocessor_args': [
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-crf', '28',
            '-c:a', 'aac'
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        # Pastikan kita mengembalikan nama file yang benar-benar ada (ekstensi .mp4)
        base_name = os.path.splitext(os.path.basename(filename))[0]
        return f"{base_name}.mp4"

@app.route("/", methods=["GET", "POST"])
def index():
    file_name = None
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            try:
                file_name = download_youtube_to_mpeg(url)
            except Exception as e:
                print(f"Error detail: {e}")
                return f"Gagal mengunduh video. Pastikan link benar. Error: {e}", 500

    return render_template("index.html", file_name=file_name)

@app.route("/download/<filename>")
def download_file(filename):
    # Mengambil file dari /tmp
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    # Binding Host dan Port untuk Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)