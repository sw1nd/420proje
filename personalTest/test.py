from backend.stegano_backend import *
def decrypt_and_validate_data(encrypted_data, key):
    # Şifreli veriyi AES ile şifre çözme
    decrypted_data = decrypt_aes(encrypted_data, key)

    # Şifre çözülen veriyi parçalara ayır
    files_data = decrypted_data.split(DELIMITER)

    # Dosya içeriklerini ve hash değerlerini saklamak için bir sözlük
    extracted_files = {}

    # Dosya ismi, hash değeri ve içeriği çıkarma ve doğrulama
    for i in range(0, len(files_data) - 1, 3):
        file_name = files_data[i]
        hash_value = files_data[i + 1]
        file_content = files_data[i + 2]

        # MD5 hash doğrulaması
        calculated_hash = create_md5_hash(file_content)
        if hash_value == calculated_hash:
            extracted_files[file_name] = file_content
        else:
            print(f"Warning: The file '{file_name}' may have been tampered with or corrupted.")

    return extracted_files

# Fonksiyonu test et
test_key = 'test_key'.encode()  # Test için basit bir anahtar
test_file_paths = ['deneme.txt', 'deneme1.txt']  # Test için dosya yolları

# Şifreli veri oluştur
encrypted_data = create_data_structure_with_hash(test_file_paths, test_key)

# Şifreli veriyi çöz ve içeriği doğrula
extracted_files = decrypt_and_validate_data(encrypted_data, test_key)
for file_name, content in extracted_files.items():
    print(f"File: {file_name}, Content: {content}")
