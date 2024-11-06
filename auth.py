from flask import Blueprint, jsonify, request, session
from flask_bcrypt import Bcrypt
from app import db, User  # app의 User 모델과 db 사용

bcrypt = Bcrypt()
auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data['password'] == data['confirm_password']:
        return jsonify({'error': 'Passwords do not match'}), 400
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    new_user = User(username=data['username'], password=hashed_password,
                    name=data['name'], age=data['age'], gender=data['gender'])
    
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()

    if user and bcrypt.check_password_hash(user.password, data['password']):
        session['user_id'] = user.id
        return jsonify({'message': 'Logged in successfully'}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@auth.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200
