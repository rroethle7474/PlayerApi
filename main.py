from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import statsapi
from typing import Optional, List, Dict, Any
from urllib.parse import unquote  # Import unquote
import pprint # pretty print an object for debugging purposes
import io
from starlette.requests import Request

from PIL import Image
import pytesseract



origins = [
    "*",  # Allow all origins http://localhost:4200
]



# uvicorn main:app --reload
# http://127.0.0.1:8000/playerdata/?name=[Player Name]
# http://127.0.0.1:8000/upload

#pip install fastapi uvicorn pydantic
# pip install Flask MLB-StatsAPI
# I don't think Flask is needed here, but I'm not sure. I'm just following the instructions.

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


def get_hitting_at_bats(player_data: [], player_current_season_data: []) -> float:
    #print("HITTING")
    #pprint.pprint(player_data)
    at_bats = 0
    stats = player_data.get('stats',{})
    current_stats = player_current_season_data.get('stats',{})
    print("CAREER STATS",stats[0].get('stats',{}).get('atBats',0))
    print("2023",current_stats[0].get('stats',{}).get('atBats',0))
    
    if stats and current_stats:
      try:
        at_bats_stats = int(stats[0].get('stats',{}).get('atBats',0))
        at_bats_current_stats = int(current_stats[0].get('stats',{}).get('atBats',0))
        at_bats = at_bats_stats - at_bats_current_stats
      except ValueError:
      # Handle the error here
        at_bats = 0
    
    # if stats and current_stats:
    #     at_bats = stats[0].get('stats',{}).get('atBats',0) - current_stats[0].get('stats',{}).get('atBats',0)
    # print("AT BATS",at_bats)
    return float(at_bats)

def get_pitching_innings(player_data: [], player_current_season_data: []) -> float:
    #print("Pitching")
    #pprint.pprint(player_data)
    # Your code here
    innings_pitched = 0.00
    stats = player_data.get('stats',{})
    current_stats = player_current_season_data.get('stats',{})
    
    if stats and current_stats:
      try:
        innings_pitched_stats = float(stats[0].get('stats',{}).get('inningsPitched',0))
        innings_pitched_current_stats = float(current_stats[0].get('stats',{}).get('inningsPitched',0))
        innings_pitched = innings_pitched_stats - innings_pitched_current_stats
      except ValueError:
      # Handle the error here
        innings_pitched = 0.00
    
    
    # if stats and current_stats:
    #     innings_pitched = stats[0].get('stats',{}).get('inningsPitched',0) - current_stats[0].get('stats',{}).get('inningsPitched',0)
    # print("INNINGS PITCHED",innings_pitched)
    
    return float(innings_pitched)

class PlayerRequest(BaseModel):
    name: str
    position: str
    isValidToKeep: bool
    
@app.post("/upload")
async def upload_file(request: Request):
    form = await request.form()
    file = form["file"]

    contents = await file.read()  # Read the file contents
    try:
        image = Image.open(io.BytesIO(contents))
        text = pytesseract.image_to_string(image)
        print(text)
        return JSONResponse(content=text)
        #return {"text": text}
    except Exception as e:
        print("ERROR",e)
        return {"detail": f"An error occurred while processing the file: {str(e)}"}
    #print("CONTENTS", contents)
    # Process the file contents as needed
    # ...
    
# @app.route('/upload', methods=['POST'])
# async def upload_file(file: UploadFile = File(...)):
#     print ("FILE",file)
#     contents = await file.read()  # Read the file contents

    # contents = await file.read()
    # Process the file contents as needed
    #return JSONResponse(content={"text": "GOOD TEST"})
    # file = files[0]
    # contents = await file.read()
    
    # try:
    #     image = Image.open(io.BytesIO(contents))
    #     text = pytesseract.image_to_string(image)
    #     print(text)
    #     return {"text": text}
    # except Exception as e:
    #     return {"detail": f"An error occurred while processing the file: {str(e)}"}

@app.get("/playerdata/")
async def get_player_data(name: str, position: Optional[str] = None):
    try:
        isValidToKeep = False
        # Use MLB-StatsAPI to find the player and get career stats
        name = unquote(name) # looks like I don't need this as the value being passed in is already decoded
        if position:
          position = unquote(position)
        
        
        player_data = None if not name else statsapi.lookup_player(name, sportId=1, season=2023)
        
        primary_position = position or None if not player_data else player_data[0].get('primaryPosition', {}).get('abbreviation', None) if player_data else None
        
        
        if primary_position:
            primary_position = primary_position.lower()
        
        player_id = None if not player_data else player_data[0].get('id',None)
        
        valid_pitcher_positions = ['pitcher','p','sp','rp','cl']
    
        if player_data and player_id and primary_position:
            if primary_position in valid_pitcher_positions:
                player_career_data = statsapi.player_stat_data(player_id, group="[pitching]", type="career")
                player_current_season_data = statsapi.player_stat_data(player_id, group="[pitching]", type="season")
                innings = get_pitching_innings(player_career_data, player_current_season_data)
                if innings >= 50:
                  isValidToKeep = True
            else:
                player_career_data = statsapi.player_stat_data(player_id, group="[hitting]", type="career")
                player_current_season_data = statsapi.player_stat_data(player_id, group="[hitting]", type="season")
                pprint.pprint(player_current_season_data)
                at_bats = get_hitting_at_bats(player_career_data, player_current_season_data)
                if at_bats >= 130:
                  isValidToKeep = True
            # need to do the same thing but use season stats for 2023 and then subtrat to validate
            return {"player_data": player_career_data, "player_current_season": player_current_season_data, "is_valid_to_keep": isValidToKeep}
        else:
            print("NO WAY!!!!!")
            isValidToKeep = False
            player_data = []
        
        if(not isValidToKeep):
            print("NOT VALID TO KEEP",name)
        return {"player_data": player_data, "is_valid_to_keep": isValidToKeep}
    
    except Exception as e:
        isValidToKeep = False
        print("ERROR",e)
        raise HTTPException(status_code=404, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
