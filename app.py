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

def create_player(player_id, name, balance):
    """Create a new player."""
    return {
        'id': player_id,
        'name': name,
        'hand': [],
        'total': 0,
        'balance': balance,
        'bet': 0,
        'canDoubleDown': False,
        'isActive': False,
        'isFinished': False,
        'winner': None
    }

def create_game_state():
    """Create initial multiplayer game state."""
    return {
        'deck': shuffle_deck(create_deck()),
        'players': [],
        'dealerHand': [],
        'dealerTotal': 0,
        'gamePhase': 'setup',
        'currentPlayerIndex': 0,
        'message': '',
        'allPlayersFinished': False
    }

def get_session_id():
    """Get session ID from request (simplified for demo)."""
    return request.remote_addr  # In production, use proper session management

def format_game_state(game_state):
    """Format game state for frontend."""
    return {
        'players': game_state['players'],
        'dealerHand': game_state['dealerHand'],
        'dealerTotal': game_state['dealerTotal'],
        'gamePhase': game_state['gamePhase'],
        'currentPlayerIndex': game_state['currentPlayerIndex'],
        'message': game_state['message'],
        'allPlayersFinished': game_state['allPlayersFinished']
    }

def check_all_players_finished(game_state):
    """Check if all players have finished their turns."""
    return all(player['isFinished'] for player in game_state['players'])

def dealer_play(game_state):
    """Play dealer's turn."""
    while game_state['dealerTotal'] < 17:
        new_card = deal_card(game_state['deck'])
        game_state['dealerHand'].append(new_card)
        game_state['dealerTotal'] = calculate_hand(game_state['dealerHand'])

def can_double_down(player):
    """Check if player can double down."""
    return (len(player['hand']) == 2 and  # Only on first two cards
            player['balance'] >= player['bet'] * 2 and  # Must have enough balance for doubled bet
            not player['isFinished'])  # Player hasn't finished their turn

def determine_winners(game_state):
    """Determine winners for all players."""
    dealer_total = game_state['dealerTotal']
    dealer_busted = dealer_total > 21
    
    for player in game_state['players']:
        if player['total'] > 21:
            # Player busted
            player['winner'] = 'lose'
            player['balance'] -= player['bet']
        elif dealer_busted:
            # Dealer busted, player wins
            player['winner'] = 'win'
            if player['total'] == 21 and len(player['hand']) == 2:
                # Blackjack pays 3:2
                player['balance'] += int(player['bet'] * 1.5)
            else:
                player['balance'] += player['bet']
        elif player['total'] > dealer_total:
            # Player wins
            player['winner'] = 'win'
            if player['total'] == 21 and len(player['hand']) == 2:
                # Blackjack pays 3:2
                player['balance'] += int(player['bet'] * 1.5)
            else:
                player['balance'] += player['bet']
        elif player['total'] < dealer_total:
            # Dealer wins
            player['winner'] = 'lose'
            player['balance'] -= player['bet']
        else:
            # Push
            player['winner'] = 'push'

@app.route('/api/start', methods=['POST'])
def start_game():
    session_id = get_session_id()
    data = request.get_json()
    player1_name = data.get('player1Name', 'Player 1')
    player2_name = data.get('player2Name', 'Player 2')
    balance = data.get('balance', 100)
    
    game_state = create_game_state()
    game_state['players'] = [
        create_player(1, player1_name, balance),
        create_player(2, player2_name, balance)
    ]
    game_state['gamePhase'] = 'betting'
    game_state['currentPlayerIndex'] = 0
    game_state['players'][0]['isActive'] = True
    game_state['message'] = f'{player1_name}, place your bet!'
    
    game_sessions[session_id] = game_state
    
    return jsonify({
        'success': True,
        'gameState': format_game_state(game_state)
    })

