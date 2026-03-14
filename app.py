import streamlit as st
import yt_dlp
import os
import shutil
import tempfile

st.set_page_config(page_title="Baixador de Músicas", page_icon="🎵")

st.title("🎵 YouTube para MP3")
st.write("Olá! Cole o link abaixo para baixar sua música.")

url = st.text_input("Cole o link do YouTube aqui:", placeholder="https://www.youtube.com/...")
tipo = st.radio("O que você está baixando?", ["Uma única música", "Uma Playlist / Mix"])

if tipo == "Uma Playlist / Mix":
    qtd_limite = st.number_input("Baixar quantas músicas? (0 para todas)", min_value=0, value=0)

def processar_download(link, is_playlist, limite=0):
    # Criar uma pasta temporária segura
    tmpdir = tempfile.mkdtemp()
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'quiet': False, # Mudei para False para você ver o erro no log se falhar
        'no_warnings': False,
        # Força o uso de IPv4, que costuma dar menos erro 403 em Cloud
        'source_address': '0.0.0.0',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{tmpdir}/%(title)s.%(ext)s',
    }

    if is_playlist:
        ydl_opts['yes_playlist'] = True
        if limite > 0:
            ydl_opts['playlistend'] = limite

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        
        if is_playlist:
            zip_path = os.path.join(tempfile.gettempdir(), "playlist_musicas")
            shutil.make_archive(zip_path, 'zip', tmpdir)
            return f"{zip_path}.zip"
        else:
            arquivos = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir) if f.endswith('.mp3')]
            return arquivos[0] if arquivos else None
    except Exception as e:
        st.error(f"Erro detalhado: {e}")
        return None

if st.button("Preparar Download"):
    if url:
        with st.spinner("Baixando... Se for playlist, pode demorar."):
            resultado = processar_download(url, tipo == "Uma Playlist / Mix", qtd_limite if tipo == "Uma Playlist / Mix" else 0)
            
            if resultado and os.path.exists(resultado):
                with open(resultado, "rb") as f:
                    st.success("Pronto!")
                    st.download_button(
                        label="⬇️ Salvar no meu computador",
                        data=f,
                        file_name=os.path.basename(resultado),
                        mime="audio/mpeg" if not resultado.endswith('.zip') else "application/zip"
                    )
            else:
                st.error("O YouTube bloqueou a tentativa. Tente novamente em alguns minutos ou verifique se o link está correto.")
    else:
        st.warning("Coloque um link!")