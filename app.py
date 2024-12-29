from flask import Flask, render_template, request, redirect, url_for, session
import random, uuid
import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Render!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Standardport 5000
    app.run(host="0.0.0.0", port=port)


app = Flask(__name__)
app.secret_key = "supersecretkey"  # Für Sitzungen erforderlich

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
    # Initialisiere ein neues Spiel
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
    
    if not game or not game["players"]:
        return redirect(url_for('results'))
    
    return render_template('question.html', 
                           question=game["current_question"], 
                           players=game["players"])

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    game_id = session.get('game_id')
    game = game_data.get(game_id)
    
    player = request.form.get('player')
    answer = request.form.get('answer')
    game["answers"][player] = answer
    
    if len(game["answers"]) == len(game["players"]):
        return redirect(url_for('context'))
    return redirect(url_for('question'))

@app.route('/context')
def context():
    game_id = session.get('game_id')
    game = game_data.get(game_id)
    
    if not game or not game["players"]:
        return redirect(url_for('results'))
    
    return render_template('context.html', answers=game["answers"], players=game["players"])

@app.route('/submit_context', methods=['POST'])
def submit_context():
    game_id = session.get('game_id')
    game = game_data.get(game_id)
    
    player = request.form.get('player')
    context = request.form.get('context')
    game["contexts"][player] = context
    
    if len(game["contexts"]) == len(game["players"]):
        return redirect(url_for('vote'))
    return redirect(url_for('context'))

@app.route('/vote')
def vote():
    game_id = session.get('game_id')
    game = game_data.get(game_id)
    
    return render_template('vote.html', contexts=game["contexts"], players=game["players"])

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    game_id = session.get('game_id')
    game = game_data.get(game_id)
    
    voted_player = request.form.get('voted_player')
    game["votes"][voted_player] = game["votes"].get(voted_player, 0) + 1
    
    if len(game["votes"]) == len(game["players"]):
        for player, score in game["votes"].items():
            game["scores"][player] += score
        if game["round"] < 3:  # Spiele 3 Runden
            game["round"] += 1
            game["answers"].clear()
            game["contexts"].clear()
            game["votes"].clear()
            game["current_question"] = random.choice(questions)
            return redirect(url_for('question'))
        else:
            return redirect(url_for('results'))
    return redirect(url_for('vote'))

@app.route('/results')
def results():
    game_id = session.get('game_id')
    game = game_data.get(game_id)
    
    winner = max(game["scores"], key=game["scores"].get)
    return render_template('results.html', scores=game["scores"], winner=winner)

if __name__ == "__main__":
    app.run(debug=True)
