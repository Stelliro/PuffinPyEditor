# PuffinPyEditor/installer/create_header_image.py
import os
import struct

def create_bmp_image():
    """
    Generates a 496x58 pixel, 24-bit BMP header image with a solid color.
    This script creates the header asset required by the NSIS installer script.
    """
    # --- Configuration ---
    img_width = 496
    img_height = 58
    bits_per_pixel = 24
    # A color from the PuffinPy Dark theme sidebar (#2a3338)
    # BMP stores colors as BGR (Blue, Green, Red)
    bg_color_bgr = (0x38, 0x33, 0x2a)

    # --- Create Folders ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "assets")
    output_path = os.path.join(assets_dir, "PuffinPyEditor_Header.bmp")

    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        print(f"Created directory: {assets_dir}")

    # --- BMP Header Calculation ---
    bytes_per_pixel = bits_per_pixel // 8
    row_size_unpadded = img_width * bytes_per_pixel
    padding = (4 - (row_size_unpadded % 4)) % 4
    row_size_padded = row_size_unpadded + padding

    pixel_data_size = row_size_padded * img_height
    file_header_size = 14
    info_header_size = 40
    file_size = file_header_size + info_header_size + pixel_data_size

    # --- Write File ---
    try:
        with open(output_path, 'wb') as f:
            # --- BITMAPFILEHEADER (14 bytes) ---
            f.write(b'BM')
            f.write(struct.pack('<L', file_size))
            f.write(struct.pack('<H', 0))
            f.write(struct.pack('<H', 0))
            f.write(struct.pack('<L', file_header_size + info_header_size))

            # --- BITMAPINFOHEADER (40 bytes) ---
            f.write(struct.pack('<L', info_header_size))
            f.write(struct.pack('<L', img_width))
            f.write(struct.pack('<L', img_height))
            f.write(struct.pack('<H', 1))
            f.write(struct.pack('<H', bits_per_pixel))
            f.write(struct.pack('<L', 0))
            f.write(struct.pack('<L', pixel_data_size))
            f.write(struct.pack('<L', 0))
            f.write(struct.pack('<L', 0))
            f.write(struct.pack('<L', 0))
            f.write(struct.pack('<L', 0))

            # --- Pixel Data ---
            padding_bytes = b'\x00' * padding
            for _ in range(img_height):
                for _ in range(img_width):
                    f.write(struct.pack('BBB', *bg_color_bgr))
                f.write(padding_bytes)

        print(f"\nSUCCESS: Created installer header asset '{output_path}'")
        return True

    except Exception as e:
        print(f"\nERROR: Failed to create BMP header image. Reason: {e}")
        return False

if __name__ == "__main__":
    create_bmp_image()