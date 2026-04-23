import os
import yt_dlp
import imageio_ffmpeg
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

# Folder sementara yang diizinkan oleh Render
DOWNLOAD_FOLDER = "/tmp"

# Mendapatkan lokasi FFmpeg secara otomatis
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def download_youtube_to_mpeg(url):
    # Kita tetapkan nama file statis agar tidak error karena spasi/karakter unik
    target_filename = 'video_download.mp4'
    final_path = os.path.join(DOWNLOAD_FOLDER, target_filename)
    
    # Hapus file lama jika ada agar tidak bentrok
    if os.path.exists(final_path):
        os.remove(final_path)

    ydl_opts = {
        'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best',
        'outtmpl': final_path,  # Simpan langsung ke /tmp/video_download.mp4
        'noplaylist': True,
        'merge_output_format': 'mp4',
        'ffmpeg_location': FFMPEG_PATH,
        'overwrites': True,
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
        ydl.download([url])
        return target_filename

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
                return f"Gagal mengunduh video. Error: {e}", 500

    return render_template("index.html", file_name=file_name)

@app.route("/download/<filename>")
def download_file(filename):
    # Menggunakan send_file karena lebih stabil untuk folder /tmp
    path_to_file = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(path_to_file):
        return send_file(path_to_file, as_attachment=True)
    else:
        return "File tidak ditemukan. Silakan coba klik download lagi.", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)