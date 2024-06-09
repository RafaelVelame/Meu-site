import os
import yt_dlp
import logging

def download_twitter_video(url, save_dir):
    try:
        # Criar o diretório se não existir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            logging.info(f"Diretório criado: {save_dir}")

        # Configurações do yt-dlp
        ydl_opts = {
            'outtmpl': os.path.join(save_dir, '%(title)s.%(ext)s'),
            'cookiesfrombrowser': ('chrome',)
        }

        # Verificar se o URL é válido
        if not url.startswith("https://x.com/"):
            logging.error("URL inválido. Certifique-se de que o URL seja do Twitter.")
            return

        # Baixar o vídeo
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        logging.info(f"Vídeo baixado com sucesso e salvo em {save_dir}")

    except yt_dlp.utils.DownloadError as e:
        logging.error(f"Erro ao baixar o vídeo: {e}")
    except OSError as e:
        logging.error(f"Erro de sistema: {e}")
    except Exception as e:
        logging.error(f"Erro inesperado: {e}")

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Exemplo de uso
url = "https://x.com/MarioAl99622137/status/1792997514322248173"
save_dir = os.path.expanduser("~/Desktop/downloadteste")
download_twitter_video(url, save_dir)
