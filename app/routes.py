from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from app import app, db
from app.models import Coin, User, UserCoin

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(name=data['name'], email=data['email'], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 200

@app.route('/coin', methods=['POST'])
@jwt_required()
def add_coin():
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()
    if not user:  # 檢查用戶是否存在
        return jsonify({'message': 'User not found'}), 404

    # 可以在這裡添加更多授權檢查，例如檢查用戶角色

    data = request.get_json()
    new_coin = Coin(name=data['name'], symbol=data['symbol'])
    db.session.add(new_coin)
    db.session.commit()
    return jsonify({'message': 'New coin added'}), 201

@app.route('/user/coin', methods=['POST'])
@jwt_required()
def add_user_coin():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    coin = Coin.query.filter_by(id=data['coin_id']).first()
    if not coin:
        return jsonify({'message': 'Coin not found'}), 404
    
    new_user_coin = UserCoin(user_id=current_user_id, coin_id=data['coin_id'], amount=data['amount'])
    db.session.add(new_user_coin)
    db.session.commit()
    return jsonify({'message': 'Coin added to user'}), 201

@app.route('/user/coins', methods=['GET'])
@jwt_required()
def get_user_coins():
    current_user_id = get_jwt_identity()
    user_coins = UserCoin.query.filter_by(user_id=current_user_id).all()
    coins_data = []
    for user_coin in user_coins:
        coin = Coin.query.filter_by(id=user_coin.coin_id).first()
        coins_data.append({'name': coin.name, 'symbol': coin.symbol, 'amount': user_coin.amount})
    return jsonify({'coins': coins_data}), 200
