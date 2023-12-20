from PIL import Image

def load_image_file(file_path):
    img = Image.open(file_path)
    img.thumbnail((200, 200))
    bit_depth = img.mode
    if bit_depth == 'RGB':
        bit_depth_info = '24-bit (8 bits per channel)'
    elif bit_depth == 'RGBA':
        bit_depth_info = '32-bit (8 bits per channel)'
    elif bit_depth == 'L':
        bit_depth_info = '8-bit'
    else:
        bit_depth_info = f'{bit_depth} (unknown bit depth)'

    image_details = f"Name: {file_path.split('/')[-1]}\n" \
                            f"Size: {img.size[0]}x{img.size[1]}\n" \
                            f"Bit Depth: {bit_depth_info}"
    return img, image_details
