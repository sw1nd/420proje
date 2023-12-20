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

# Fonksiyonu test et
image_path = 'deneme.bmp'  # Resmin saklandığı dosya yolu
test_key = 'test_key'.encode()  # Test için basit bir anahtar
test_file_paths = ['deneme.txt', 'deneme1.txt']  # Test için dosya yolları

# Şifreli veri oluştur
binary_data = create_data_structure_with_hash(test_file_paths, test_key)

# Saklanan veriyi doğrula

original_binary_bits = ''.join([format(byte, '08b') for byte in binary_data])



# Test the function
extracted_bits = original_binary_bits
extracted_binary_data = correct_and_convert_bits_to_bytes(extracted_bits)
print(extracted_binary_data)
print('Comparison result:',extracted_binary_data == binary_data)
