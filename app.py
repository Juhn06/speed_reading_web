from flask import Flask, render_template, request, jsonify
import os
from docx import Document
import PyPDF2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Đảm bảo folder uploads tồn tại
os.makedirs('uploads', exist_ok=True)


# Trang chủ - Upload file
@app.route('/')
def index():
    return render_template('index.html')


# Trang đọc
@app.route('/reader')
def reader():
    return render_template('reader.html')


# Xử lý upload file
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Không có file'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Chưa chọn file'}), 400

    # Lưu file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Đọc nội dung file
    text = read_file(filepath)

    # Tách thành từng từ
    words = text.split()

    return jsonify({
        'words': words,
        'total': len(words),
        'filename': file.filename
    })


# Hàm đọc file theo loại
def read_file(filepath):
    ext = filepath.split('.')[-1].lower()

    if ext == 'txt':
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    elif ext == 'docx':
        doc = Document(filepath)
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text

    elif ext == 'pdf':
        with open(filepath, 'rb') as f:
            pdf = PyPDF2.PdfReader(f)
            text = ''
            for page in pdf.pages:
                text += page.extract_text()
        return text

    else:
        return "Định dạng file không hỗ trợ"


if __name__ == '__main__':
    app.run(debug=True, port=5000)