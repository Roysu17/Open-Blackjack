import { useState } from "react";
import { Hand } from "./components/Hand";
import { PlayerHand } from "./components/PlayerHand";
import { api } from "./api";
import type { GameState, Player } from "./types";
import "./App.css";

function App() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [betInput, setBetInput] = useState("");
  const [balanceInput, setBalanceInput] = useState("100");
  const [player1Name, setPlayer1Name] = useState("Player 1");
  const [player2Name, setPlayer2Name] = useState("Player 2");
  const [loading, setLoading] = useState(false);

  const startNewGame = async () => {
    setLoading(true);
    try {
      const response = await api.startGame(player1Name, player2Name, parseInt(balanceInput));
      if (response.success) {
        setGameState(response.gameState);
      }
    } catch (error) {
      console.error("Failed to start game:", error);
    }
    setLoading(false);
  };

  const placeBet = async (playerId: number) => {
    if (!gameState || !betInput) return;
    setLoading(true);
    try {
      const response = await api.placeBet(playerId, parseInt(betInput));
      if (response.success) {
        setGameState(response.gameState);
        setBetInput("");
      }
    } catch (error) {
      console.error("Failed to place bet:", error);
    }
    setLoading(false);
  };

  const hit = async (playerId: number) => {
    setLoading(true);
    try {
      const response = await api.hit(playerId);
      if (response.success) {
        setGameState(response.gameState);
      }
    } catch (error) {
      console.error("Failed to hit:", error);
    }
    setLoading(false);
  };

  const stand = async (playerId: number) => {
    setLoading(true);
    try {
      const response = await api.stand(playerId);
      if (response.success) {
        setGameState(response.gameState);
      }
    } catch (error) {
      console.error("Failed to stand:", error);
    }
    setLoading(false);
  };

  const doubleDown = async (playerId: number) => {
    setLoading(true);
    try {
      const response = await api.doubleDown(playerId);
      if (response.success) {
        setGameState(response.gameState);
      }
    } catch (error) {
      console.error("Failed to double down:", error);
    }
    setLoading(false);
  };

  const nextRound = async () => {
    setLoading(true);
    try {
      const response = await api.nextRound();
      if (response.success) {
        setGameState(response.gameState);
      }
    } catch (error) {
      console.error("Failed to start next round:", error);
    }
    setLoading(false);
  };

  const getActivePlayer = (): Player | null => {
    if (!gameState) return null;
    return gameState.players.find(p => p.isActive) || null;
  };

  if (!gameState) {
    return (
      <div className="app">
        <div className="game-container">
          <h1>🃏 Open Blackjack - Multiplayer</h1>
          <div className="start-game">
            <div className="player-setup">
              <label>
                Player 1 Name:
                <input
                  type="text"
                  value={player1Name}
                  onChange={(e) => setPlayer1Name(e.target.value)}
                  placeholder="Player 1"
                />
              </label>
              <label>
                Player 2 Name:
                <input
                  type="text"
                  value={player2Name}
                  onChange={(e) => setPlayer2Name(e.target.value)}
                  placeholder="Player 2"
                />
              </label>
              <label>
                Starting Balance (each): $
                <input
                  type="number"
                  value={balanceInput}
                  onChange={(e) => setBalanceInput(e.target.value)}
                  min="1"
                />
              </label>
            </div>
            <button
              onClick={startNewGame}
              disabled={loading || !balanceInput || !player1Name || !player2Name}
            >
              {loading ? "Starting..." : "Start Multiplayer Game"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  const activePlayer = getActivePlayer();

  return (
    <div className="app">
      <div className="game-container">
        <h1>🃏 Open Blackjack - Multiplayer</h1>

        {gameState.message && (
          <div className="message">{gameState.message}</div>
        )}

        <div className="game-layout">
          {/* Dealer Hand */}
          <div className="dealer-section">
            <Hand
              cards={gameState.dealerHand}
              total={gameState.dealerTotal}
              title="Dealer"
              hideFirstCard={gameState.gamePhase === "playing" || gameState.gamePhase === "betting"}
            />
          </div>

          {/* Players */}
          <div className="players-section">
            {gameState.players.map((player, index) => (
              <PlayerHand
                key={player.id}
                player={player}
                isActive={player.isActive}
                isCurrentPlayer={index === gameState.currentPlayerIndex}
              />
            ))}
          </div>
        </div>

        <div className="controls">
          {gameState.gamePhase === "betting" && activePlayer && (
            <div className="betting">
              <div className="betting-header">
                <h3>{activePlayer.name}'s turn to bet</h3>
              </div>
              <label>
                Bet Amount: $
                <input
                  type="number"
                  value={betInput}
                  onChange={(e) => setBetInput(e.target.value)}
                  min="1"
                  max={activePlayer.balance}
                  placeholder="Enter bet amount"
                />
              </label>
              <button
                onClick={() => placeBet(activePlayer.id)}
                disabled={
                  loading || !betInput || parseInt(betInput) > activePlayer.balance || parseInt(betInput) <= 0
                }
              >
                {loading ? "Placing..." : "Place Bet"}
              </button>
            </div>
          )}

          {gameState.gamePhase === "playing" && activePlayer && (
            <div className="playing">
              <div className="playing-header">
                <h3>{activePlayer.name}'s turn</h3>
              </div>
              <div className="action-buttons">
                <button onClick={() => hit(activePlayer.id)} disabled={loading}>
                  Hit
                </button>
                <button onClick={() => stand(activePlayer.id)} disabled={loading}>
                  Stand
                </button>
                {activePlayer.canDoubleDown && (
                  <button
                    onClick={() => doubleDown(activePlayer.id)}
                    disabled={loading || activePlayer.balance < activePlayer.bet}
                  >
                    Double Down
                  </button>
                )}
              </div>
            </div>
          )}

          {gameState.gamePhase === "results" && (
            <div className="results">
              <div className="results-summary">
                <h3>Round Results</h3>
                {gameState.players.map(player => (
                  <div key={player.id} className={`result-item ${player.winner}`}>
                    {player.name}: {player.winner === 'win' ? 'Won' : player.winner === 'lose' ? 'Lost' : 'Push'}
                    {player.winner === 'win' && player.total === 21 && player.hand.length === 2 && ' (Blackjack!)'}
                  </div>
                ))}
              </div>
              <button onClick={nextRound} disabled={loading}>
                {loading ? "Starting..." : "Next Round"}
              </button>
            </div>
          )}

          {gameState.gamePhase === "finished" && (
            <div className="finished">
              <h3>Game Over!</h3>
              <p>All players are out of money.</p>
              <button onClick={() => setGameState(null)}>Start New Game</button>
            </div>
          )}

          <div className="game-controls">
            <button onClick={() => setGameState(null)} className="secondary">
              Exit Game
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
