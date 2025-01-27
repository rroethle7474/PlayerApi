import statsapi as MLBStatsAPI
from models.player_id_dto import PlayerIdDTO

class MLBService:
    def __init__(self):
        self.api = MLBStatsAPI

    def get_player_data(self, player_id):
        print (player_id)
        return self.api.player_stats(player_id)
    
    def get_player_id(self, player_name):
        return self.api.lookup_player(player_name, sportId=1)

    def get_gameday_data(self, game_id):
        return self.api.game_data(game_id)

    def get_team_data(self, team_id):
        return self.api.team_data(team_id)
