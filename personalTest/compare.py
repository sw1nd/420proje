from PIL import Image

def compare_image_lsb(image_path1, image_path2):
    # İki resmi aç
    image1 = Image.open(image_path1)
    image2 = Image.open(image_path2)

    # Resimlerin boyutlarını kontrol et
    if image1.size != image2.size:
        raise ValueError("Images do not have the same dimensions.")

    pixels1 = list(image1.getdata())
    pixels2 = list(image2.getdata())

    # LSB farklılıklarını say
    lsb_differences = 0

    # Pikselleri ve renk kanallarını karşılaştır
    for (pixel1, pixel2) in zip(pixels1, pixels2):
        for channel1, channel2 in zip(pixel1, pixel2):
            # En az anlamlı bitleri karşılaştır
            if (channel1 & 1) != (channel2 & 1):
                lsb_differences += 1

    return lsb_differences

from PIL import Image

def compare_image_bits_except_lsb(image_path1, image_path2):
    # İki resmi aç
    image1 = Image.open(image_path1)
    image2 = Image.open(image_path2)

    # Resimlerin boyutlarını kontrol et
    if image1.size != image2.size:
        raise ValueError("Images do not have the same dimensions.")

    pixels1 = list(image1.getdata())
    pixels2 = list(image2.getdata())

    # LSB hariç bit farklılıklarını say
    non_lsb_differences = 0

    # Pikselleri ve renk kanallarını karşılaştır
    for (pixel1, pixel2) in zip(pixels1, pixels2):
        for channel_index in range(len(pixel1)):
            # En az anlamlı bit hariç diğer bitleri karşılaştır (0xFE ile AND işlemi yaparak LSB'yi sıfırlarız)
            if (pixel1[channel_index] & 0xFE) != (pixel2[channel_index] & 0xFE):
                non_lsb_differences += 1

    return non_lsb_differences

# Fonksiyonu test et
image_path_1 = 'personalTest/deneme.bmp'
image_path_2 = 'personalTest/rere.bmp'
difference_count = compare_image_bits_except_lsb(image_path_1, image_path_2)
print(f"Total non-LSB differences: {difference_count}")

# Fonksiyonu test et

difference_count = compare_image_lsb(image_path_1, image_path_2)
print(f"Total LSB differences: {difference_count}")
