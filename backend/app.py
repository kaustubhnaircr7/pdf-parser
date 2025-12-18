import sys
import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

from utils.pdf_utils import extract_text_from_pdf
from utils.issuer_detector import detect_issuer
from parsers.icici_parser import ICICIParser
from parsers.hdfc_parser import HDFCParser
from parsers.icici_parser import ICICIParser
from parsers.hdfc_parser import HDFCParser
from parsers.amex_parser import AmexParser
from parsers.chase_parser import ChaseParser
from parsers.union_parser import UnionParser
from parsers.wellsfargo_parser import WellsFargoParser

app = Flask(__name__)
CORS(app)

def get_parser(issuer, text):
    if issuer == 'icici':
        return ICICIParser(text)
    elif issuer == 'hdfc':
        return HDFCParser(text)
    elif issuer == 'amex':
        return AmexParser(text) # Amex logic refined
    elif issuer == 'chase':
        return ChaseParser(text)
    elif issuer == 'union':
        return UnionParser(text)
    elif issuer == 'wellsfargo':
        return WellsFargoParser(text)
    else:
        return None

def process_pdf(file_path):
    text = extract_text_from_pdf(file_path)
    if not text:
        return {"status": "error", "message": "Failed to extract text from PDF"}
    
    issuer = detect_issuer(text)
    if not issuer:
        return {"status": "error", "message": "Could not detect credit card issuer"}
        
    parser = get_parser(issuer, text)
    if not parser:
        return {"status": "error", "message": f"No parser available for issuer: {issuer}"}
        
    result = parser.parse()
    return result

@app.route('/parse', methods=['POST'])
def parse_endpoint():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file provided"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No file selected"}), 400
        
    # Save temporarily
    temp_path = os.path.join("temp", file.filename)
    os.makedirs("temp", exist_ok=True)
    file.save(temp_path)
    
    try:
        result = process_pdf(temp_path)
        return jsonify(result)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    # CLI Mode: Check if a file argument is provided
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            print(f"Processing {file_path}...")
            result = process_pdf(file_path)
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: File not found - {file_path}")
    else:
        # Server Mode
        print("Starting Flask server on port 5000...")
        app.run(debug=True, port=5000)
