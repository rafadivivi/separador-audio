from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import shutil
import os
import zipfile
from spleeter.separator import Separator

app = FastAPI()

# Inicializa o Spleeter no modo de 4 faixas (vocals, drums, bass, other)
separator = Separator('spleeter:4stems')

@app.get("/")
def read_root():
    return {"status": "Online", "message": "API de Sep Separação de Áudio Ativa!"}

@app.post("/separate")
async def separate_audio(file: UploadFile = File(...)):
    # 1. Salva o MP3 enviado temporariamente no servidor
    input_path = "temp_input.mp3"
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")
    
    # 2. Configura as pastas de saída
    output_dir = "output"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    # 3. Executa a IA do Spleeter para separar as faixas
    try:
        separator.separate_to_file(input_path, output_dir)
    except Exception as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        raise HTTPException(status_code=500, detail=f"Erro no Spleeter: {str(e)}")
    
    # O Spleeter cria uma subpasta com as faixas separadas (output/temp_input/)
    song_folder = os.path.join(output_dir, "temp_input")
    zip_path = "separated_tracks.zip"
    
    if os.path.exists(zip_path):
        os.remove(zip_path)
        
    # 4. Compacta as faixas (.wav) geradas em um único arquivo .zip
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(song_folder):
            for f in files:
                # Salva os arquivos direto na raiz do ZIP para facilitar a extração no Android
                zipf.write(os.path.join(root, f), f)
                
    # Limpa os arquivos temporários para não lotar o servidor gratuito
    if os.path.exists(input_path):
        os.remove(input_path)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        
    # 5. Envia o arquivo ZIP de volta para o seu aplicativo
    return FileResponse(zip_path, media_type="application/zip", filename="faixas_separadas.zip")
