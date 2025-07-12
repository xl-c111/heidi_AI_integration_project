from flask import Blueprint, request, jsonify
import os
import fitz  # PyMuPDF

document_bp = Blueprint('document', __name__)

@document_bp.route('/upload-document', methods=['POST'])
def upload_document():
    uploaded_file = request.files.get('file')
    if not uploaded_file or not uploaded_file.filename.endswith('.pdf'):
        return jsonify({"error": "No valid PDF file provided"}), 400

    file_path = os.path.join('/tmp', uploaded_file.filename)
    uploaded_file.save(file_path)

    try:
        # Extract text using PyMuPDF
        doc = fitz.open(file_path)
        full_text = ''
        for page in doc:
            full_text += page.get_text()
        doc.close()

        return jsonify({"text": full_text.strip()})
    except Exception as e:
        return jsonify({"error": f"Failed to extract text: {str(e)}"}), 500
