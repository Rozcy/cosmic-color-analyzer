from image_analyzer import analyze_image_colors
import os
import hashlib
import re
from typing import Dict, Optional
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

# Global constants
PORT = 8080
HOST = '127.0.0.1'
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
CHUNK_SIZE = 8 * 1024  # 8KB
UPLOAD_FOLDER = 'uploads'

# HTTP status codes
HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_SERVER_ERROR = 500

# MIME types
MIME_JSON = 'application/json'
MIME_HTML = 'text/html'
MIME_CSS = 'text/css'
MIME_JS = 'application/javascript'

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class ImageAnalyzerHandler(BaseHTTPRequestHandler):
    last_uploaded_image = None

    def __init__(self, *args, **kwargs):
        self.last_error_message = ""
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handles GET requests."""
        if self.path == '/' or self.path == '/index.html':
            self.serve_file('index.html', MIME_HTML)
        elif self.path == '/styles.css':
            self.serve_file('styles.css', MIME_CSS)
        elif self.path == '/script.js':
            self.serve_file('script.js', MIME_JS)
        elif self.path == '/analyze':
            self.handle_analyze_request()
        else:
            self.send_error(HTTP_NOT_FOUND, "File not found")

    def do_POST(self):
        """Handles POST requests."""
        if self.path == '/upload':
            self.handle_upload_request()
        else:
            self.send_error(HTTP_NOT_FOUND, "Endpoint not found")

    def serve_file(self, filename: str, content_type: str):
        """Serves a static file."""
        try:
            with open(filename, 'rb') as file:
                content = file.read()
            self.send_response(HTTP_OK)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(HTTP_NOT_FOUND, "File not found")

    def handle_analyze_request(self):
        """Handles the /analyze endpoint."""
        if ImageAnalyzerHandler.last_uploaded_image:
            colors = analyze_image_colors(ImageAnalyzerHandler.last_uploaded_image)
            response_data = '{"colors":' + str(colors).replace("'", '"') + '}'
            self.send_response(HTTP_OK)
            self.send_header('Content-Type', MIME_JSON)
            self.end_headers()
            self.wfile.write(response_data.encode())
        else:
            self.log_error("No image uploaded yet")
            self.send_error(HTTP_BAD_REQUEST, "No image uploaded yet")

    def handle_upload_request(self):
        """Handles the /upload endpoint."""
        content_type = self.headers.get('Content-Type', '')
        if content_type.startswith('multipart/form-data'):
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > MAX_REQUEST_SIZE:
                self.send_error(HTTP_BAD_REQUEST, "Request too large")
                return

            body = self.rfile.read(content_length)
            form_data = self.parse_multipart_form_data(body)

            filename = form_data.get('filename')
            chunk_number = int(form_data.get('chunk', '-1'))
            total_chunks = int(form_data.get('totalChunks', '-1'))
            file_checksum = form_data.get('fileChecksum')
            file_content = form_data.get('file')

            if all([filename, chunk_number != -1, total_chunks != -1, file_checksum, file_content]):
                self.handle_chunk_upload(filename, chunk_number, total_chunks, file_checksum, file_content)
            else:
                missing = [k for k, v in {'filename': filename, 'chunk': chunk_number, 'totalChunks': total_chunks,
                                          'fileChecksum': file_checksum, 'file': file_content}.items() if v is None]
                self.log_error(f"Missing required upload information: {', '.join(missing)}")
                self.send_error(HTTP_BAD_REQUEST, f"Missing required upload information: {', '.join(missing)}")
        else:
            self.log_error(f"Invalid Content-Type: {content_type}")
            self.send_error(HTTP_BAD_REQUEST, f"Invalid Content-Type: {content_type}")

    def handle_chunk_upload(self, filename: str, chunk_number: int, total_chunks: int, file_checksum: str, file_content: bytes):
        """Handles the upload of a single chunk."""
        temp_file_path = os.path.join(UPLOAD_FOLDER, f"{filename}.part")
        with open(temp_file_path, 'ab') as f:
            f.write(file_content)

        if chunk_number == total_chunks - 1:
            # All chunks received, verify checksum
            with open(temp_file_path, 'rb') as f:
                file_data = f.read()
                calculated_checksum = hashlib.md5(file_data).hexdigest()

            if calculated_checksum == file_checksum:
                final_file_path = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.exists(final_file_path):
                    os.remove(final_file_path)
                os.rename(temp_file_path, final_file_path)
                ImageAnalyzerHandler.last_uploaded_image = file_data
                self.send_response(HTTP_OK)
                self.end_headers()
                self.wfile.write(b"Upload successful")
            else:
                os.remove(temp_file_path)
                self.log_error(f"Checksum mismatch. Expected: {file_checksum}, Calculated: {calculated_checksum}")
                self.send_error(HTTP_BAD_REQUEST, "Checksum mismatch")
        else:
            self.send_response(HTTP_OK)
            self.end_headers()
            self.wfile.write(f"Chunk {chunk_number + 1}/{total_chunks} received".encode())

    def parse_multipart_form_data(self, body: bytes) -> Dict[str, Optional[bytes]]:
        """Parses multipart form data from request body."""
        content_type = self.headers.get('Content-Type', '')
        boundary = content_type.split('boundary=')[1].encode()
        parts = body.split(b'--' + boundary)
        data = {}

        for part in parts[1:-1]:  # Skip the first and last empty parts
            if b'\r\n\r\n' in part:
                header, content = part.split(b'\r\n\r\n', 1)
                header_lines = header.split(b'\r\n')
                content_disposition = next((line for line in header_lines if line.startswith(b'Content-Disposition')), None)
                if content_disposition:
                    name_match = re.search(b'name="(.+?)"', content_disposition)
                    if name_match:
                        name = name_match.group(1).decode()
                        if b'filename=' in content_disposition:
                            filename_match = re.search(b'filename="(.+?)"', content_disposition)
                            if filename_match:
                                data['filename'] = filename_match.group(1).decode()
                            data[name] = content.strip(b'\r\n')
                        else:
                            data[name] = content.strip(b'\r\n').decode()

        return data

    def log_error(self, format, *args):
        """Overrides to fix compatibility with base class."""
        self.last_error_message = format % args
        print(f"Error: {self.last_error_message}")

def run_server():
    """Runs the HTTP server."""
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, ImageAnalyzerHandler)
    print(f"Server running on http://{HOST}:{PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()