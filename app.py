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
        # lotto_numbers.txt에서 마지막 회차 읽기
        with open(os.path.join(os.path.dirname(__file__), 'lotto_numbers.txt'), 'r') as f:
            lines = f.readlines()
            if not lines:
                raise ValueError("로또 데이터 파일이 비어있습니다.")
            last_round = int(lines[-1].split(',')[0])  # 마지막 줄의 회차 번호
            
        # 현재 날짜로부터 이번 주 토요일 계산
        today = datetime.today()
        days_until_saturday = (5 - today.weekday()) % 7
        this_saturday = today + timedelta(days=days_until_saturday)
        
        # 이번 주 토요일이 지났다면 다음 주 토요일의 회차
        if today.weekday() == 5 and today.hour >= 21:  # 토요일 21시 이후
            return last_round + 1
        elif days_until_saturday == 0 and today.hour >= 21:  # 토요일 21시 이후
            return last_round + 1
        else:
            return last_round
            
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
