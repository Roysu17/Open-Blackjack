# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview


Open-Blackjack is a web-based multiplayer implementation of the classic Blackjack casino game with a React TypeScript frontend and Flask Python backend. The game supports hotseat multiplayer for two players on a single device, featuring a modern web interface while maintaining the classic casino experience.


## Running the Application

### Development Mode
```bash
# Start Flask backend
pip install -r requirements.txt
python app.py

# Start React frontend (in another terminal)
cd client
npm install
npm run dev
```

### Production Mode
```bash
# Build frontend
cd client
npm run build
cd ..

# Start Flask server (serves both API and built frontend)
pip install -r requirements.txt
python app.py
```

The application will be available at `http://localhost:5000`.

## Architecture

The application uses a client-server architecture:

### Backend (`app.py`)

Flask server with REST API endpoints for multiplayer games:
- `/api/start` - Initialize new multiplayer game with player names and starting balance
- `/api/bet` - Place bet for specific player and deal initial cards when both players bet
- `/api/hit` - Draw additional card for specific player
- `/api/stand` - End current player's turn, move to next player or dealer
- `/api/double` - Double down for specific player (double bet, one card, auto-stand)
- `/api/next-round` - Start next round after results are shown

- `/api/state` - Get current game state

Core game logic functions (from original `game.py`):
- `create_deck()` - Creates a standard 52-card deck
- `shuffle_deck(deck)` - Randomizes card order
- `deal_card(deck)` - Removes and returns top card
- `calculate_hand(hand)` - Computes hand value with Ace handling

### Frontend (`client/`)
React TypeScript application with Vite build system:
- `src/App.tsx` - Main multiplayer game component with turn-based state management
- `src/components/Card.tsx` - Individual playing card display
- `src/components/Hand.tsx` - Hand of cards with total (dealer)
- `src/components/PlayerHand.tsx` - Player-specific hand component with status indicators
- `src/api.ts` - API client for multiplayer backend communication
- `src/types.ts` - TypeScript interfaces for multiplayer game state and player data

### Game Features
- **Hotseat Multiplayer**: Two players take turns on the same device
- Standard Blackjack rules with single deck per hand
- Web-based UI with card animations and player status indicators
- Individual player balances and betting system
- Turn-based gameplay with visual active player indicators
- Double down option (when balance allows)
- Proper Ace value handling (1 or 11)
- Dealer AI following house rules (hit on 16, stand on 17)
- Round-based results with win/loss tracking
- Session-based game state management

### Multiplayer Flow
1. **Setup**: Enter both player names and starting balance
2. **Betting Phase**: Players take turns placing bets
3. **Playing Phase**: Players take turns hitting, standing, or doubling down
4. **Dealer Phase**: Dealer plays automatically when all players finish
5. **Results Phase**: Show round results and update balances
6. **Next Round**: Start new round or end game if players are out of money

## Development Notes

### Dependencies
- Backend: Flask, Flask-CORS (see `requirements.txt`)
- Frontend: React, TypeScript, Vite (see `client/package.json`)

### Build Commands
- `npm run dev` - Start development server with hot reload
- `npm run build` - Build production frontend to `client/dist/`
- `npm run preview` - Preview production build locally

### API Development
- Backend serves frontend static files in production
- Development proxy configured in `vite.config.ts` for API calls
- CORS enabled for development cross-origin requests
- Session management uses client IP (simplified for demo)