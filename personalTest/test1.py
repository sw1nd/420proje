from backend.stegano_backend import *
def correct_and_convert_bits_to_bytes(extracted_bits):
    """
    Correct the extracted bits if necessary and convert them to bytes.

    :param extracted_bits: A list of extracted bits
    :return: The corresponding bytes
    """
    # Eksik bitleri tamamla (eğer varsa)
    while len(extracted_bits) % 8 != 0:
        extracted_bits.append('0')

    # Bitleri baytlara dönüştür
    extracted_binary_data = bytes(int(''.join(extracted_bits[i:i+8]), 2) for i in range(0, len(extracted_bits), 8))
    return extracted_binary_data

def verify_hidden_data_in_image(image_path, original_binary_data):
    # Resmi aç ve piksellerini al
    image = Image.open(image_path)
    pixels = list(image.getdata())

    # Çıkarılan bitleri saklamak için bir dizi
    extracted_bits = []

    # Piksellerdeki en az anlamlı bitleri çıkar
    for pixel in pixels:
        for channel in pixel[:3]:  # RGB kanallarını kullan
            extracted_bits.append(str(channel & 1))
    
    # Bit dizisini tekrar baytlara dönüştür
   # extracted_binary_data = bytes(int(''.join(extracted_bits[i:i+8]), 2) for i in range(0, len(extracted_bits), 8))
    extracted_binary_data = correct_and_convert_bits_to_bytes(extracted_bits)
    # Çıkarılan veriyi orijinal veriyle karşılaştır
    return extracted_binary_data == original_binary_data

# Fonksiyonu test et
image_path = 'deneme.bmp'  # Resmin saklandığı dosya yolu
test_key = 'test_key'.encode()  # Test için basit bir anahtar
test_file_paths = ['deneme.txt', 'deneme1.txt']  # Test için dosya yolları

# Şifreli veri oluştur
binary_data = create_data_structure_with_hash(test_file_paths, test_key)

# İkili veriyi resme sakla
new_image = hide_data_in_image(image_path, binary_data)
new_image.save('new_image.bmp')  # Saklanan resmi kaydet

# Saklanan veriyi doğrula
is_data_verified = verify_hidden_data_in_image('new_image.bmp', binary_data)
print(f"Data verification result: {is_data_verified}")

def hide_data_in_image(image_path, binary_data):
    image = Image.open(image_path)
    pixels = list(image.getdata())
    print(binary_data)  
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
    print('newpizels' , len(new_pixels))
    new_image = Image.new(image.mode, image.size)
    new_image.putdata(new_pixels)
    return new_image

def compare_binary_bits_in_hidden_data(image_path, original_binary_bits):
    """
    Compare the original binary bits with the binary bits extracted from the image.

    :param image_path: Path to the image with hidden data
    :param original_binary_bits: The original binary bits that were hidden in the image
    :return: True if the bits match, False otherwise
    """
    # Open the image and get the pixels
    image = Image.open(image_path)
    pixels = list(image.getdata())

    # Extract the least significant bits from each pixel
    extracted_bits = []
    for pixel in pixels:
        for channel in pixel[:3]:  # RGB channels
            extracted_bits.append(str(channel & 1))
    #print(extracted_bits)
    # Compare the extracted bits with the original bits
    bit_string = ''.join(extracted_bits)
    print(len(bit_string))
    return bit_string == original_binary_bits

original_binary_bits = ''.join([format(byte, '08b') for byte in binary_data])

print(len(original_binary_bits))
print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
# Compare the original binary bits with the extracted bits
result = compare_binary_bits_in_hidden_data('new_image.bmp', original_binary_bits)
print(f"Comparison result: {result}")



# Test the function
extracted_bits = original_binary_bits
extracted_binary_data = correct_and_convert_bits_to_bytes(extracted_bits)
print(extracted_binary_data)
print(extracted_binary_data == binary_data)
