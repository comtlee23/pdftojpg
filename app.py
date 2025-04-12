# app.py

import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from datetime import datetime

# 설정
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'static/output'
ALLOWED_EXTENSIONS = {'pdf'}

# Poppler 경로 (윈도우 사용 시만 지정, Mac/Linux는 생략 가능)
# POPPLER_PATH = r"C:\poppler-24.02.0\Library\bin"
POPPLER_PATH = None  # macOS/Linux인 경우 None 유지

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# 폴더 없으면 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'pdf_file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})

    file = request.files['pdf_file']

    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # 현재 시간으로 파일 이름 고유화
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_image_name = f"converted_{timestamp}.jpg"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_image_name)

            # PDF → 이미지 변환
            images = convert_from_path(filepath, dpi=200, poppler_path=POPPLER_PATH)
            images[0].save(output_path, 'JPEG')  # 첫 페이지만 저장

            return jsonify({
                'success': True,
                'download_url': f'/static/output/{output_image_name}'
            })

        except Exception as e:
            print("변환 오류:", e)
            return jsonify({'success': False, 'error': str(e)})

    return jsonify({'success': False, 'error': 'Invalid file'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug = True)
