from database.db import create_tables, create_user, get_user
from agent import run_agent


# Make sure database tables exist
create_tables()


# For now, use a test user
telegram_id = "test_123"
name = "Abhishek"

# Create user if they don't exist
create_user(name, telegram_id)

# Get user from database
user = get_user(telegram_id)

user_id = user[0]


print("AI Movie Agent is ready!")
print("Type 'exit' to quit.\n")


while True:

    user_message = input("You: ")

    if user_message.lower() == "exit":
        break

    answer = run_agent(
        user_id,
        user_message
    )

    print("\nAgent:", answer)
    print()