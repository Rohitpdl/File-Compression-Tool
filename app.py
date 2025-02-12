from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
from huffman import HuffmanCodec
import io
import time
from typing import BinaryIO, Tuple

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'development-key')

# Configure constants
UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB limit

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

app.config.update(
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    COMPRESSED_FOLDER=COMPRESSED_FOLDER,
    MAX_CONTENT_LENGTH=MAX_CONTENT_LENGTH
)

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_file(input_stream: BinaryIO, operation_type: str) -> Tuple[bytes, float, float]:
    """
    Process a file using Huffman compression/decompression
    Returns: (processed_data, processing_time, compression_ratio)
    """
    start_time = time.time()
    codec = HuffmanCodec()
    
    # Create input/output buffers
    output_buffer = io.BytesIO()
    input_size = 0
    
    try:
        # Get original file size
        input_stream.seek(0, 2)  # Seek to end
        input_size = input_stream.tell()
        input_stream.seek(0)  # Reset to beginning
        
        # Process the file
        if operation_type == 'compress':
            codec.compress(input_stream, output_buffer)
        else:  # decompress
            codec.decompress(input_stream, output_buffer)
        
        processing_time = time.time() - start_time
        
        # Calculate compression ratio for compression operations
        output_size = output_buffer.tell()
        compression_ratio = ((input_size - output_size) / input_size * 100) if operation_type == 'compress' else 0
        
        return output_buffer.getvalue(), processing_time, compression_ratio
        
    except Exception as e:
        raise RuntimeError(f"Error during {operation_type}: {str(e)}")

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type')
        return redirect(url_for('index'))
    
    try:
        filename = secure_filename(file.filename)
        compressed_filename = f"compressed_{filename}.huf"
        
        # Process the file
        compressed_data, processing_time, compression_ratio = process_file(file.stream, 'compress')
        
        # Create response data
        output_buffer = io.BytesIO(compressed_data)
        output_buffer.seek(0)
        
        # Add compression stats to flash message
        flash(f'Compression complete: {compression_ratio:.1f}% reduction in {processing_time:.2f} seconds')
        
        return send_file(
            output_buffer,
            as_attachment=True,
            download_name=compressed_filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        flash(f'Error during compression: {str(e)}')
        return redirect(url_for('index'))

@app.route('/decompress', methods=['POST'])
def decompress_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if not file.filename.endswith('.huf'):
        flash('Invalid compressed file type (must be .huf)')
        return redirect(url_for('index'))
    
    try:
        filename = secure_filename(file.filename)
        decompressed_filename = filename.rsplit('.huf', 1)[0]
        
        # Process the file
        decompressed_data, processing_time, _ = process_file(file.stream, 'decompress')
        
        # Create response data
        output_buffer = io.BytesIO(decompressed_data)
        output_buffer.seek(0)
        
        # Add decompression stats to flash message
        flash(f'Decompression complete in {processing_time:.2f} seconds')
        
        return send_file(
            output_buffer,
            as_attachment=True,
            download_name=decompressed_filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        flash(f'Error during decompression: {str(e)}')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)