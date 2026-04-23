from flask import Flask, render_template, request, send_from_directory
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


def download_youtube_to_mpeg(url):
    ydl_opts = {
        'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
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
        final_filename = os.path.splitext(filename)[0] + ".mp4"
        return os.path.basename(final_filename)


@app.route("/", methods=["GET", "POST"])
def index():
    file_name = None

    if request.method == "POST":
        url = request.form.get("url")
        if url:
            file_name = download_youtube_to_mpeg(url)

    return render_template("index.html", file_name=file_name)


@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)


# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
    # Gunakan port dari environment variable Render, default ke 5000 jika lokal
    port = int(os.environ.get("PORT", 5000))
    # Host harus 0.0.0.0 agar bisa diakses di internet
    app.run(host="0.0.0.0", port=port)