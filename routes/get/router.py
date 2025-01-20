from fastapi import APIRouter, Request, HTTPException, status
from bson.objectid import ObjectId

getrouter = APIRouter()

@getrouter.get("/games", response_description="List all games")
async def list_games(request: Request):
    """ List 10 games """
    pipeline = [
        {"$limit": 10},
        {"$project": {"_id": {"$toString": "$_id"}, "Title": 1, "Release Date": 1, "Developer": 1, "Publisher": 1, "Genres": 1, "Genres Splitted": 1, "User Score": 1, "User Ratings Count": 1, "Platforms Info": 1}}
    ]
    return list(request.app.database.games.aggregate(pipeline))


@getrouter.get("/games/{game_id}", response_description="Get a single game")
def show_game(game_id: str, request: Request):
    """ Get a single game """
    game_id = game_id.strip()
    game = request.app.database.games.find_one({"_id": ObjectId(game_id)})
    if game:
        game['_id'] = str(game['_id'])
        return game
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No game with that id")