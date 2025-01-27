from flask import Flask, request, jsonify
from flask_cors import CORS
from controllers.player_controller import player_bp
from controllers.gameday_controller import gameday_bp
from controllers.team_controller import team_bp
from controllers.document_controller import document_bp
from services.pinecone_service import PineconeService
from service_container import ServiceContainer



def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Create and populate service container
    services = ServiceContainer()
    services.register('pinecone_service', PineconeService())
    
    # Attach service container to app
    app.services = services
    # Register blueprints
    app.register_blueprint(player_bp, url_prefix='/api/player')
    app.register_blueprint(gameday_bp, url_prefix='/api/gameday')
    app.register_blueprint(team_bp, url_prefix='/api/team')
    app.register_blueprint(document_bp, url_prefix='/api/document')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
