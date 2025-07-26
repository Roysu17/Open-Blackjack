from flask import Flask, request, jsonify, send_from_directory, send_file
import random
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Game state storage (in production, use a proper session store)
game_sessions = {}

def create_deck():
    """Create a deck of cards."""
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    return [{'value': v, 'suit': s} for s in suits for v in values]

def shuffle_deck(deck):
    """Shuffle the deck of cards."""
    random.shuffle(deck)
    return deck

def deal_card(deck):
    """Deal one card from the deck."""
    return deck.pop()

def calculate_hand(hand):
    """Calculate the total value of a hand."""
    total = 0
    aces = 0
    for card in hand:
        if card['value'] in ['Jack', 'Queen', 'King']:
            total += 10
        elif card['value'] == 'Ace':
            aces += 1
            total += 11
        else:
            total += int(card['value'])
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def create_game_state():
    """Create initial game state."""
    return {
        'deck': shuffle_deck(create_deck()),
        'playerHand': [],
        'dealerHand': [],
        'playerTotal': 0,
        'dealerTotal': 0,
        'balance': 0,
        'bet': 0,
        'gamePhase': 'betting',
        'canDoubleDown': False,
        'message': '',
        'winner': None
    }

def get_session_id():
    """Get session ID from request (simplified for demo)."""
    return request.remote_addr  # In production, use proper session management

@app.route('/api/start', methods=['POST'])
def start_game():
    session_id = get_session_id()
    data = request.get_json()
    balance = data.get('balance', 100)
    
    game_state = create_game_state()
    game_state['balance'] = balance
    game_state['message'] = f'Game started with ${balance}. Place your bet!'
    
    game_sessions[session_id] = game_state
    
    return jsonify({
        'success': True,
        'gameState': {
            'playerHand': game_state['playerHand'],
            'dealerHand': game_state['dealerHand'],
            'playerTotal': game_state['playerTotal'],
            'dealerTotal': game_state['dealerTotal'],
            'balance': game_state['balance'],
            'bet': game_state['bet'],
            'gamePhase': game_state['gamePhase'],
            'canDoubleDown': game_state['canDoubleDown'],
            'message': game_state['message'],
            'winner': game_state.get('winner')
        }
    })

@app.route('/api/bet', methods=['POST'])
def place_bet():
    session_id = get_session_id()
    if session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'Game not started'})
    
    game_state = game_sessions[session_id]
    data = request.get_json()
    bet = data.get('bet', 0)
    
    if bet <= 0 or bet > game_state['balance']:
        return jsonify({'success': False, 'message': 'Invalid bet amount'})
    
    # Start new hand
    game_state['deck'] = shuffle_deck(create_deck())
    game_state['bet'] = bet
    game_state['playerHand'] = [deal_card(game_state['deck']), deal_card(game_state['deck'])]
    game_state['dealerHand'] = [deal_card(game_state['deck']), deal_card(game_state['deck'])]
    game_state['playerTotal'] = calculate_hand(game_state['playerHand'])
    game_state['dealerTotal'] = calculate_hand(game_state['dealerHand'])
    game_state['gamePhase'] = 'playing'
    game_state['canDoubleDown'] = True
    game_state['winner'] = None
    
    # Check for blackjack
    if game_state['playerTotal'] == 21:
        if game_state['dealerTotal'] == 21:
            game_state['message'] = 'Both have Blackjack! Push.'
            game_state['gamePhase'] = 'finished'
        else:
            game_state['message'] = 'Blackjack! You win!'
            game_state['balance'] += int(bet * 1.5)  # Blackjack pays 3:2
            game_state['gamePhase'] = 'finished'
            game_state['winner'] = 'player'
    else:
        game_state['message'] = 'Choose your action: Hit, Stand, or Double Down'
    
    return jsonify({
        'success': True,
        'gameState': {
            'playerHand': game_state['playerHand'],
            'dealerHand': game_state['dealerHand'],
            'playerTotal': game_state['playerTotal'],
            'dealerTotal': game_state['dealerTotal'],
            'balance': game_state['balance'],
            'bet': game_state['bet'],
            'gamePhase': game_state['gamePhase'],
            'canDoubleDown': game_state['canDoubleDown'],
            'message': game_state['message'],
            'winner': game_state.get('winner')
        }
    })

@app.route('/api/hit', methods=['POST'])
def hit():
    session_id = get_session_id()
    if session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'Game not started'})
    
    game_state = game_sessions[session_id]
    
    if game_state['gamePhase'] != 'playing':
        return jsonify({'success': False, 'message': 'Cannot hit in current game phase'})
    
    # Deal card to player
    new_card = deal_card(game_state['deck'])
    game_state['playerHand'].append(new_card)
    game_state['playerTotal'] = calculate_hand(game_state['playerHand'])
    game_state['canDoubleDown'] = False
    
    if game_state['playerTotal'] > 21:
        game_state['message'] = 'Bust! You lose.'
        game_state['balance'] -= game_state['bet']
        game_state['gamePhase'] = 'finished'
        game_state['winner'] = 'dealer'
    else:
        game_state['message'] = f'You drew {new_card["value"]} of {new_card["suit"]}. Choose your action.'
    
    return jsonify({
        'success': True,
        'gameState': {
            'playerHand': game_state['playerHand'],
            'dealerHand': game_state['dealerHand'],
            'playerTotal': game_state['playerTotal'],
            'dealerTotal': game_state['dealerTotal'],
            'balance': game_state['balance'],
            'bet': game_state['bet'],
            'gamePhase': game_state['gamePhase'],
            'canDoubleDown': game_state['canDoubleDown'],
            'message': game_state['message'],
            'winner': game_state.get('winner')
        }
    })

