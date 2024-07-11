# Cosmic Color Analyzer

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Technologies Used](#technologies-used)
4. [Project Structure](#project-structure)
5. [Detailed Component Breakdown](#detailed-component-breakdown)
   
   5.1. [Server (server.py)](#server-serverpy)
   
   5.2. [Image Analyzer (image_analyzer.py)](#image-analyzer-image_analyzerpy)
   
   5.3. [Frontend (index.html, styles.css, script.js)](#frontend-indexhtml-stylescss-scriptjs)

6. [Setup and Installation](#setup-and-installation)
7. [How It Works](#how-it-works)
8. [Dependencies Explained](#dependencies-explained)
9. [Design Decisions and Rationale](#design-decisions-and-rationale)
10. [Image Analyzer: A Deep Dive](#image-analyzer-a-deep-dive)

## Introduction

The Cosmic Color Analyzer is a web application that allows users to upload images and analyze the dominant colors present in them. It showcases a unique approach to image processing by implementing custom PNG parsing and using minimal external libraries for JPEG handling. This project demonstrates low-level image manipulation, client-server communication, and frontend development techniques.

## Features

- Custom PNG parsing and analysis without relying on external image processing libraries
- JPEG support using minimal PIL functionality
- Large file handling through chunked uploads
- Client-side file integrity checks using MD5 checksums
- Server-side image processing and color analysis
- Display of top 5 dominant colors with their RGB values and percentages
- Responsive design for various screen sizes

## Technologies Used

- Frontend: HTML5, CSS3, JavaScript (ES6+)
- Backend: Python 3.x
- HTTP Server: Python's built-in `http.server` module
- Image Processing: 
  - Custom implementation for PNG parsing and analysis
  - PIL (Python Imaging Library) for opening JPEG images only
- Checksum Calculation: CryptoJS (client-side), hashlib (server-side)

## Project Structure

```
cosmic-color-analyzer/
│
├── server.py
├── image_analyzer.py
├── index.html
├── styles.css
├── script.js
└── uploads/
```

## Detailed Component Breakdown

### Server (server.py)

The server component is built using Python's built-in `http.server` module. This decision was made to minimize external dependencies and demonstrate how to create a basic HTTP server from scratch.

Key components:

1. `ImageAnalyzerHandler` class:
   - Inherits from `BaseHTTPRequestHandler`
   - Handles GET and POST requests
   - Implements file serving, upload handling, and color analysis requests

2. File serving:
   - `do_GET` method serves static files (HTML, CSS, JS)
   - `serve_file` method reads and sends file content with appropriate MIME types

3. Upload handling:
   - `do_POST` method handles file uploads
   - `handle_upload_request` parses multipart form data
   - `handle_chunk_upload` manages chunked file uploads and reassembly

4. Color analysis:
   - `handle_analyze_request` calls the image analyzer and returns results

5. Utility methods:
   - `parse_multipart_form_data` for parsing form data
   - `log_error` for error logging

Design decisions:
- Using `http.server` showcases how to build a basic server without frameworks
- Chunked uploads allow handling of large files
- In-memory processing of uploads improves performance but limits scalability

### Image Analyzer (image_analyzer.py)

This component contains the core logic for image parsing and color analysis. It showcases low-level image manipulation techniques.

Key components:

1. PNG Parsing:
   - `parse_png_chunks`: Extracts chunks from PNG file
   - `parse_ihdr`: Parses image header information
   - `process_pixel_data`: Handles pixel data extraction and decompression
   - `unfilter`: Implements PNG unfiltering algorithms

2. JPEG Handling:
   - Uses PIL to open JPEG images and extract pixel data

3. Color Analysis:
   - `analyze_colors`: Counts color occurrences and calculates percentages

Design decisions:
- Custom PNG parsing demonstrates low-level file format handling
- Minimal use of PIL for JPEG showcases integration with external libraries
- Color analysis algorithm prioritizes speed over memory efficiency

### Frontend (index.html, styles.css, script.js)

The frontend provides a user-friendly interface for image upload and result display.

Key components:

1. HTML Structure:
   - Simple form for file input
   - Progress bar for upload tracking
   - Results display area

2. CSS Styling:
   - Responsive design using flexbox
   - Custom styling for file input and buttons
   - Animated progress bar

3. JavaScript Functionality:
   - File selection and preview
   - Chunked file upload implementation
   - Client-side MD5 checksum calculation
   - AJAX requests for upload and analysis
   - Dynamic result display

Design decisions:
- Chunked uploads in JavaScript allow handling large files
- Client-side checksum ensures file integrity
- Responsive design improves usability across devices

## Setup and Installation

1. Ensure you have Python 3.x installed on your system.
2. Clone this repository:
   ```
   git clone https://github.com/YegorCherov/cosmic-color-analyzer.git
   cd cosmic-color-analyzer
   ```
3. Install the required Python packages:
   ```
   pip install pillow
   ```
   Note: Pillow is only used for opening JPEG images. The rest of the processing uses custom implementations.
4. Run the server:
   ```
   python server.py
   ```
5. Open a web browser and navigate to `http://localhost:8080` to use the application.

## How It Works

1. User selects an image file through the web interface.
2. JavaScript calculates MD5 checksum and initiates chunked upload.
3. Server receives chunks, reassembles the file, and verifies integrity.
4. User initiates color analysis.
5. Server processes the image:
   - For PNG: Custom parsing and analysis
   - For JPEG: Opens with PIL, then custom analysis
6. Analysis results are sent back to the client and displayed.

## Dependencies Explained

1. `zlib`: Used for decompressing PNG image data. Essential for handling PNG compression.
2. `PIL` (Python Imaging Library): Used only for opening JPEG images. Chosen for its simplicity in handling JPEG files.
3. `io`: Provides byte stream handling, crucial for in-memory file operations.
4. `typing`: Enhances code readability and helps catch type-related errors early.
5. `os`: Used for file and directory operations, essential for managing uploaded files.
6. `hashlib`: Generates MD5 checksums for file integrity verification.
7. `re`: Used in parsing multipart form data, crucial for handling file uploads.
8. `http.server`: The backbone of the server implementation.
9. `urllib.parse`: Assists in parsing URL components and query strings.

## Design Decisions and Rationale

1. Custom PNG Parsing:
   - Rationale: Educational value and fine-grained control over the process.
   - Trade-off: Increased complexity vs. learning opportunity and potential performance optimization.

2. Minimal Use of PIL for JPEG:
   - Rationale: Balance between reinventing the wheel and using established libraries.
   - Trade-off: Slight increase in dependencies vs. reliable JPEG handling.

3. Chunked Uploads:
   - Rationale: Allows handling of large files without overwhelming server memory.
   - Trade-off: Increased complexity vs. improved scalability.

4. In-Memory Processing:
   - Rationale: Simplifies implementation and improves performance for small to medium files.
   - Trade-off: Limited scalability for very large files or high concurrency.

5. Client-Side Checksum:
   - Rationale: Ensures file integrity before and after upload.
   - Trade-off: Slight performance impact vs. improved reliability.


&nbsp;
# Image Analyzer: A Deep Dive

## 1. Introduction to Digital Images

Before we delve into the code, let's understand what a digital image is:

- A digital image is a two-dimensional array of pixels.
- Each pixel represents a color and is typically stored as a combination of red, green, and blue (RGB) values.
- In most computer systems, each color channel (R, G, or B) is represented by a number from 0 to 255.

For example, (255, 0, 0) represents pure red, (0, 255, 0) is pure green, and (0, 0, 255) is pure blue.

## 2. Image File Formats: PNG and JPEG

The analyzer handles two popular image formats: PNG and JPEG. Let's understand these formats:

### 2.1 PNG (Portable Network Graphics)

PNG is a lossless compression format, meaning it preserves image quality perfectly.

Key characteristics:
- Uses a series of "chunks" to store data
- Supports transparency
- Uses filtering and compression for efficient storage

### 2.2 JPEG (Joint Photographic Experts Group)

JPEG is a lossy compression format, meaning it sacrifices some image quality to achieve smaller file sizes.

Key characteristics:
- Divides image into blocks and applies frequency-based compression
- Doesn't support transparency
- Ideal for photographs and complex images with smooth color transitions

## 3. The Image Analyzer Structure

Now, let's break down the `image_analyzer.py` file:

```python
import zlib
from PIL import Image
import io
from typing import List, Tuple, Dict, Optional

# ... (rest of the code)
```

- `zlib`: A library for data compression and decompression. PNG uses zlib compression.
- `PIL`: Python Imaging Library, used here for handling JPEG images.
- `io`: Provides tools for working with I/O (input/output) operations, useful for handling byte streams.
- `typing`: Provides support for type hints, making the code more readable and maintainable.

## 4. Analyzing Image Colors

The main function `analyze_image_colors` is the entry point:

```python
def analyze_image_colors(image_data: bytes) -> List[Dict[str, str]]:
    # ... (function body)
```

This function takes raw image data as bytes and returns a list of dictionaries, each representing a dominant color.

### 4.1 Image Type Detection

```python
def detect_image_type(data: bytes) -> str:
    # ... (function body)
```

This function looks at the first few bytes of the image data to determine if it's PNG or JPEG:
- PNG files start with the bytes `89 50 4E 47 0D 0A 1A 0A` (in hexadecimal)
- JPEG files typically start with `FF D8`

### 4.2 Parsing PNG Images

PNG parsing is done manually, which is complex but educational:

```python
def parse_png(data: bytes) -> Optional[List[Tuple[int, int, int]]]:
    # ... (function body)
```

#### PNG Structure

A PNG file consists of:
1. A fixed signature
2. A series of chunks, each with:
   - Length (4 bytes)
   - Chunk type (4 bytes)
   - Chunk data (variable length)
   - CRC (Cyclic Redundancy Check, 4 bytes)

Important chunks:
- IHDR: Contains basic information about the image (width, height, bit depth, color type)
- IDAT: Contains the actual image data, compressed using zlib
- IEND: Marks the end of the PNG datastream

#### PNG Parsing Process

1. Parse PNG chunks:
   ```python
   def parse_png_chunks(data: bytes) -> Dict[str, List[bytes]]:
       # ... (function body)
   ```
   This function separates the PNG file into its constituent chunks.

2. Parse IHDR chunk:
   ```python
   def parse_ihdr(ihdr_data: bytes) -> Tuple[int, int, int, int]:
       # ... (function body)
   ```
   Extracts width, height, bit depth, and color type from the IHDR chunk.

3. Process pixel data:
   ```python
   def process_pixel_data(data: bytes, width: int, height: int, color_type: int) -> List[Tuple[int, int, int]]:
       # ... (function body)
   ```
   This is where the magic happens:
   - Decompress the IDAT chunk data using zlib
   - "Unfilter" the data (reverse the PNG filtering process)
   - Extract RGB values for each pixel

#### PNG Filtering and Unfiltering

PNG uses a technique called filtering to improve compression:

```python
def unfilter(filter_type: int, current: List[int], previous: Optional[List[int]], bytes_per_pixel: int) -> List[int]:
    # ... (function body)
```

For each scanline (row of pixels), PNG applies one of five filter types:
0. None: No filtering
1. Sub: Subtract the value of the pixel to the left
2. Up: Subtract the value of the pixel above
3. Average: Subtract the average of the left and above pixels
4. Paeth: A special predictor that chooses the most similar of left, above, or upper-left pixel

The `unfilter` function reverses this process to recover the original pixel values.

### 4.3 Parsing JPEG Images

JPEG parsing is simpler because it uses PIL:

```python
def parse_jpeg(data: bytes) -> Optional[List[Tuple[int, int, int]]]:
    # ... (function body)
```

- Opens the JPEG data using PIL
- Converts to RGB mode if necessary
- Extracts pixel data

Using PIL for JPEG is simpler because JPEG decompression is more complex than PNG and would require significantly more code to implement manually.

### 4.4 Color Analysis

Once we have the pixel data, we analyze the colors:

```python
def analyze_colors(pixels: List[Tuple[int, int, int]]) -> List[Dict[str, str]]:
    # ... (function body)
```

This function:
1. Counts the occurrence of each unique color
2. Sorts colors by frequency
3. Selects the top 5 colors
4. Calculates the percentage of each top color
5. Formats the results as a list of dictionaries