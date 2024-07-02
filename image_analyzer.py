import zlib
from PIL import Image
import io
from typing import List, Tuple, Dict, Optional

# Constants
PNG_SIGNATURE = b'\x89PNG\r\n\x1A\n'
JPEG_SIGNATURE = b'\xFF\xD8'
MAX_COLORS = 5
BYTES_PER_PIXEL_RGB = 3
BYTES_PER_PIXEL_RGBA = 4

def analyze_image_colors(image_data: bytes) -> List[Dict[str, str]]:
    """Analyze the colors in the given image data."""
    image_type = detect_image_type(image_data)
    if image_type == 'unknown':
        print("Error: Unknown image type")
        return []

    print(f"Detected image type: {image_type}")

    pixels = parse_image(image_data, image_type)
    if pixels is None:
        print("Error: Failed to parse image data")
        return []

    return analyze_colors(pixels)

def detect_image_type(data: bytes) -> str:
    """Detect the type of image based on its signature bytes."""
    if data.startswith(PNG_SIGNATURE):
        return 'png'
    elif data.startswith(JPEG_SIGNATURE):
        return 'jpeg'
    return 'unknown'

def parse_image(data: bytes, image_type: str) -> Optional[List[Tuple[int, int, int]]]:
    """Parse the image data based on its type."""
    if image_type == 'png':
        return parse_png(data)
    elif image_type == 'jpeg':
        return parse_jpeg(data)
    else:
        print(f"Error: Unsupported image type: {image_type}")
        return None

def parse_png(data: bytes) -> Optional[List[Tuple[int, int, int]]]:
    """Parse PNG image data."""
    try:
        chunks = parse_png_chunks(data)
        ihdr_data = chunks.get('IHDR')
        idat_data = b''.join(chunks.get('IDAT', []))
        print("HELLO")
        if not ihdr_data or not idat_data:
            raise ValueError("Missing IHDR or IDAT chunks")
        print("HELLO1")
        width, height, bit_depth, color_type = parse_ihdr(ihdr_data)
        print("HELLO2")
        print(f"Image dimensions: {width}x{height}, Bit depth: {bit_depth}, Color type: {color_type}")

        decompressed_data = zlib.decompress(idat_data)
        print(f"Decompressed data size: {len(decompressed_data)}")

        pixels = process_pixel_data(decompressed_data, width, height, color_type)
        print(f"Successfully parsed {len(pixels)} pixels")
        return pixels

    except Exception as e:
        print(f"Error parsing PNG: {str(e)}")
        return None

def parse_png_chunks(data: bytes) -> Dict[str, List[bytes]]:
    """Parse PNG chunks to extract IHDR and IDAT data."""
    chunks = {}
    chunk_start = 8  # Start after PNG signature

    while chunk_start < len(data):
        chunk_type, chunk_data, chunk_start = read_chunk(data, chunk_start)
        print(f"Processing chunk: {chunk_type}, length: {len(chunk_data)}")
        
        if chunk_type not in chunks:
            chunks[chunk_type] = []
        chunks[chunk_type].append(chunk_data)
        
        if chunk_type == 'IEND':
            break

    return chunks

def read_chunk(data: bytes, start: int) -> Tuple[str, bytes, int]:
    """Read a single PNG chunk."""
    if start + 8 > len(data):
        raise ValueError(f"Unexpected end of file at position {start}")
    
    length = int.from_bytes(data[start:start+4], 'big')
    chunk_type = data[start+4:start+8].decode('ascii')
    chunk_end = start + 8 + length
    
    if chunk_end + 4 > len(data):
        raise ValueError(f"Chunk {chunk_type} data exceeds file length")
    
    chunk_data = data[start+8:chunk_end]
    return chunk_type, chunk_data, chunk_end + 4

