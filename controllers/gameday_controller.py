from flask import Blueprint, jsonify, request
from services.mlb_service import MLBService

gameday_bp = Blueprint('gameday', __name__)
mlb_service = MLBService()

@gameday_bp.route('/<int:game_id>', methods=['GET'])
def get_gameday(game_id):
    data = mlb_service.get_gameday_data(game_id)
    return jsonify(data)

