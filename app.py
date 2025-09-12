from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pytesseract
from PIL import Image
import io
import docx
import os
import uuid

# 关键：修改为你的Tesseract安装路径！
pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract\tesseract-uninstall.exe'

app = Flask(__name__)
CORS(app)  # 允许跨域访问

# 创建临时文件夹
UPLOAD_FOLDER = 'temp_files'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/api/process-image', methods=['POST'])
def process_image():
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': '未上传图片'})
        
        file = request.files['image']
        image = Image.open(file.stream)
        
        # 识别文字（支持中文+英文）
        text = pytesseract.image_to_string(image, lang='chi_sim+eng', config='--temp_dir D:\\temp')

        if not text.strip():
            return jsonify({'success': False, 'error': '未识别到文字'})
        
        # 生成Word文档
        doc = docx.Document()
        doc.add_paragraph(text)
        filename = f"{uuid.uuid4()}.docx"
        doc.save(f"{UPLOAD_FOLDER}/{filename}")
        
        return jsonify({
            'success': True,
            'text': text,
            'file_url': f'/api/download/{filename}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/download/<filename>')
def download(filename):
    return send_file(f"{UPLOAD_FOLDER}/{filename}", as_attachment=True, download_name='识别结果.docx')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)