def parse_ihdr(ihdr_data: bytes) -> Tuple[int, int, int, int]:
    """Parse the IHDR chunk of a PNG image."""
    print("Parsing IHDR data...")
    print(f"IHDR data length: {len(ihdr_data)}")
    print(f"IHDR data: {ihdr_data}")

    ihdr_bytes = ihdr_data[0]  # Get the bytes object from the list

    width = int.from_bytes(ihdr_bytes[0:4], 'big')
    print(f"Width: {width}")

    height = int.from_bytes(ihdr_bytes[4:8], 'big')
    print(f"Height: {height}")

    bit_depth = ihdr_bytes[8]
    print(f"Bit depth: {bit_depth}")

    color_type = ihdr_bytes[9]
    print(f"Color type: {color_type}")

    print("Finished parsing IHDR data.")
    return width, height, bit_depth, color_type

def process_pixel_data(data: bytes, width: int, height: int, color_type: int) -> List[Tuple[int, int, int]]:
    """Process the decompressed pixel data of a PNG image."""
    bytes_per_pixel = BYTES_PER_PIXEL_RGBA if color_type == 6 else BYTES_PER_PIXEL_RGB
    stride = width * bytes_per_pixel + 1  # bytes per pixel + 1 byte for filter type
    pixels = []
    previous_row_data = None

    for y in range(height):
        row_start = y * stride
        row_end = row_start + stride
        filter_type = data[row_start]
        row_data = list(data[row_start + 1 : row_end])

        unfiltered = unfilter(filter_type, row_data, previous_row_data, bytes_per_pixel)
        row_pixels = [tuple(unfiltered[i:i+bytes_per_pixel][:3]) for i in range(0, len(unfiltered), bytes_per_pixel)]
        pixels.extend(row_pixels)

        previous_row_data = unfiltered

    return pixels

def unfilter(filter_type: int, current: List[int], previous: Optional[List[int]], bytes_per_pixel: int) -> List[int]:
    """Apply reverse filtering to a scanline of PNG image data."""
    result = []
    for i in range(len(current)):
    
        x = current[i]
        a = current[i - bytes_per_pixel] if i >= bytes_per_pixel else 0
        b = previous[i] if previous and i < len(previous) else 0
        c = previous[i - bytes_per_pixel] if previous and i >= bytes_per_pixel else 0
        
        if filter_type == 0:  # None
            result.append(x)
        elif filter_type == 1:  # Sub
            result.append((x + a) % 256)
        elif filter_type == 2:  # Up
            result.append((x + b) % 256)
        elif filter_type == 3:  # Average
            result.append((x + (a + b) // 2) % 256)
        elif filter_type == 4:  # Paeth
            result.append((x + paeth_predictor(a, b, c)) % 256)
        else:
            raise ValueError(f"Unknown filter type: {filter_type}")
    return result

def paeth_predictor(a: int, b: int, c: int) -> int:
    """Implement the Paeth predictor function for PNG filtering."""
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    elif pb <= pc:
        return b
    else:
        return c

def parse_jpeg(data: bytes) -> Optional[List[Tuple[int, int, int]]]:
    """Parse JPEG image data using PIL."""
    try:
        with Image.open(io.BytesIO(data)) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            pixels = list(img.getdata())
            print(f"Extracted {len(pixels)} pixels from JPEG")
            return pixels
    except Exception as e:
        print(f"Error parsing JPEG: {str(e)}")
        return None

def analyze_colors(pixels: List[Tuple[int, int, int]]) -> List[Dict[str, str]]:
    """Analyze the colors in the given pixel data."""
    color_count = {}
    total_pixels = len(pixels)

    for pixel in pixels:
        if pixel in color_count:
            color_count[pixel] += 1
        else:
            color_count[pixel] = 1

    sorted_colors = sorted(color_count.items(), key=lambda x: x[1], reverse=True)
    top_colors = sorted_colors[:MAX_COLORS]

    results = []
    for color, count in top_colors:
        percentage = (count / total_pixels) * 100
        results.append({
            'r': str(color[0]),
            'g': str(color[1]),
            'b': str(color[2]),
            'percentage': f'{percentage:.2f}%'
        })

    return results

if __name__ == "__main__":
    # You can add test code here if needed
    pass