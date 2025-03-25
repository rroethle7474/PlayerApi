from flask import Blueprint, jsonify, request
from services.mlb_service import MLBService
from models.player_id_dto import PlayerIdDTO

player_bp = Blueprint('player', __name__)
mlb_service = MLBService()

@player_bp.route('/<int:player_id>', methods=['GET'])
def get_player_by_id(player_id):
    data = mlb_service.get_player_data(player_id)
    return jsonify(data)

@player_bp.route('/<string:player_name>', methods=['GET'])
def get_player_by_name(player_name):
    print(player_name)
    player_id = None
    data = {}
    player_id_results = mlb_service.get_player_id(player_name)
    print("player_id_results", player_id_results)
    if player_id_results and len(player_id_results) > 0:
        player_info = player_id_results[0]
        player_dto = PlayerIdDTO.from_dict(player_info)
        player_id = player_dto.player_id
        print("player_id", player_id)
    if player_id:
        data = mlb_service.get_player_data(player_id)
        print("data", data)
    return jsonify(data)

@player_bp.route('/', methods=['POST'])
def get_player():
    data = request.get_json()
    player_name = data.get('player_name')
    if not player_name:
        return jsonify({'error': 'Player name is required'}), 400
    
    player_data = mlb_service.get_player_data_by_name(player_name)
    if not player_data:
        return jsonify({'error': 'Player not found'}), 404

    return jsonify(player_data)

@player_bp.route('/player_stats', methods=['POST'])
def get_player_stats():
    data = request.json
    player_name = data.get('name')

    if not player_name:
        return jsonify({"error": "Player name is required"}), 400

    # Look up the player ID
    player_lookup = lookup_player(player_name)

    if not player_lookup:
        return jsonify({"error": "Player not found"}), 404

    player_id = player_lookup[0]['id']

    # Get the current season stats
    stats = player_stats(player_id, 'season')

    return jsonify(stats)