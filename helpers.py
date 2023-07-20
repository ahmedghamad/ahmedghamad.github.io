import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def get_books(genre):
    """Look up books."""

# Contact API

    api_key = os.environ.get("API_KEY")
    url = 'https://www.googleapis.com/books/v1/volumes'
    params = {
        'q': genre,
        'subject': genre,
        'key': api_key
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        results = []
        if "items" in data:
            books = data["items"]
            for book in books:
                book1 = {}
                volume_info = book["volumeInfo"]
                book1['title'] = volume_info.get("title", "N/A")
                authors = volume_info.get("authors", [])
                book1['author'] = authors[0] if authors else "N/A"
                book1['publisher'] = volume_info.get("publisher", "N/A")
                book1['description'] = volume_info.get("description", "N/A")

                results.append(book1)

            return results
        else:
            print(response.content)
            print('Error:', response.status_code)
            return None