@app.route('/api/stand', methods=['POST'])
def stand():
    session_id = get_session_id()
    if session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'Game not started'})
    
    game_state = game_sessions[session_id]
    
    if game_state['gamePhase'] != 'playing':
        return jsonify({'success': False, 'message': 'Cannot stand in current game phase'})
    
    # Dealer's turn
    game_state['gamePhase'] = 'dealer'
    while game_state['dealerTotal'] < 17:
        new_card = deal_card(game_state['deck'])
        game_state['dealerHand'].append(new_card)
        game_state['dealerTotal'] = calculate_hand(game_state['dealerHand'])
    
    # Determine winner
    if game_state['dealerTotal'] > 21:
        game_state['message'] = 'Dealer busts! You win!'
        game_state['balance'] += game_state['bet']
        game_state['winner'] = 'player'
    elif game_state['dealerTotal'] > game_state['playerTotal']:
        game_state['message'] = 'Dealer wins.'
        game_state['balance'] -= game_state['bet']
        game_state['winner'] = 'dealer'
    elif game_state['playerTotal'] > game_state['dealerTotal']:
        game_state['message'] = 'You win!'
        game_state['balance'] += game_state['bet']
        game_state['winner'] = 'player'
    else:
        game_state['message'] = 'Push (tie).'
        game_state['winner'] = 'push'
    
    game_state['gamePhase'] = 'finished'
    
    return jsonify({
        'success': True,
        'gameState': {
            'playerHand': game_state['playerHand'],
            'dealerHand': game_state['dealerHand'],
            'playerTotal': game_state['playerTotal'],
            'dealerTotal': game_state['dealerTotal'],
            'balance': game_state['balance'],
            'bet': game_state['bet'],
            'gamePhase': game_state['gamePhase'],
            'canDoubleDown': game_state['canDoubleDown'],
            'message': game_state['message'],
            'winner': game_state.get('winner')
        }
    })

@app.route('/api/double', methods=['POST'])
def double_down():
    session_id = get_session_id()
    if session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'Game not started'})
    
    game_state = game_sessions[session_id]
    
    if game_state['gamePhase'] != 'playing' or not game_state['canDoubleDown']:
        return jsonify({'success': False, 'message': 'Cannot double down'})
    
    if game_state['balance'] < game_state['bet']:
        return jsonify({'success': False, 'message': 'Insufficient balance to double down'})
    
    # Double the bet and deal one card
    game_state['bet'] *= 2
    new_card = deal_card(game_state['deck'])
    game_state['playerHand'].append(new_card)
    game_state['playerTotal'] = calculate_hand(game_state['playerHand'])
    
    if game_state['playerTotal'] > 21:
        game_state['message'] = 'Bust! You lose.'
        game_state['balance'] -= game_state['bet']
        game_state['gamePhase'] = 'finished'
        game_state['winner'] = 'dealer'
    else:
        # Dealer's turn (automatic stand after double down)
        game_state['gamePhase'] = 'dealer'
        while game_state['dealerTotal'] < 17:
            dealer_card = deal_card(game_state['deck'])
            game_state['dealerHand'].append(dealer_card)
            game_state['dealerTotal'] = calculate_hand(game_state['dealerHand'])
        
        # Determine winner
        if game_state['dealerTotal'] > 21:
            game_state['message'] = 'Dealer busts! You win!'
            game_state['balance'] += game_state['bet']
            game_state['winner'] = 'player'
        elif game_state['dealerTotal'] > game_state['playerTotal']:
            game_state['message'] = 'Dealer wins.'
            game_state['balance'] -= game_state['bet']
            game_state['winner'] = 'dealer'
        elif game_state['playerTotal'] > game_state['dealerTotal']:
            game_state['message'] = 'You win!'
            game_state['balance'] += game_state['bet']
            game_state['winner'] = 'player'
        else:
            game_state['message'] = 'Push (tie).'
            game_state['winner'] = 'push'
        
        game_state['gamePhase'] = 'finished'
    
    return jsonify({
        'success': True,
        'gameState': {
            'playerHand': game_state['playerHand'],
            'dealerHand': game_state['dealerHand'],
            'playerTotal': game_state['playerTotal'],
            'dealerTotal': game_state['dealerTotal'],
            'balance': game_state['balance'],
            'bet': game_state['bet'],
            'gamePhase': game_state['gamePhase'],
            'canDoubleDown': False,
            'message': game_state['message'],
            'winner': game_state.get('winner')
        }
    })

@app.route('/api/state', methods=['GET'])
def get_state():
    session_id = get_session_id()
    if session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'Game not started'})
    
    game_state = game_sessions[session_id]
    return jsonify({
        'success': True,
        'gameState': {
            'playerHand': game_state['playerHand'],
            'dealerHand': game_state['dealerHand'],
            'playerTotal': game_state['playerTotal'],
            'dealerTotal': game_state['dealerTotal'],
            'balance': game_state['balance'],
            'bet': game_state['bet'],
            'gamePhase': game_state['gamePhase'],
            'canDoubleDown': game_state['canDoubleDown'],
            'message': game_state['message'],
            'winner': game_state.get('winner')
        }
    })

# Serve React app
@app.route('/')
def serve_react_app():
    return send_from_directory('client/dist', 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    if os.path.exists(f'client/dist/{path}'):
        return send_from_directory('client/dist', path)
    return send_from_directory('client/dist', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)