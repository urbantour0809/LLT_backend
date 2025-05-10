from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from predict import load_lotto_data, predict_lotto_numbers

app = Flask(__name__)

# CORS 설정
CORS(app, 
     origins=['https://llt-aws.vercel.app'],
     methods=['GET'],
     allow_headers=['Content-Type'],
     max_age=3600
)

# 회차 계산 함수
def get_lotto_round():
    try:
        # 현재 날짜로부터 이번 주 토요일 계산
        today = datetime.today()
        days_until_saturday = (5 - today.weekday()) % 7
        this_saturday = today + timedelta(days=days_until_saturday)
        
        # 기준 날짜 (2025-05-03, 1170회)
        base_date = datetime(2025, 5, 3)
        base_round = 1170
        
        # 현재 날짜와 기준 날짜의 차이를 주 단위로 계산
        weeks_diff = (this_saturday - base_date).days // 7
        
        # 현재 회차 계산
        current_round = base_round + weeks_diff
        
        return current_round
            
    except Exception as e:
        raise Exception(f"회차 계산 중 오류 발생: {str(e)}")

# 로또 번호 예측 API
@app.route('/generate-lotto')
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
