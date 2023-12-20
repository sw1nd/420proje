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
    md5_hash = hashlib.md5()
    md5_hash.update(data.encode())
    return md5_hash.hexdigest()

def validate_extracted_files(extracted_files):
    for file_name, content in extracted_files.items():
        extracted_hash, extracted_content = content.split(DELIMITER, 1)
        calculated_hash = create_md5_hash(extracted_content)
        if extracted_hash != calculated_hash:
            print(f"Warning: The file '{file_name}' may have been tampered with or corrupted.")
        else:
            with open(f"extracted_{file_name}", 'w') as file:
                file.write(extracted_content)

def derive_aes_key_from_password(password):
    # Parolayı SHA-256 kullanarak hash'le ve 32 baytlık bir anahtar elde et
    return hashlib.sha256(password).digest()

# AES encryption
def encrypt_aes(data, password):
    key = derive_aes_key_from_password(password)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data.encode()) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return encrypted_data

# AES decryption
def decrypt_aes(encrypted_data, password):
    key = derive_aes_key_from_password(password)
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    try:
        padded_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
        return padded_data.decode('utf-8')
    except ValueError as e:
        raise ValueError(f"Padding error: {e}")

def create_data_structure_with_hash(file_paths, key):
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
    """
    Calculate the size of the file structure (file name, hash, content, delimiters) in bits.
    """
    file_name = os.path.basename(file_path)
    with open(file_path, 'r') as file:
        content = file.read()

    # Create an MD5 hash of the content
    md5_hash = hashlib.md5(content.encode()).hexdigest()

    # Construct the file structure with delimiters
    file_structure = f"{file_name}{DELIMITER}{md5_hash}{DELIMITER}{content}{DELIMITER}"

    # Convert the file structure to binary and calculate its size in bits
    binary_file_structure = ''.join(format(ord(char), '08b') for char in file_structure)
    size_in_bits = len(binary_file_structure)

    return size_in_bits

def extract_and_validate_files(binary_data, key):
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
            print(f"Warning: The file '{file_name}' may have been tampered with or corrupted.")
            return None
    
    return extracted_files

def hide_data_in_audio(audio_path, binary_data):
    with wave.open(audio_path, 'rb') as audio_file:
        frame_bytes = bytearray(list(audio_file.readframes(audio_file.getnframes())))

        # binary_data'yı ikili forma çevir
        binary_bits = ''.join([format(byte, '08b') for byte in binary_data])
        # Embed the binary bits into the audio
        for i in range(len(binary_bits)):
            frame_bytes[i] = (frame_bytes[i] & 254) | int(binary_bits[i])
            
    return audio_file.getparams(), frame_bytes


def extract_data_from_audio(audio_path, key):
    with wave.open(audio_path, 'rb') as audio_file:
        frame_bytes = bytearray(list(audio_file.readframes(audio_file.getnframes())))

        # Extract the LSB of each byte
        extracted_bits = [str(byte & 1) for byte in frame_bytes]
        encrypted_data = bytes(int("".join(extracted_bits[i:i+8]), 2) for i in range(0, len(extracted_bits), 8))
    
        # Decrypt and return the data
        return extract_and_validate_files(encrypted_data, key)

def hide_data_in_image(image_path, binary_data):
    image = Image.open(image_path)
    pixels = list(image.getdata())

    # Bayt dizisini bitlere dönüştür
    binary_bits = ''.join([format(byte, '08b') for byte in binary_data])

    binary_data_index = 0
    new_pixels = []
    for pixel in pixels:
        if image.mode == 'RGB':
            new_pixel = list(pixel)  # RGB modunda piksel zaten bir tuple'dır
        else:
            new_pixel = [pixel]  # Diğer modlarda pikseli bir liste içine al
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
        for channel in pixel[:3]:  # Only the first three channels (RGB)
            extracted_bits.append(str(channel & 1))

    encrypted_data = bytes(int("".join(extracted_bits[i:i+8]), 2) for i in range(0, len(extracted_bits), 8))

    return extract_and_validate_files(encrypted_data, key)

def get_file_type_and_extension(file_path):
    # Dosya uzantısını al
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    # MIME türünü al ve dosya türünü belirle
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