@app.route('/api/bet', methods=['POST'])
def place_bet():
    session_id = get_session_id()
    if session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'Game not started'})
    
    game_state = game_sessions[session_id]
    data = request.get_json()
    player_id = data.get('playerId')
    bet = data.get('bet', 0)
    
    if game_state['gamePhase'] != 'betting':
        return jsonify({'success': False, 'message': 'Not in betting phase'})
    
    player = next((p for p in game_state['players'] if p['id'] == player_id), None)
    if not player or not player['isActive']:
        return jsonify({'success': False, 'message': 'Invalid player or not active'})
    
    if bet <= 0 or bet > player['balance']:
        return jsonify({'success': False, 'message': 'Invalid bet amount'})
    
    player['bet'] = bet
    player['isActive'] = False
    
    # Move to next player or start dealing
    if game_state['currentPlayerIndex'] < len(game_state['players']) - 1:
        game_state['currentPlayerIndex'] += 1
        next_player = game_state['players'][game_state['currentPlayerIndex']]
        next_player['isActive'] = True
        game_state['message'] = f'{next_player["name"]}, place your bet!'
    else:
        # All bets placed, deal cards
        game_state['deck'] = shuffle_deck(create_deck())
        game_state['dealerHand'] = [deal_card(game_state['deck']), deal_card(game_state['deck'])]
        game_state['dealerTotal'] = calculate_hand(game_state['dealerHand'])
        
        # Deal cards to players
        for player in game_state['players']:
            player['hand'] = [deal_card(game_state['deck']), deal_card(game_state['deck'])]
            player['total'] = calculate_hand(player['hand'])
            player['canDoubleDown'] = can_double_down(player)
            player['isFinished'] = False
        
        # Start with first player
        game_state['gamePhase'] = 'playing'
        game_state['currentPlayerIndex'] = 0
        game_state['players'][0]['isActive'] = True
        
        # Check for blackjacks
        blackjacks = [p for p in game_state['players'] if p['total'] == 21]
        if blackjacks:
            for player in blackjacks:
                player['isFinished'] = True
                player['isActive'] = False
            
            # Move to next non-blackjack player
            next_player_index = 0
            while (next_player_index < len(game_state['players']) and 
                   game_state['players'][next_player_index]['isFinished']):
                next_player_index += 1
            
            if next_player_index < len(game_state['players']):
                game_state['currentPlayerIndex'] = next_player_index
                game_state['players'][next_player_index]['isActive'] = True
                game_state['message'] = f'{game_state["players"][next_player_index]["name"]}, choose your action!'
            else:
                # All players have blackjack or are finished
                game_state['gamePhase'] = 'dealer'
                dealer_play(game_state)
                determine_winners(game_state)
                game_state['gamePhase'] = 'results'
                game_state['message'] = 'Round complete! Check results.'
        else:
            game_state['message'] = f'{game_state["players"][0]["name"]}, choose your action!'
    
    return jsonify({
        'success': True,
        'gameState': format_game_state(game_state)
    })

@app.route('/api/hit', methods=['POST'])
def hit():
    session_id = get_session_id()
    if session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'Game not started'})
    
    game_state = game_sessions[session_id]
    data = request.get_json()
    player_id = data.get('playerId')
    
    if game_state['gamePhase'] != 'playing':
        return jsonify({'success': False, 'message': 'Not in playing phase'})
    
    player = next((p for p in game_state['players'] if p['id'] == player_id), None)
    if not player or not player['isActive']:
        return jsonify({'success': False, 'message': 'Invalid player or not active'})
    
    # Deal card to player
    new_card = deal_card(game_state['deck'])
    player['hand'].append(new_card)
    player['total'] = calculate_hand(player['hand'])
    player['canDoubleDown'] = False
    
    if player['total'] > 21:
        # Player busted
        player['isFinished'] = True
        player['isActive'] = False
        game_state['message'] = f'{player["name"]} busted!'
        
        # Move to next player
        next_player_index = game_state['currentPlayerIndex'] + 1
        while (next_player_index < len(game_state['players']) and 
               game_state['players'][next_player_index]['isFinished']):
            next_player_index += 1
        
        if next_player_index < len(game_state['players']):
            game_state['currentPlayerIndex'] = next_player_index
            game_state['players'][next_player_index]['isActive'] = True
            game_state['message'] += f' {game_state["players"][next_player_index]["name"]}, your turn!'
        else:
            # All players finished
            game_state['gamePhase'] = 'dealer'
            dealer_play(game_state)
            determine_winners(game_state)
            game_state['gamePhase'] = 'results'
            game_state['message'] = 'Round complete! Check results.'
    else:
        game_state['message'] = f'{player["name"]} drew {new_card["value"]} of {new_card["suit"]}. Choose your action.'
    
    return jsonify({
        'success': True,
        'gameState': format_game_state(game_state)
    })

