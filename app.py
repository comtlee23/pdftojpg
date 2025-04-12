# app.py

import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from datetime import datetime
from zipfile import ZipFile

# ===== 설정 =====
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'static/output'
ALLOWED_EXTENSIONS = {'pdf'}

# poppler 경로 (macOS/Linux는 None, Windows는 경로 지정 필요)
POPPLER_PATH = None  # 예: r"C:\poppler\bin"

app = Flask(__name__, static_folder='static', template_folder='template')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# ===== 폴더 생성 =====
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ===== 파일 확장자 검사 =====
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ===== 홈 페이지 =====
@app.route('/')
def index():
    return render_template('index.html')

# ===== PDF → 이미지 변환 & ZIP 압축 후 다운로드 페이지로 리디렉트 =====
@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'pdf_file' not in request.files:
        return "No file part", 400

    file = request.files['pdf_file']

    if file.filename == '':
        return "No selected file", 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # 고유 파일 이름 생성
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            base_name = f"converted_{timestamp}"

            # PDF → 이미지 변환
            images = convert_from_path(filepath, dpi=200, poppler_path=POPPLER_PATH)

            # 이미지 저장
            image_filenames = []
            for i, image in enumerate(images):
                image_filename = f"{base_name}_page_{i+1}.jpg"
                image_path = os.path.join(app.config['OUTPUT_FOLDER'], image_filename)
                image.save(image_path, 'JPEG')
                image_filenames.append(image_path)

            # ZIP 압축 생성
            zip_filename = f"{base_name}.zip"
            zip_path = os.path.join(app.config['OUTPUT_FOLDER'], zip_filename)
            with ZipFile(zip_path, 'w') as zipf:
                for img_path in image_filenames:
                    arcname = os.path.basename(img_path)
                    zipf.write(img_path, arcname=arcname)

            # ✅ 리디렉션: 다운로드 페이지로 이동
            return redirect(url_for('download_page', filename=zip_filename))

        except Exception as e:
            print("변환 오류:", e)
            return f"변환 중 오류 발생: {str(e)}", 500

    return "Invalid file", 400

# ===== 다운로드 페이지 라우트 =====
@app.route('/download/<filename>')
def download_page(filename):
    return render_template('download.html', filename=filename)

# ===== 앱 실행 =====
if __name__ == '__main__':
    app.run(debug=True)
