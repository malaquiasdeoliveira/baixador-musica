import streamlit as st
import yt_dlp
import os
import shutil

# Configuração visual da página
st.set_page_config(page_title="Baixador de Músicas", page_icon="🎵")

st.title("🎵 YouTube para MP3")
st.write("Olá! Cole o link abaixo, escolha se é uma música ou playlist e clique em preparar.")

# Interface de entrada para o usuário
url = st.text_input("Cole o link do YouTube aqui:", placeholder="https://www.youtube.com/...")
tipo = st.radio("O que você está baixando?", ["Uma única música", "Uma Playlist / Mix"])

if tipo == "Uma Playlist / Mix":
    qtd_limite = st.number_input("Baixar quantas músicas? (0 para todas)", min_value=0, value=0)

def processar_download(link, is_playlist, limite=0):
    output_path = "baixados"
    
    # Limpa a pasta de downloads anterior para não misturar arquivos
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path)

    # Configurações para burlar o erro 403 e definir qualidade
    ydl_opts = {
        'format': 'bestaudio/best',
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
    }

    # Lógica específica para Playlists (baseada no seu código original)
    if is_playlist:
        ydl_opts['yes_playlist'] = True
        if limite > 0:
            ydl_opts['playlistend'] = limite

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        
        # Se for playlist, compacta tudo em um arquivo ZIP
        if is_playlist:
            nome_zip = "playlist_musicas"
            shutil.make_archive(nome_zip, 'zip', output_path)
            return f"{nome_zip}.zip"
        else:
            # Se for música única, pega o primeiro (e único) arquivo da pasta
            arquivos = os.listdir(output_path)
            if arquivos:
                return os.path.join(output_path, arquivos[0])
            return None
            
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")
        return None

# Botão de ação principal
if st.button("Preparar Download"):
    if url:
        with st.spinner("O site está processando o áudio... Isso pode levar alguns minutos."):
            resultado = processar_download(url, tipo == "Uma Playlist / Mix", qtd_limite if tipo == "Uma Playlist / Mix" else 0)
            
            if resultado and os.path.exists(resultado):
                with open(resultado, "rb") as f:
                    st.success("Tudo pronto! Agora é só salvar.")
                    st.download_button(
                        label="⬇️ Clique aqui para salvar no seu dispositivo",
                        data=f,
                        file_name=os.path.basename(resultado),
                        mime="application/octet-stream"
                    )
            else:
                st.error("Não foi possível gerar o arquivo. Verifique o link ou tente novamente.")
    else:
        st.warning("Ei! Você esqueceu de colar o link do YouTube.")

# Rodapé simples
st.markdown("---")
st.caption("Downloads particulares.")