from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from functools import wraps
import os
from dotenv import load_dotenv
from predict import load_lotto_data, predict_lotto_numbers

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)

# CORS 설정
CORS(app, 
     origins=['https://llt-aws.vercel.app'],
     methods=['GET'],
     allow_headers=['X-API-Key', 'Content-Type'],
     max_age=3600
)

# API 키 설정
API_KEY = os.getenv('API_KEY')

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key and api_key == API_KEY:
            return f(*args, **kwargs)
        return jsonify({'error': 'Invalid API key'}), 401
    return decorated_function

# 회차 계산 함수
def get_lotto_round():
    start_lotto_round = 1143
    start_date = datetime(2024, 10, 20)
    today = datetime.today()
    delta_days = (today - start_date).days
    delta_weeks = delta_days // 7
    current_round = start_lotto_round + delta_weeks
    return current_round

# 로또 번호 예측 API
@app.route('/generate-lotto')
@require_api_key
def generate_lotto():
    try:
        lotto_numbers = load_lotto_data(os.path.join(os.path.dirname(__file__), 'lotto_numbers.txt'))
        predictions = predict_lotto_numbers(lotto_numbers)
        current_round = get_lotto_round()
        return jsonify(numbers=predictions, round=current_round)
    except Exception as e:
        return jsonify({'error': 'Prediction failed', 'message': str(e)}), 500

# Health Check API 추가
@app.route('/health')
def health_check():
    try:
        # 기본적인 서버 상태 확인
        status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'lotto-prediction-api'
        }
        
        # 모델 파일 존재 여부 확인
        model_path = os.path.join(os.path.dirname(__file__), 'lotto_model.h5')
        data_path = os.path.join(os.path.dirname(__file__), 'lotto_numbers.txt')
        
        status['checks'] = {
            'model_file': os.path.exists(model_path),
            'data_file': os.path.exists(data_path)
        }
        
        return jsonify(status), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# 에러 핸들링
@app.errorhandler(Exception)
def handle_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': str(error)
    }), 500

# 포트 설정
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
