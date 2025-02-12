# app.py
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
from Huffman import Huffman
import io
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'gif'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['COMPRESSED_FOLDER'] = COMPRESSED_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
        # Save the uploaded file
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        # Prepare output filename
        compressed_filename = f"compressed_{filename}.bin"
        compressed_path = os.path.join(app.config['COMPRESSED_FOLDER'], compressed_filename)
        
        # Compress the file
        huffman = Huffman()
        start_time = time.time()
        
        with open(upload_path, 'rb') as fin, open(compressed_path, 'wb') as fout:
            huffman.compress(fin, fout)
        
        compression_time = time.time() - start_time
        
        # Calculate compression ratio
        original_size = os.path.getsize(upload_path)
        compressed_size = os.path.getsize(compressed_path)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        # Read the compressed file into memory
        with open(compressed_path, 'rb') as f:
            compressed_data = io.BytesIO(f.read())
        
        # Clean up temporary files
        os.remove(upload_path)
        os.remove(compressed_path)
        
        # Prepare the file for download
        compressed_data.seek(0)
        return send_file(
            compressed_data,
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
    
    try:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        # Prepare output filename
        decompressed_filename = f"decompressed_{filename.rsplit('.', 1)[0]}"
        decompressed_path = os.path.join(app.config['COMPRESSED_FOLDER'], decompressed_filename)
        
        # Decompress the file
        huffman = Huffman()
        start_time = time.time()
        
        with open(upload_path, 'rb') as fin, open(decompressed_path, 'wb') as fout:
            huffman.decompress(fin, fout)
        
        decompression_time = time.time() - start_time
        
        # Read the decompressed file into memory
        with open(decompressed_path, 'rb') as f:
            decompressed_data = io.BytesIO(f.read())
        
        # Clean up temporary files
        os.remove(upload_path)
        os.remove(decompressed_path)
        
        # Prepare the file for download
        decompressed_data.seek(0)
        return send_file(
            decompressed_data,
            as_attachment=True,
            download_name=decompressed_filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        flash(f'Error during decompression: {str(e)}')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)