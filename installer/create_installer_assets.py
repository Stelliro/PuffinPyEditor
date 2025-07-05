# PuffinPyEditor/installer/create_installer_assets.py
import os
import struct
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette

# --- Helper Functions for creating BMP and ICO files ---

def create_bmp(width: int, height: int, color_hex: str, output_path: Path):
    """Generates a solid-color, 24-bit BMP file."""
    try:
        color_hex = color_hex.lstrip('#')
        # BMP uses BGR order
        bgr_color = tuple(int(color_hex[i:i + 2], 16) for i in (4, 2, 0))
    except (ValueError, IndexError):
        print(f"ERROR: Invalid color hex provided for BMP: {color_hex}")
        return False

    bytes_per_pixel = 3
    row_size_unpadded = width * bytes_per_pixel
    padding = (4 - (row_size_unpadded % 4)) % 4
    row_size_padded = row_size_unpadded + padding
    pixel_data_size = row_size_padded * height
    file_header_size, info_header_size = 14, 40
    file_size = file_header_size + info_header_size + pixel_data_size

    try:
        with open(output_path, 'wb') as f:
            # BITMAPFILEHEADER
            f.write(b'BM')
            f.write(struct.pack('<L', file_size))
            f.write(struct.pack('<HH', 0, 0)) # Reserved
            f.write(struct.pack('<L', file_header_size + info_header_size))
            
            # BITMAPINFOHEADER
            f.write(struct.pack('<L', info_header_size))
            f.write(struct.pack('<l', width))
            f.write(struct.pack('<l', height))
            f.write(struct.pack('<H', 1)) # Planes
            f.write(struct.pack('<H', 24)) # Bits per pixel
            f.write(struct.pack('<L', 0)) # Compression (BI_RGB)
            f.write(struct.pack('<L', pixel_data_size))
            f.write(struct.pack('<LLLL', 0, 0, 0, 0)) # XPels, YPels, ClrUsed, ClrImportant
            
            # Pixel Data (bottom-to-top scanlines)
            padding_bytes = b'\x00' * padding
            for _ in range(height):
                for _ in range(width):
                    f.write(struct.pack('BBB', *bgr_color))
                f.write(padding_bytes)
                
        print(f"SUCCESS: Created BMP asset '{output_path.name}'")
        return True
    except IOError as e:
        print(f"ERROR: Failed to write BMP '{output_path}': {e}")
        return False

def create_ico(size: int, color_hex: str, output_path: Path):
    """Generates a solid-color, 32-bit ICO file."""
    try:
        color_hex = color_hex.lstrip('#')
        # ICO uses BGRA order for its internal BMP
        bgra_color = tuple(int(color_hex[i:i + 2], 16) for i in (4, 2, 0)) + (255,) # Add full alpha
    except (ValueError, IndexError):
        print(f"ERROR: Invalid color hex provided for ICO: {color_hex}")
        return False

    # DIB (Device-Independent Bitmap) Data for the ICO
    # BITMAPINFOHEADER
    # Height is doubled to account for the XOR mask (color) and AND mask (transparency)
    info_header = struct.pack('<lllHHLLllLL', 40, size, size * 2, 1, 32, 0, 0, 0, 0, 0, 0)
    
    # XOR mask (color data)
    xor_mask = bytearray(struct.pack('<BBBB', *bgra_color) * (size * size))
    
    # AND mask (transparency data, 1 bit per pixel). All 0s for fully opaque.
    and_mask = bytearray([0x00] * (size * size // 8))
    
    dib_data = info_header + xor_mask + and_mask
    dib_size = len(dib_data)

    # ICO File Headers
    # ICONDIR (6 bytes)
    icon_dir = struct.pack('<HHH', 0, 1, 1) # Reserved, Type 1 (ICO), 1 image
    
    # ICONDIRENTRY (16 bytes)
    image_offset = 22 # 6 (ICONDIR) + 16 (ICONDIRENTRY)
    icon_dir_entry = struct.pack('<BBBBHHLL', size, size, 0, 0, 1, 32, dib_size, image_offset)

    try:
        with open(output_path, 'wb') as f:
            f.write(icon_dir)
            f.write(icon_dir_entry)
            f.write(dib_data)
        print(f"SUCCESS: Created ICO asset '{output_path.name}'")
        return True
    except IOError as e:
        print(f"ERROR: Failed to create ICO '{output_path}': {e}")
        return False

# --- Main Execution ---
if __name__ == "__main__":
    print("\n--- Generating Installer Assets ---")
    
    # Create a headless QApplication to access system-wide theme information
    app = QApplication(sys.argv)
    palette = app.palette()

    # Get system colors for a native look and feel
    # QPalette.ColorRole.Highlight is the main accent color (e.g., for selected items)
    icon_color = palette.color(QPalette.ColorRole.Highlight).name()
    # QPalette.ColorRole.Button is a good, neutral background for UI elements
    header_bg_color = palette.color(QPalette.ColorRole.Button).name()
    # QPalette.ColorRole.Window is the general window background color
    welcome_bg_color = palette.color(QPalette.ColorRole.Window).name()
    
    print(f"Using system colors: Icon Accent ({icon_color}), Header BG ({header_bg_color}), Welcome BG ({welcome_bg_color})")

    assets_dir = Path(__file__).parent / "assets"
    assets_dir.mkdir(exist_ok=True)

    # Generate all required assets using the system theme colors
    all_ok = all([
        create_ico(32, icon_color, assets_dir / "PuffinPyEditor.ico"),
        create_bmp(496, 58, header_bg_color, assets_dir / "PuffinPyEditor_Header.bmp"),
        create_bmp(164, 314, welcome_bg_color, assets_dir / "welcome.bmp")
    ])

    if not all_ok:
        print("\n--- ERROR: One or more assets failed to generate. ---")
        sys.exit(1)
    
    print("\n--- All installer assets generated successfully. ---")
    sys.exit(0)