from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
import os
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Temporary user store (for demo, use DB in production)
users = {}

# YouTube API key
YOUTUBE_API_KEY = "AIzaSyCNM1WXPbQLxla15bXAIbkeAgM7O-c0_6M"

# Spotify playlists
spotify_playlists = {
    "Happy": [
        "https://open.spotify.com/embed/playlist/37i9dQZF1DXdPec7aLTmlC",
        "https://open.spotify.com/embed/playlist/37i9dQZF1DWYBO1MoTDhZI"
    ],
    "Sad": [
        "https://open.spotify.com/embed/playlist/37i9dQZF1DWVV27DiNWxkR",
        "https://open.spotify.com/embed/playlist/37i9dQZF1DX3YSRoSdA634"
    ],
    "Romantic": [
        "https://open.spotify.com/embed/playlist/37i9dQZF1DX50QitC6Oqtn",
        "https://open.spotify.com/embed/playlist/37i9dQZF1DX3PIPIT6lEg5"
    ],
    "Energetic": [
        "https://open.spotify.com/embed/playlist/37i9dQZF1DX1g0iEXLFycr"
    ],
    "Chill": [
        "https://open.spotify.com/embed/playlist/37i9dQZF1DWVCHIm2MEeIy"
    ],
    "Angry": [
        "https://open.spotify.com/embed/playlist/37i9dQZF1DWSqBruwoIXkA"
    ],
    "Focus": [
        "https://open.spotify.com/embed/playlist/37i9dQZF1DX4sWSpwq3LiO"
    ],
    "Sleep": [
        "https://open.spotify.com/embed/playlist/37i9dQZF1DWSSBwgXMlrMk"
    ]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return render_template('signup.html', error='User already exists!')
        users[username] = password
        session['user'] = username
        return redirect(url_for('home'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.get(username) == password:
            session['user'] = username
            return redirect(url_for('chat'))  # ✅ Fixed here
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/home')
def home():
    if 'user' not in session:
        return render_template('chat.html', alert=True)
    return render_template('home.html', user=session['user'])

# ✅ Add this route for chatbox page
@app.route('/chat')
def chat():
    if 'user' not in session:
        return redirect(url_for('home'))
    return render_template('chat.html', user=session['user'])
@app.route("/get_songs", methods=["POST"])
def get_songs():
    data = request.get_json()
    mood = data.get("mood")
    platform = data.get("platform")

    if not mood or not platform:
        return jsonify({"error": "Mood or platform missing"}), 400

    mood = mood.capitalize()
    songs = []

    if platform == "YouTube":
        query = f"{mood} songs playlist"
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=6&q={query}&key={YOUTUBE_API_KEY}&type=video"
        res = requests.get(url)
        for item in res.json().get("items", []):
            video_id = item["id"].get("videoId")
            title = item["snippet"].get("title")
            if video_id:
                songs.append({"name": title, "video_id": video_id})
        return jsonify({"platform": "YouTube", "songs": songs})

    elif platform == "Spotify":
        playlist_list = spotify_playlists.get(mood, [])
        if playlist_list:
            return jsonify({
                "platform": "Spotify",
                "playlist": random.choice(playlist_list)
            })

    elif platform == "JioSaavn":
        return jsonify({
            "platform": "JioSaavn",
            "songs": [
                {"name": f"{mood} Hits – JioSaavn", "link": f"https://www.jiosaavn.com/search/{mood}"}
            ]
        })

    return jsonify({"error": "No songs found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
