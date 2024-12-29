from flask import Flask, render_template, request, redirect, url_for, session
import random
import uuid
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Globale Variablen für das Spiel
questions = [
    "Was ist deine Lieblingsaktivität?",
    "Wie fühlst du dich an einem Montagmorgen?",
    "Was denkst du über Katzen?",
    "Was würdest du auf eine einsame Insel mitnehmen?",
    "Beschreibe dein letztes Essen."
]
game_data = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setup', methods=['POST'])
def setup():
    players = request.form.get('players').split(', ')
    game_id = str(uuid.uuid4())
    random.shuffle(players)
    
    game_data[game_id] = {
        "players": players,
        "answers": {},
        "contexts": {},
        "votes": {},
        "scores": {player: 0 for player in players},
        "round": 1,
        "current_question": random.choice(questions)
    }
    
    session['game_id'] = game_id
    return redirect(url_for('question'))

@app.route('/question')
def question():
    game_id = session.get('game_id')
    game = game_data.get(game_id)
    
    if not game:
        return redirect(url_for('index'))
    
    return render_template('question.html', question=game["current_question"], players=game["players"])

@app.route('/results')
def results():
    game_id = session.get('game_id')
    game = game_data.get(game_id)
    
    if not game:
        return redirect(url_for('index'))
    
    winner = max(game["scores"], key=game["scores"].get)
    return render_template('results.html', scores=game["scores"], winner=winner)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
