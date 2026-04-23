from flask import Flask, render_template, request, send_from_directory, send_file
import yt_dlp
import os

app = Flask(__name__)

# PERBAIKAN 1: Gunakan folder /tmp karena Render membatasi izin tulis di folder root
DOWNLOAD_FOLDER = "/tmp"

# Pastikan folder ada (walaupun /tmp biasanya selalu ada di Linux)
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def download_youtube_to_mpeg(url):
    ydl_opts = {
        'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best',
        # PERBAIKAN 2: Path output diarahkan ke /tmp
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'concurrent_fragment_downloads': 5,
        'merge_output_format': 'mp4',
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
        # yt-dlp mungkin mengubah ekstensi saat merge, pastikan kita ambil nama akhirnya
        final_filename = os.path.splitext(filename)[0] + ".mp4"
        return os.path.basename(final_filename)


@app.route("/", methods=["GET", "POST"])
def index():
    file_name = None
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            try:
                file_name = download_youtube_to_mpeg(url)
            except Exception as e:
                print(f"Error: {e}")
                return f"Terjadi kesalahan: {e}", 500

    return render_template("index.html", file_name=file_name)


@app.route("/download/<filename>")
def download_file(filename):
    # PERBAIKAN 3: Mengambil file dari /tmp
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    # PERBAIKAN 4: Binding Host dan Port untuk Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)