# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Open-Blackjack is a web-based implementation of the classic Blackjack casino game with a React TypeScript frontend and Flask Python backend. The game features a modern web interface while maintaining the classic casino experience.

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
Flask server with REST API endpoints:
- `/api/start` - Initialize new game with starting balance
- `/api/bet` - Place bet and deal initial cards
- `/api/hit` - Draw additional card
- `/api/stand` - End player turn, dealer plays
- `/api/double` - Double down (double bet, one card, auto-stand)
- `/api/state` - Get current game state

Core game logic functions (from original `game.py`):
- `create_deck()` - Creates a standard 52-card deck
- `shuffle_deck(deck)` - Randomizes card order
- `deal_card(deck)` - Removes and returns top card
- `calculate_hand(hand)` - Computes hand value with Ace handling

### Frontend (`client/`)
React TypeScript application with Vite build system:
- `src/App.tsx` - Main game component with state management
- `src/components/Card.tsx` - Individual playing card display
- `src/components/Hand.tsx` - Hand of cards with total
- `src/api.ts` - API client for backend communication
- `src/types.ts` - TypeScript interfaces for game state

### Game Features
- Standard Blackjack rules with single deck per hand
- Web-based UI with card animations and styling
- Player balance and betting system
- Double down option (when balance allows)
- Proper Ace value handling (1 or 11)
- Dealer AI following house rules (hit on 16, stand on 17)
- Session-based game state management

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