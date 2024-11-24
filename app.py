from flask import Flask, request, send_file, jsonify
from spleeter.separator import Separator
import os
import shutil
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)

# Allow cross-origin requests (CORS)
from flask_cors import CORS
CORS(app)

# Initialize Spleeter
separator = Separator('spleeter:4stems')

# Endpoint for processing audio
@app.route('/process-audio', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save the uploaded file
    filename = secure_filename(file.filename)
    input_path = os.path.join('uploads', filename)
    output_path = os.path.join('outputs', filename.split('.')[0])
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)

    file.save(input_path)

    try:
        # Run Spleeter to separate stems
        separator.separate_to_file(input_path, output_path)

        # Create a zip file of the stems
        zip_path = f"{output_path}.zip"
        shutil.make_archive(output_path, 'zip', output_path)

        # Clean up original files
        os.remove(input_path)
        shutil.rmtree(output_path)

        # Send zip file as response
        return send_file(zip_path, as_attachment=True, download_name='stems.zip')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Cleanup zip file after sending
        if os.path.exists(zip_path):
            os.remove(zip_path)

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
