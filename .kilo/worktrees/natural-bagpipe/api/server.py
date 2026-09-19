from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent import run_agent
from database.db import create_tables, create_user, get_user


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create database tables
create_tables()


@app.get("/")
def home():
    return {
        "message": "AI Movie Agent API is running"
    }


@app.post("/chat")
def chat(data: dict):

    # Get data from frontend
    user_id_from_frontend = data.get("user_id")
    user_message = data.get("message", "")

    # Temporary user ID for frontend testing
    telegram_id = user_id_from_frontend
    name = "Web User"

    # Create user if not already exists
    create_user(name, telegram_id)

    # Get user from database
    user = get_user(telegram_id)

    # Check if user exists
    if not user:
        return {
            "response": "User not found"
        }

    # Database user ID
    user_id = user[0]

    # Run AI agent
    response = run_agent(user_id, user_message)

    return {
        "response": response
    }