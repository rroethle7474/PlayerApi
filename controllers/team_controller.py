from flask import Blueprint, jsonify, request
from services.mlb_service import MLBService

team_bp = Blueprint('team', __name__)
mlb_service = MLBService()

@team_bp.route('/<int:team_id>', methods=['GET'])
def get_team(team_id):
    data = mlb_service.get_team_data(team_id)
    return jsonify(data)
