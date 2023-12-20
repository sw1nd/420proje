from PIL import Image
import wave
from cryptography.fernet import Fernet
import struct

def hide_text(image_path, secret_text, output_path):
	# Open the image
	image = Image.open(image_path)

	# Convert the secret text to binary
	binary_secret_text = ''.join(format(ord(char), '08b') for char in secret_text)

	# Check if the image can accommodate the secret text
	image_capacity = image.width * image.height * 3
	if len(binary_secret_text) > image_capacity:
		raise ValueError("Image does not have sufficient capacity to hide the secret text.")

	# Hide the secret text in the image
	pixels = image.load()
	index = 0
	for i in range(image.width):
		for j in range(image.height):
			r, g, b = pixels[i, j]

			# Modify the least significant bit of each color channel
			if index < len(binary_secret_text):
				r = (r & 0xFE) | int(binary_secret_text[index])
				index += 1
			if index < len(binary_secret_text):
				g = (g & 0xFE) | int(binary_secret_text[index])
				index += 1
			if index < len(binary_secret_text):
				b = (b & 0xFE) | int(binary_secret_text[index])
				index += 1

			pixels[i, j] = (r, g, b)

	# Save the image with the hidden secret text
	image.save(output_path)

def extract_text(image_path):
	# Open the image
	image = Image.open(image_path)

	# Extract the secret text from the image
	pixels = image.load()
	binary_secret_text = ""
	for i in range(image.width):
		for j in range(image.height):
			r, g, b = pixels[i, j]

			# Extract the least significant bit of each color channel
			binary_secret_text += str(r & 1)
			binary_secret_text += str(g & 1)
			binary_secret_text += str(b & 1)

	# Convert the binary text to ASCII
	secret_text = ""
	for i in range(0, len(binary_secret_text), 8):
		char = chr(int(binary_secret_text[i:i+8], 2))
		secret_text += char

	return secret_text

'''def hide_text_in_audio(audio_path, secret_text, output_path):
    # WAV dosyasını aç
    song = wave.open(audio_path, mode='rb')
    
    # Gizli metni ikili formata çevir
    binary_secret_text = ''.join(format(ord(i), '08b') for i in secret_text)
    # Ses çerçevelerini oku
    frames = bytearray(list(song.readframes(song.getnframes())))
    
    # Gizli metni ses çerçevelerine gizle
    index = 0
    for i, frame in enumerate(frames):
        if index < len(binary_secret_text):
            frames[i] = (frame & 254) | int(binary_secret_text[index], 2)
            index += 1

    # Yeni ses dosyasını yaz
    with wave.open(output_path, 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(frames)

    song.close()

def extract_text_from_audio(audio_path):
    # WAV dosyasını aç
    song = wave.open(audio_path, mode='rb')
    
    # Ses çerçevelerini oku
    frames = bytearray(list(song.readframes(song.getnframes())))
    song.close()
    
    # Gizli metni çıkar
    extracted_bits = [frames[i] & 1 for i in range(len(frames))]
    
    # İkili veriyi metne çevir
    secret_text = "".join(chr(int("".join(map(str, extracted_bits[i:i+8])), 2)) for i in range(0, len(extracted_bits), 8))
    
    return secret_text.strip('\x00')'''



# Metni şifrelemek için fonksiyon
def encrypt_message(message, key):
    fernet = Fernet(key)
    encrypted_message = fernet.encrypt(message.encode())
    return encrypted_message

# Metni çözmek için fonksiyon
def decrypt_message(encrypted_message, key):
    fernet = Fernet(key)
    decrypted_message = fernet.decrypt(encrypted_message)
    return decrypted_message.decode()

# Gizli metni WAV dosyasına gizlemek için fonksiyon
def hide_text_in_audio(audio_path, secret_text, output_path, encryption_key):
    # Gizli metni şifrele
    encrypted_message = encrypt_message(secret_text, encryption_key)
    # WAV dosyasını aç
    with wave.open(audio_path, mode='rb') as song:
        # Gizli metni ikili forma çevir
        binary_secret_text = ''.join(format(byte, '08b') for byte in encrypted_message)
        # Ses çerçevelerini oku
        frames = bytearray(list(song.readframes(song.getnframes())))
        # Gizli metni ses çerçevelerine gizle
        index = 0
        for i in range(len(frames)):
            frame = frames[i]
            if index < len(binary_secret_text):
                frames[i] = frame & 0xFE | int(binary_secret_text[index], 2)
                index += 1
        # Yeni ses dosyasını yaz
        with wave.open(output_path, 'wb') as fd:
            fd.setparams(song.getparams())
            fd.writeframes(frames)

# Gizli metni WAV dosyasından çıkarmak için fonksiyon
def extract_text_from_audio(audio_path, decryption_key):
    # WAV dosyasını aç
    with wave.open(audio_path, mode='rb') as song:
        # Ses çerçevelerini oku
        frames = bytearray(list(song.readframes(song.getnframes())))
        # Gizli metni çıkar
        extracted_bits = [str(frame & 1) for frame in frames]
        # İkili veriyi byte dizisine çevir
        secret_bytes = bytes(int(''.join(extracted_bits[i:i+8]), 2) for i in range(0, len(extracted_bits), 8))
        # Metni çöz
        secret_text = decrypt_message(secret_bytes, decryption_key)
        return secret_text
