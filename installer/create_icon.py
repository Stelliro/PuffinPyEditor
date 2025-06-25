# PuffinPyEditor/installer/create_icon.py
import os
import struct

def create_ico_file():
    """
    Generates a simple 32x32 pixel, 32-bit ICO file with a solid color.
    This creates the PuffinPyEditor.ico asset required by the NSIS installer.
    """
    # --- Configuration ---
    width, height = 32, 32
    bits_per_pixel = 32  # Use 32-bit for alpha channel support (BGRA)
    # A color from the PuffinPy Crimson Code theme accent (#FF073A)
    # Stored as BGRA for BMP format within ICO
    color_bgra = (0x3A, 0x07, 0xFF, 0xFF)

    # --- Create Folders ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "assets")
    output_path = os.path.join(assets_dir, "PuffinPyEditor.ico")

    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        print(f"Created directory: {assets_dir}")

    # --- BMP DIB (Device-Independent Bitmap) Data (without BITMAPFILEHEADER) ---
    # BITMAPINFOHEADER (40 bytes)
    info_header = struct.pack(
        '<lllHHLLllLL',
        40,              # biSize (header size)
        width,           # biWidth
        height * 2,      # biHeight (includes XOR mask and AND mask)
        1,               # biPlanes
        bits_per_pixel,  # biBitCount
        0,               # biCompression (BI_RGB)
        0,               # biSizeImage (can be 0 for BI_RGB)
        0,               # biXPelsPerMeter
        0,               # biYPelsPerMeter
        0,               # biClrUsed
        0                # biClrImportant
    )

    # XOR Mask (the actual color data)
    xor_mask = bytearray()
    for _ in range(height):
        for _ in range(width):
            xor_mask.extend(struct.pack('BBBB', *color_bgra))

    # AND Mask (the transparency data, all opaque for this simple icon)
    # 1 bit per pixel, row padded to 4 bytes. 32 pixels = 4 bytes, so no padding needed.
    and_mask = bytearray([0x00] * (width * height // 8))

    dib_data = info_header + xor_mask + and_mask
    dib_size = len(dib_data)

    # --- ICO Header ---
    # ICONDIR (6 bytes)
    icon_dir = struct.pack('<HHH', 0, 1, 1)  # Reserved, Type 1 (ICO), 1 image

    # ICONDIRENTRY (16 bytes)
    # The offset to the DIB data is right after the headers (6 + 16 = 22)
    image_offset = 22
    icon_dir_entry = struct.pack(
        '<BBBBHHLL',
        width if width < 256 else 0,
        height if height < 256 else 0,
        0,               # bColorCount (0 for true color)
        0,               # bReserved
        1,               # wPlanes
        bits_per_pixel,  # wBitCount
        dib_size,        # dwBytesInRes
        image_offset     # dwImageOffset
    )

    # --- Write File ---
    try:
        with open(output_path, 'wb') as f:
            f.write(icon_dir)
            f.write(icon_dir_entry)
            f.write(dib_data)

        print(f"SUCCESS: Created icon asset '{output_path}'")
        return True

    except Exception as e:
        print(f"ERROR: Failed to create ICO file. Reason: {e}")
        return False

if __name__ == "__main__":
    create_ico_file()