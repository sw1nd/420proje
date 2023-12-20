from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import wave
import numpy as np
import os
import hashlib
from PIL import Image
import mimetypes

DELIMITER = '<<endoffile>>'

def create_md5_hash(data):
    # Verilen veriyi MD5 hash'ine dönüştürür
    md5_hash = hashlib.md5()
    md5_hash.update(data.encode())
    return md5_hash.hexdigest()

def validate_extracted_files(extracted_files):
    # Çıkarılan dosyaları doğrular; hash'lerini kontrol eder
    for file_name, content in extracted_files.items():
        extracted_hash, extracted_content = content.split(DELIMITER, 1)
        calculated_hash = create_md5_hash(extracted_content)
        if extracted_hash != calculated_hash:
            print(f"Uyarı: '{file_name}' dosyası bozulmuş veya değiştirilmiş olabilir.")
        else:
            with open(f"extracted_{file_name}", 'w') as file:
                file.write(extracted_content)

def derive_aes_key_from_password(password):
    # Paroladan AES anahtarı türetir
    return hashlib.sha256(password).digest()

def encrypt_aes(data, password):
    # Veriyi AES ile şifreler
    key = derive_aes_key_from_password(password)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return encrypted_data

def decrypt_aes(encrypted_data, password):
    # Şifrelenmiş veriyi AES ile çözer
    key = derive_aes_key_from_password(password)
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    try:
        padded_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
        return padded_data.decode('utf-8')
    except ValueError as e:
        raise ValueError(f"Dolgu hatası: {e}")

def create_data_structure_with_hash(file_paths, key):
    # Dosya yollarından şifreli veri yapısı oluşturur
    binary_data = b''
    for path in file_paths:
        file_name = os.path.basename(path)
        with open(path, 'r') as file:
            content = file.read()
        hash_value = create_md5_hash(content)
        file_structure = f"{file_name}{DELIMITER}{hash_value}{DELIMITER}{content}{DELIMITER}"
        encrypted_file_structure = encrypt_aes(file_structure, key)
        binary_data += encrypted_file_structure
    return binary_data

def calculate_file_structure_size(file_path):
    # Dosya yapısının boyutunu bit cinsinden hesaplar
    file_name = os.path.basename(file_path)
    with open(file_path, 'r') as file:
        content = file.read()
    md5_hash = hashlib.md5(content.encode()).hexdigest()
    file_structure = f"{file_name}{DELIMITER}{md5_hash}{DELIMITER}{content}{DELIMITER}"
    binary_file_structure = ''.join(format(ord(char), '08b') for char in file_structure)
    size_in_bits = len(binary_file_structure)
    return size_in_bits

def extract_and_validate_files(binary_data, key):
    # Şifreli veriyi çözüp dosyaları doğrular
    decrypted_data = decrypt_aes(binary_data, key)
    files_data = decrypted_data.split(DELIMITER)
    extracted_files = {}
    for i in range(0, len(files_data) - 1, 3):
        file_name = files_data[i]
        hash_value = files_data[i + 1]
        file_content = files_data[i + 2]
        calculated_hash = create_md5_hash(file_content)
        if hash_value == calculated_hash:
            extracted_files[file_name] = file_content
        else:
            print(f"Uyarı: '{file_name}' dosyası bozulmuş veya değiştirilmiş olabilir.")
            return None
    return extracted_files

# ... (Audio ve Image için saklama ve çıkarma fonksiyonları)

def hide_data_in_audio(audio_path, binary_data):
    with wave.open(audio_path, 'rb') as audio_file:
        frame_bytes = bytearray(list(audio_file.readframes(audio_file.getnframes())))

        # binary_data'yı ikili forma çevir
        binary_bits = ''.join([format(byte, '08b') for byte in binary_data])
        # binary bitleri audioya ekle
        for i in range(len(binary_bits)):
            frame_bytes[i] = (frame_bytes[i] & 254) | int(binary_bits[i])
            
    return audio_file.getparams(), frame_bytes


def extract_data_from_audio(audio_path, key):
    with wave.open(audio_path, 'rb') as audio_file:
        frame_bytes = bytearray(list(audio_file.readframes(audio_file.getnframes())))

        #Her bytein LSB sini al
        extracted_bits = [str(byte & 1) for byte in frame_bytes]
        encrypted_data = bytes(int("".join(extracted_bits[i:i+8]), 2) for i in range(0, len(extracted_bits), 8))
    
        # Decrypt
        return extract_and_validate_files(encrypted_data, key)

def hide_data_in_image(image_path, binary_data):
    image = Image.open(image_path)
    pixels = list(image.getdata())

    # Bayt dizisini bitlere dönüştür
    binary_bits = ''.join([format(byte, '08b') for byte in binary_data])

    binary_data_index = 0
    new_pixels = []
    for pixel in pixels:
        new_pixel = list(pixel)
        for i in range(3):
            if binary_data_index < len(binary_bits):
                # Bitleri piksellerin en az anlamlı bitlerine yerleştir
                new_pixel[i] = new_pixel[i] & ~1 | int(binary_bits[binary_data_index], 2)
                binary_data_index += 1
        new_pixels.append(tuple(new_pixel))

    new_image = Image.new(image.mode, image.size)
    new_image.putdata(new_pixels)
    return new_image

    

def extract_data_from_image(image_path, key):
    image = Image.open(image_path)
    pixels = list(image.getdata())

    extracted_bits = []
    for pixel in pixels:
        for channel in pixel[:3]:  
            extracted_bits.append(str(channel & 1))

    encrypted_data = bytes(int("".join(extracted_bits[i:i+8]), 2) for i in range(0, len(extracted_bits), 8))

    return extract_and_validate_files(encrypted_data, key)

def get_file_type_and_extension(file_path):
    # Dosya uzantısını ve tipini alır
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        if mime_type.startswith('image/'):
            file_type = 'image'
        elif mime_type.startswith('audio/'):
            file_type = 'audio'
        else:
            file_type = 'unknown'
    else:
        file_type = 'unknown'
    return file_type, file_extension
