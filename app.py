from flask import Flask, request, render_template, send_file, jsonify
import os
import yt_dlp
import logging
import re
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
import threading
from urllib.parse import quote as url_quote


app = Flask(__name__)

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Variáveis globais para armazenar o progresso e controle de download
download_progress = {"progress": "0%"}
cancel_event = threading.Event()
download_thread = None
video_path = None

def sanitize_filename(filename):
    """Sanitize the filename to ensure it is secure and valid."""
    return secure_filename(re.sub(r'[\\/*?:"<>|]', "", filename))

def is_valid_url(url):
    """Check if the provided URL is valid."""
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])

def progress_hook(d):
    """Hook function to update the progress of the download."""
    if cancel_event.is_set():
        raise yt_dlp.utils.DownloadError("Download cancelado pelo usuário")
    if d['status'] == 'downloading':
        percent_str = d.get('_percent_str', '0.0%').strip()
        download_progress["progress"] = percent_str
    elif d['status'] == 'finished':
        download_progress["progress"] = "100%"

def download_video(url):
    """Function to download video from the provided URL."""
    global download_progress, video_path
    download_progress = {"progress": "0%"}  # Reset progress

    try:
        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(result)
            sanitized_path = sanitize_filename(os.path.basename(video_path))
            os.rename(video_path, sanitized_path)
            video_path = sanitized_path

        logging.info(f"Vídeo baixado com sucesso e salvo em {video_path}")
        return video_path

    except yt_dlp.utils.DownloadError as e:
        logging.error(f"Erro ao baixar o vídeo: {e}")
        return f"Erro ao baixar o vídeo: {e}"
    except OSError as e:
        logging.error(f"Erro de sistema: {e}")
        return f"Erro de sistema: {e}"
    except Exception as e:
        logging.error(f"Erro inesperado: {e}")
        return f"Erro inesperado: {e}"

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route to handle video download requests."""
    global cancel_event, download_thread, video_path
    message = None
    if request.method == 'POST':
        url = request.form['url']
        if not is_valid_url(url):
            message = "URL inválida. Por favor, insira uma URL válida."
        else:
            if download_thread is not None and download_thread.is_alive():
                message = "Já há um download em andamento. Por favor, aguarde."
            else:
                cancel_event.clear()  # Reset the cancel event
                download_thread = threading.Thread(target=lambda: download_video(url))
                download_thread.start()
                download_thread.join()  # Wait for the download to finish
                if os.path.exists(video_path):
                    return send_file(video_path, as_attachment=True)
                else:
                    message = f"Erro ao baixar o vídeo. {video_path}"
    return render_template('index.html', message=message)

@app.route('/progress')
def progress():
    """Route to get the current progress of the download."""
    return jsonify(download_progress)

@app.route('/cancel', methods=['POST'])
def cancel():
    """Route to cancel the current download."""
    global cancel_event
    cancel_event.set()
    return jsonify({"status": "cancelado"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
