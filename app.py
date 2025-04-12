# app.py

import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from datetime import datetime
from zipfile import ZipFile

# ===== 설정 =====
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'static/output'
ALLOWED_EXTENSIONS = {'pdf'}

# poppler 경로 (macOS/Linux는 None, Windows는 경로 지정 필요)
POPPLER_PATH = None

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

# ===== PDF → 이미지 변환 & ZIP 압축 =====
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
            # 고유한 파일 이름 기반 설정
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            base_name = f"converted_{timestamp}"

            # PDF → 이미지 변환 (모든 페이지)
            images = convert_from_path(filepath, dpi=200, poppler_path=POPPLER_PATH)

            # JPG 이미지 저장
            image_filenames = []
            for i, image in enumerate(images):
                image_filename = f"{base_name}_page_{i+1}.jpg"
                image_path = os.path.join(app.config['OUTPUT_FOLDER'], image_filename)
                image.save(image_path, 'JPEG')
                image_filenames.append(image_path)

            # 이미지들을 ZIP 파일로 묶기
            zip_filename = f"{base_name}.zip"
            zip_path = os.path.join(app.config['OUTPUT_FOLDER'], zip_filename)
            with ZipFile(zip_path, 'w') as zipf:
                for img_path in image_filenames:
                    arcname = os.path.basename(img_path)
                    zipf.write(img_path, arcname=arcname)

            # 클라이언트에 다운로드 링크 전달
            return jsonify({
                'success': True,
                'download_url': f"/static/output/{zip_filename}"
            })

        except Exception as e:
            print("변환 오류:", e)
            return jsonify({'success': False, 'error': str(e)})

    return jsonify({'success': False, 'error': 'Invalid file'})

# ===== 다운로드 페이지 라우트 =====
@app.route('/download/<filename>')
def download_page(filename):
    return render_template('download.html', filename=filename)

# ===== 앱 실행 =====
if __name__ == '__main__':
    app.run(debug=True)
