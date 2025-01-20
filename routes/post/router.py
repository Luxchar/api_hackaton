from fastapi import APIRouter, Request, HTTPException, status
from bson.objectid import ObjectId
from typing import List

postrouter = APIRouter()

@postrouter.post("/games", response_description="ajoute jeu", status_code=status.HTTP_201_CREATED)
async def add_game(request: Request, game_data: dict):
    """ Add a game to the database """
    inserted_game = request.app.database.games.insert_one(game_data)
    
    if inserted_game.inserted_id:
        return {
            "message": "Game added successfully",
            "inserted_game_id": str(inserted_game.inserted_id)
        }
    
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to add game")

@postrouter.post("/games/multiple", response_description="Add multiple games", status_code=status.HTTP_201_CREATED)
async def add_x_games(request: Request, games_data: List[dict]):  
    """ Add multiple games """
   
    inserted_games_ids = []
    
    
    inserted_result = request.app.database.games.insert_many(games_data)
    
    
    if inserted_result.inserted_ids:
        inserted_games_ids.extend([str(game_id) for game_id in inserted_result.inserted_ids])
    else:
        
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to insert games")
    
    
    return {
        "message": "Games added successfully",
        "inserted_games_ids": inserted_games_ids
    }