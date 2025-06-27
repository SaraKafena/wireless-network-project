import os
import sys
import math
import json
import openai

from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('GOOGLE_API_KEY')
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.calculations import calculations_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes - مهم للاتصال بين الواجهتين
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(calculations_bp, url_prefix='/api')

# Database configuration - قاعدة البيانات (اختيارية)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """خدمة الملفات الثابتة"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/health')
def health_check():
    """فحص صحة الخادم"""
    return jsonify({
        'status': 'healthy',
        'message': 'Wireless Network Calculator API is running!',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🚀 بدء تشغيل خادم الشبكة اللاسلكية...")
    print("📡 الواجهة الخلفية جاهزة على: http://localhost:5000")
    print("🔗 API متاح على: http://localhost:5000/api/")
    print("❤️ فحص الصحة: http://localhost:5000/health")
    print("⚠️ لإيقاف الخادم: اضغط Ctrl+C")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

