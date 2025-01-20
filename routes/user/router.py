from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel
from bson import ObjectId
import bcrypt
import uuid

userrouter = APIRouter()

def hash_password(password: str):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


@userrouter.post("/register", response_description="Add new user", status_code=status.HTTP_201_CREATED)
async def create_user(request: Request):
    """ Add new user """
    user = await request.json()
    if user.get("username") and user.get("password"):
        # Check if the user already exists
        db_user = request.app.database.users.find_one({"username": user["username"]})
        if db_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered")
        
        # Generate token to connect
        user["token"] = str(uuid.uuid4())
        
        # You should hash the password before storing it in the database
        hashed_password = hash_password(user["password"])
        
        db_user = {"username": user["username"], "password": hashed_password, "token": user["token"], "likes": []}
        result = request.app.database.users.insert_one(db_user)
        
        # Convert ObjectId to string
        user_id = str(result.inserted_id)
        return {**db_user, "_id": user_id}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user data")

@userrouter.post("/login", response_description="Login user")
async def login_user(request: Request):
    """ Login user """
    user = await request.json()
    if user.get("username") and user.get("password"):
        db_user = request.app.database.users.find_one({"username": user["username"]})
        if db_user:
            if verify_password(user["password"], db_user["password"]):
                return {"message": "Login successful", "token": db_user["token"]}
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user data")