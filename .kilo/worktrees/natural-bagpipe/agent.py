import json


from llm import ask_llm

from tools.tmdb import search_movie

from database.db import (
    create_tables,
    create_user,
    get_user,
    save_message,
    get_history,
    save_preference,
    get_preferences
)


# --------------------------------------------------
# EXTRACT USER PREFERENCE
# --------------------------------------------------

def extract_preference(user_message):

    prompt = f"""
You are a user preference extraction system.

Analyze the user's message and identify whether
they have expressed a long-term preference.

Only extract a preference if the user clearly
expresses something they like, dislike, usually watch,
prefer, or want as a recurring preference.

Return ONLY valid JSON.
Do not add explanations.
Do not use markdown.
Do not use ```.

If there is a preference:

{{
    "has_preference": true,
    "key": "favorite_genre",
    "value": "science fiction"
}}

If there is no preference:

{{
    "has_preference": false,
    "key": null,
    "value": null
}}

Examples:

User: "I love sci-fi movies"

{{
    "has_preference": true,
    "key": "favorite_genre",
    "value": "science fiction"
}}

User: "I usually watch English movies"

{{
    "has_preference": true,
    "key": "language",
    "value": "English"
}}

User: "I don't like horror movies"

{{
    "has_preference": true,
    "key": "disliked_genre",
    "value": "horror"
}}

User: "I prefer movies released after 2015"

{{
    "has_preference": true,
    "key": "preferred_release_period",
    "value": "after 2015"
}}

User: "Recommend a movie for tonight"

{{
    "has_preference": false,
    "key": null,
    "value": null
}}

User: "Hi"

{{
    "has_preference": false,
    "key": null,
    "value": null
}}

User message:
{user_message}
"""

    result = ask_llm([
        {
            "role": "user",
            "content": prompt
        }
    ])

    try:
        return json.loads(result)

    except json.JSONDecodeError:

        return {
            "has_preference": False,
            "key": None,
            "value": None
        }


# --------------------------------------------------
# CHECK IF USER IS ASKING ABOUT MOVIES
# --------------------------------------------------

def is_movie_request(user_message):

    movie_keywords = [
        "movie",
        "movies",
        "film",
        "films",
        "recommend",
        "recommendation",
        "watch",
        "actor",
        "actress",
        "cinema"
    ]

    message = user_message.lower()

    return any(
        keyword in message
        for keyword in movie_keywords
    )


# --------------------------------------------------
# SEARCH MOVIES USING TMDB
# --------------------------------------------------

def search_movies_for_user(user_message, preferences):

    # Default search query
    search_query = user_message

    # If user has a favorite genre,
    # use that genre for the TMDB search.
    for key, value in preferences:

        if key == "favorite_genre":

            search_query = value

            break

    # Search TMDB
    movies = search_movie(search_query)

    return movies


# --------------------------------------------------
# MAIN AGENT
# --------------------------------------------------

def run_agent(user_id, user_message):

    # ----------------------------------------------
    # 1. Extract preference from current message
    # ----------------------------------------------

    preference = extract_preference(user_message)

    # ----------------------------------------------
    # 2. Save preference if detected
    # ----------------------------------------------

    if preference["has_preference"]:

        save_preference(
            user_id,
            preference["key"],
            preference["value"]
        )

    # ----------------------------------------------
    # 3. Get previous conversation history
    # ----------------------------------------------

    history = get_history(user_id)

    # ----------------------------------------------
    # 4. Get saved user preferences
    # ----------------------------------------------

    preferences = get_preferences(user_id)

    # ----------------------------------------------
    # 5. Create base AI messages
    # ----------------------------------------------

    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI Movie Recommendation Agent. "
                "You help users discover movies and have natural conversations. "
                "Use the user's preferences and conversation history "
                "only when they are relevant to the current request. "
                "For simple greetings or general conversation, respond naturally "
                "without forcing movie preferences into the conversation."
            )
        }
    ]

    # ----------------------------------------------
    # 6. Add user preferences to AI context
    # ----------------------------------------------

    if preferences:

        preference_text = "User preferences:\n"

        for key, value in preferences:

            preference_text += f"- {key}: {value}\n"

        messages.append(
            {
                "role": "system",
                "content": preference_text
            }
        )

    # ----------------------------------------------
    # 7. Add conversation history
    # ----------------------------------------------

    for role, content in history:

        messages.append(
            {
                "role": role,
                "content": content
            }
        )

    # ----------------------------------------------
    # 8. Check if this is a movie request
    # ----------------------------------------------

    movie_data = []

    if is_movie_request(user_message):

        movie_data = search_movies_for_user(
            user_message,
            preferences
        )

    # ----------------------------------------------
    # 9. Add TMDB data to AI context
    # ----------------------------------------------


    if movie_data and isinstance(movie_data, list):

        movie_text = "TMDB Movie Data:\n"

        for movie in movie_data:

            if not isinstance(movie, dict):
                continue

            movie_text += (
                f"\nTitle: {movie.get('title')}\n"
                f"Release Date: {movie.get('release_date')}\n"
                f"Rating: {movie.get('rating')}\n"
                f"Overview: {movie.get('overview')}\n"
            )

        messages.append({
            "role": "system",
            "content": movie_text
        })

    # ----------------------------------------------
    # 11. Ask OpenRouter
    # ----------------------------------------------

    answer = ask_llm(messages)

    # ----------------------------------------------
    # 12. Save user message
    # ----------------------------------------------

    save_message(
        user_id,
        "user",
        user_message
    )

    # ----------------------------------------------
    # 13. Save assistant response
    # ----------------------------------------------

    save_message(
        user_id,
        "assistant",
        answer
    )

    # ----------------------------------------------
    # 14. Return answer
    # ----------------------------------------------

    return answer