@app.route('/api/stand', methods=['POST'])
def stand():
    session_id = get_session_id()
    if session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'Game not started'})
    
    game_state = game_sessions[session_id]
    data = request.get_json()
    player_id = data.get('playerId')
    
    if game_state['gamePhase'] != 'playing':
        return jsonify({'success': False, 'message': 'Not in playing phase'})
    
    player = next((p for p in game_state['players'] if p['id'] == player_id), None)
    if not player or not player['isActive']:
        return jsonify({'success': False, 'message': 'Invalid player or not active'})
    
    # Player stands
    player['isFinished'] = True
    player['isActive'] = False
    
    # Move to next player
    next_player_index = game_state['currentPlayerIndex'] + 1
    while (next_player_index < len(game_state['players']) and 
           game_state['players'][next_player_index]['isFinished']):
        next_player_index += 1
    
    if next_player_index < len(game_state['players']):
        game_state['currentPlayerIndex'] = next_player_index
        game_state['players'][next_player_index]['isActive'] = True
        game_state['message'] = f'{player["name"]} stands. {game_state["players"][next_player_index]["name"]}, your turn!'
    else:
        # All players finished
        game_state['gamePhase'] = 'dealer'
        dealer_play(game_state)
        determine_winners(game_state)
        game_state['gamePhase'] = 'results'
        game_state['message'] = 'Round complete! Check results.'
    
    return jsonify({
        'success': True,
        'gameState': format_game_state(game_state)
    })

@app.route('/api/double', methods=['POST'])
def double_down():
    session_id = get_session_id()
    if session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'Game not started'})
    
    game_state = game_sessions[session_id]
    data = request.get_json()
    player_id = data.get('playerId')
    
    if game_state['gamePhase'] != 'playing':
        return jsonify({'success': False, 'message': 'Not in playing phase'})
    
    player = next((p for p in game_state['players'] if p['id'] == player_id), None)
    if not player or not player['isActive']:
        return jsonify({'success': False, 'message': 'Invalid player or not active'})
    
    if not can_double_down(player):
        return jsonify({'success': False, 'message': 'Cannot double down - insufficient balance or invalid timing'})
    
    # Double the bet and deal one card
    player['bet'] *= 2
    new_card = deal_card(game_state['deck'])
    player['hand'].append(new_card)
    player['total'] = calculate_hand(player['hand'])
    player['isFinished'] = True
    player['isActive'] = False
    
    if player['total'] > 21:
        game_state['message'] = f'{player["name"]} doubled down and busted!'
    else:
        game_state['message'] = f'{player["name"]} doubled down and drew {new_card["value"]} of {new_card["suit"]}.'
    
    # Move to next player
    next_player_index = game_state['currentPlayerIndex'] + 1
    while (next_player_index < len(game_state['players']) and 
           game_state['players'][next_player_index]['isFinished']):
        next_player_index += 1
    
    if next_player_index < len(game_state['players']):
        game_state['currentPlayerIndex'] = next_player_index
        game_state['players'][next_player_index]['isActive'] = True
        game_state['message'] += f' {game_state["players"][next_player_index]["name"]}, your turn!'
    else:
        # All players finished
        game_state['gamePhase'] = 'dealer'
        dealer_play(game_state)
        determine_winners(game_state)
        game_state['gamePhase'] = 'results'
        game_state['message'] = 'Round complete! Check results.'
    
    return jsonify({
        'success': True,
        'gameState': format_game_state(game_state)
    })

@app.route('/api/next-round', methods=['POST'])
def next_round():
    session_id = get_session_id()
    if session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'Game not started'})
    
    game_state = game_sessions[session_id]
    
    if game_state['gamePhase'] != 'results':
        return jsonify({'success': False, 'message': 'Not in results phase'})
    
    # Reset for next round
    game_state['deck'] = shuffle_deck(create_deck())
    game_state['dealerHand'] = []
    game_state['dealerTotal'] = 0
    game_state['gamePhase'] = 'betting'
    game_state['currentPlayerIndex'] = 0
    
    for player in game_state['players']:
        player['hand'] = []
        player['total'] = 0
        player['bet'] = 0
        player['canDoubleDown'] = False
        player['isActive'] = False
        player['isFinished'] = False
        player['winner'] = None
    
    # Check if players have money left
    active_players = [p for p in game_state['players'] if p['balance'] > 0]
    if len(active_players) == 0:
        game_state['gamePhase'] = 'finished'
        game_state['message'] = 'Game over! All players are out of money.'
    else:
        game_state['players'][0]['isActive'] = True
        game_state['message'] = f'{game_state["players"][0]["name"]}, place your bet!'
    
    return jsonify({
        'success': True,
        'gameState': format_game_state(game_state)
    })

@app.route('/api/state', methods=['GET'])
def get_state():
    session_id = get_session_id()
    if session_id not in game_sessions:
        return jsonify({'success': False, 'message': 'Game not started'})
    
    game_state = game_sessions[session_id]
    return jsonify({
        'success': True,
        'gameState': format_game_state(game_state)
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