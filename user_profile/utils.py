import os
from PIL import Image
from werkzeug.utils import secure_filename
import uuid

UPLOAD_FOLDER = "static/profile_pics"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_profile_picture(file, user_id, size=(300, 300)):
    if not allowed_file(file.filename):
        return None
    
    # Gera um nome único
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    # Subpasta baseada no ID do usuário (para distribuir arquivos)
    subfolder = str(user_id % 100)  # cria 100 subpastas (0-99)
    folder_path = os.path.join(UPLOAD_FOLDER, subfolder)
    os.makedirs(folder_path, exist_ok=True)

    # Caminho final
    file_path = os.path.join(folder_path, filename)

    #Salva a imagem temporariamente e redimensiona
    img = Image.open(file)
    img.thumbnail(size)
    img.save(file_path)

    # Retorna o caminho relativo que será salvo no banco
    relative_path = f"{subfolder}/{filename}"
    return relative_path
