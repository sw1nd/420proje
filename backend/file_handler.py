import os

def handle_file(file_path):
    # Dosya uzantısını al ve tipine göre işlem yap
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
        return 'image', file_path
    elif ext in ['.wav', '.mp3', '.ogg', '.flac']:
        return 'audio', file_path
    else:
        return 'unknown', None
