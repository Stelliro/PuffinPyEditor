# PuffinPyEditor/installer/create_installer_assets.py
import os
import struct
import argparse
from typing import Tuple


def create_bmp(width: int, height: int, color_hex: str, output_path: str):
    """Generates a solid-color, 24-bit BMP file."""
    try:
        color_hex = color_hex.lstrip('#')
        bgr_color = tuple(int(color_hex[i:i + 2], 16) for i in (4, 2, 0))
    except ValueError:
        print(f"ERROR: Invalid color hex: {color_hex}")
        return False

    bytes_per_pixel = 3
    row_size_unpadded = width * bytes_per_pixel
    padding = (4 - (row_size_unpadded % 4)) % 4
    row_size_padded = row_size_unpadded + padding

    pixel_data_size = row_size_padded * height
    file_header_size = 14
    info_header_size = 40
    file_size = file_header_size + info_header_size + pixel_data_size

    try:
        with open(output_path, 'wb') as f:
            # BITMAPFILEHEADER
            f.write(b'BM')
            f.write(struct.pack('<L', file_size))
            f.write(struct.pack('<HH', 0, 0))
            f.write(struct.pack('<L', file_header_size + info_header_size))
            # BITMAPINFOHEADER
            f.write(struct.pack('<L', info_header_size))
            f.write(struct.pack('<l', width))
            f.write(struct.pack('<l', height))
            f.write(struct.pack('<H', 1))
            f.write(struct.pack('<H', 24))
            f.write(struct.pack('<L', 0))
            f.write(struct.pack('<L', pixel_data_size))
            f.write(struct.pack('<LLLL', 0, 0, 0, 0))
            # Pixel Data
            padding_bytes = b'\x00' * padding
            for _ in range(height):
                for _ in range(width):
                    f.write(struct.pack('BBB', *bgr_color))
                f.write(padding_bytes)
        print(f"SUCCESS: Created BMP asset '{os.path.basename(output_path)}'")
        return True
    except IOError as e:
        print(f"ERROR: Failed to create BMP '{output_path}': {e}")
        return False


def create_ico(size: int, color_hex: str, output_path: str):
    """Generates a solid-color, 32-bit ICO file."""
    try:
        color_hex = color_hex.lstrip('#')
        bgra_color = tuple(int(color_hex[i:i + 2], 16) for i in (4, 2, 0)) + (255,)  # Add alpha
    except ValueError:
        print(f"ERROR: Invalid color hex: {color_hex}")
        return False

    info_header = struct.pack('<lllHHLLllLL', 40, size, size * 2, 1, 32, 0, 0, 0, 0, 0, 0)
    xor_mask = bytearray(struct.pack('<BBBB', *bgra_color) * (size * size))
    and_mask = bytearray([0x00] * (size * size // 8))
    dib_data = info_header + xor_mask + and_mask
    dib_size = len(dib_data)

    icon_dir = struct.pack('<HHH', 0, 1, 1)  # 1 icon in file
    image_offset = 22
    icon_dir_entry = struct.pack('<BBBBHHLL', size, size, 0, 0, 1, 32, dib_size, image_offset)

    try:
        with open(output_path, 'wb') as f:
            f.write(icon_dir)
            f.write(icon_dir_entry)
            f.write(dib_data)
        print(f"SUCCESS: Created ICO asset '{os.path.basename(output_path)}'")
        return True
    except IOError as e:
        print(f"ERROR: Failed to create ICO '{output_path}': {e}")
        return False


if __name__ == "__main__":
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # Generate all required assets from one script
    all_ok = all([
        create_ico(32, "#FF073A", os.path.join(assets_dir, "PuffinPyEditor.ico")),
        create_bmp(496, 58, "#2a3338", os.path.join(assets_dir, "PuffinPyEditor_Header.bmp")),
        create_bmp(164, 314, "#2f383e", os.path.join(assets_dir, "welcome.bmp"))
    ])

    if not all_ok:
        exit(1)