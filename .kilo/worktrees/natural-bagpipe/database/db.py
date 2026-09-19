import sqlite3


DB_NAME = "movie_agent.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            telegram_id TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # User preferences table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            preference_key TEXT NOT NULL,
            preference_value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, preference_key)
        )
    """)

    connection.commit()
    connection.close()


def create_user(name, telegram_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users (name, telegram_id)
        VALUES (?, ?)
    """, (name, telegram_id))

    connection.commit()
    connection.close()


def get_user(telegram_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, telegram_id
        FROM users
        WHERE telegram_id = ?
    """, (telegram_id,))

    user = cursor.fetchone()

    connection.close()

    return user


def save_message(user_id, role, content):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO messages (user_id, role, content)
        VALUES (?, ?, ?)
    """, (user_id, role, content))

    connection.commit()
    connection.close()


def get_history(user_id, limit=10):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT role, content
        FROM messages
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (user_id, limit))

    messages = cursor.fetchall()

    connection.close()

    # Reverse so oldest message comes first
    messages.reverse()

    return messages


def save_preference(user_id, key, value):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO user_preferences
        (user_id, preference_key, preference_value)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, preference_key)
        DO UPDATE SET preference_value = excluded.preference_value
    """, (user_id, key, value))

    connection.commit()
    connection.close()


def get_preferences(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT preference_key, preference_value
        FROM user_preferences
        WHERE user_id = ?
    """, (user_id,))

    preferences = cursor.fetchall()

    connection.close()

    return preferences


# --------------------------------------------------
# TEST CODE
# --------------------------------------------------

if __name__ == "__main__":

    create_tables()

    create_user(
        "Abhishek",
        "test_123"
    )

    user = get_user("test_123")

    print("User:", user)

    user_id = user[0]

    # Test messages
    save_message(
        user_id,
        "user",
        "I like science fiction movies."
    )

    save_message(
        user_id,
        "assistant",
        "Great! I can recommend science fiction movies."
    )

    print("\nConversation History:")

    history = get_history(user_id)

    for role, content in history:
        print(f"{role}: {content}")

    # Test preferences
    save_preference(
        user_id,
        "favorite_genre",
        "science fiction"
    )

    save_preference(
        user_id,
        "language",
        "English"
    )

    print("\nUser Preferences:")

    preferences = get_preferences(user_id)

    for key, value in preferences:
        print(f"{key}: {value}")