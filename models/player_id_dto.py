class PlayerIdDTO:
    def __init__(self, player_id, full_name, first_name, last_name, primary_number, current_team_id, primary_position_code, mlb_debut_date):
        self.player_id = player_id
        self.full_name = full_name
        self.first_name = first_name
        self.last_name = last_name
        self.primary_number = primary_number
        self.current_team_id = current_team_id
        self.primary_position_code = primary_position_code
        self.mlb_debut_date = mlb_debut_date

    @classmethod
    def from_dict(cls, data):
        return cls(
            player_id=data.get('id'),
            full_name=data.get('fullName'),
            first_name=data.get('firstName'),
            last_name=data.get('lastName'),
            primary_number=data.get('primaryNumber'),
            current_team_id=data.get('currentTeam', {}).get('id'),
            primary_position_code=data.get('primaryPosition', {}).get('code'),
            mlb_debut_date=data.get('mlbDebutDate')
        )
