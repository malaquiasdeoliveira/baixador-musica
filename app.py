import streamlit as st
import yt_dlp
import os
import shutil

st.set_page_config(page_title="Baixador de Músicas", page_icon="🎵")

st.title("🎵 YouTube para MP3")
st.write("Olá! Cole o link abaixo, escolha o tipo e clique no botão para baixar.")

# Interface de entrada
url = st.text_input("Cole o link do YouTube aqui:", placeholder="https://www.youtube.com/...")
tipo = st.radio("O que você está baixando?", ["Uma única música", "Uma Playlist / Mix"])

if tipo == "Uma Playlist / Mix":
    qtd_limite = st.number_input("Baixar quantas músicas? (0 para todas)", min_value=0, value=0)

def processar_download(link, is_playlist, limite=0):
    output_path = "baixados"
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'quiet': True,
    }

    if is_playlist:
        ydl_opts['yes_playlist'] = True
        if limite > 0:
            ydl_opts['playlistend'] = limite

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        
        # Se for playlist, compacta em ZIP como no seu original
        if is_playlist:
            shutil.make_archive("musicas_playlist", 'zip', output_path)
            return "musicas_playlist.zip"
        else:
            # Se for música única, retorna o caminho do arquivo gerado
            arquivo = os.listdir(output_path)[0]
            return os.path.join(output_path, arquivo)
    except Exception as e:
        st.error(f"Erro: {e}")
        return None

if st.button("Preparar Download"):
    if url:
        with st.spinner("Processando... Isso pode demorar um pouco dependendo do tamanho."):
            resultado = processar_download(url, tipo == "Uma Playlist / Mix", qtd_limite if tipo == "Uma Playlist / Mix" else 0)
            
            if resultado:
                with open(resultado, "rb") as f:
                    st.success("Concluído! Clique abaixo para salvar no seu PC.")
                    st.download_button(
                        label="⬇️ Salvar Arquivo",
                        data=f,
                        file_name=os.path.basename(resultado),
                        mime="application/octet-stream"
                    )
    else:
        st.warning("Por favor, cole um link primeiro!")