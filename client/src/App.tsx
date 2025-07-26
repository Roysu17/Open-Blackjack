import { useState } from "react";
import { Hand } from "./components/Hand";
import { api } from "./api";
import type { GameState } from "./types";
import "./App.css";

function App() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [betInput, setBetInput] = useState("");
  const [balanceInput, setBalanceInput] = useState("100");
  const [loading, setLoading] = useState(false);

  const startNewGame = async () => {
    setLoading(true);
    try {
      const response = await api.startGame(parseInt(balanceInput));
      if (response.success) {
        setGameState(response.gameState);
      }
    } catch (error) {
      console.error("Failed to start game:", error);
    }
    setLoading(false);
  };

  const placeBet = async () => {
    if (!gameState || !betInput) return;
    setLoading(true);
    try {
      const response = await api.placeBet(parseInt(betInput));
      if (response.success) {
        setGameState(response.gameState);
        setBetInput("");
      }
    } catch (error) {
      console.error("Failed to place bet:", error);
    }
    setLoading(false);
  };

  const hit = async () => {
    setLoading(true);
    try {
      const response = await api.hit();
      if (response.success) {
        setGameState(response.gameState);
      }
    } catch (error) {
      console.error("Failed to hit:", error);
    }
    setLoading(false);
  };

  const stand = async () => {
    setLoading(true);
    try {
      const response = await api.stand();
      if (response.success) {
        setGameState(response.gameState);
      }
    } catch (error) {
      console.error("Failed to stand:", error);
    }
    setLoading(false);
  };

  const doubleDown = async () => {
    setLoading(true);
    try {
      const response = await api.doubleDown();
      if (response.success) {
        setGameState(response.gameState);
      }
    } catch (error) {
      console.error("Failed to double down:", error);
    }
    setLoading(false);
  };

  if (!gameState) {
    return (
      <div className="app">
        <div className="game-container">
          <h1>🃏 Open Blackjack</h1>
          <div className="start-game">
            <label>
              Starting Balance: $
              <input
                type="number"
                value={balanceInput}
                onChange={(e) => setBalanceInput(e.target.value)}
                min="1"
              />
            </label>
            <button onClick={startNewGame} disabled={loading || !balanceInput}>
              {loading ? "Starting..." : "Start Game"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="game-container">
        <h1>🃏 Open Blackjack</h1>

        <div className="game-info">
          <div className="balance">Balance: ${gameState.balance}</div>
          {gameState.bet > 0 && (
            <div className="current-bet">Bet: ${gameState.bet}</div>
          )}
        </div>

        {gameState.message && (
          <div className="message">{gameState.message}</div>
        )}

        <div className="hands">
          <Hand
            cards={gameState.dealerHand}
            total={gameState.dealerTotal}
            title="Dealer"
            hideFirstCard={gameState.gamePhase === "playing"}
          />

          <Hand
            cards={gameState.playerHand}
            total={gameState.playerTotal}
            title="Your Hand"
          />
        </div>

        <div className="controls">
          {gameState.gamePhase === "betting" && (
            <div className="betting">
              <label>
                Bet Amount: $
                <input
                  type="number"
                  value={betInput}
                  onChange={(e) => setBetInput(e.target.value)}
                  min="1"
                  max={gameState.balance}
                />
              </label>
              <button
                onClick={placeBet}
                disabled={
                  loading || !betInput || parseInt(betInput) > gameState.balance
                }
              >
                {loading ? "Placing..." : "Place Bet"}
              </button>
              <button onClick={() => setGameState(null)}>Cash Out</button>
            </div>
          )}

          {gameState.gamePhase === "playing" && (
            <div className="playing">
              <button onClick={hit} disabled={loading}>
                Hit
              </button>
              <button onClick={stand} disabled={loading}>
                Stand
              </button>
              {gameState.canDoubleDown && (
                <button
                  onClick={doubleDown}
                  disabled={loading || gameState.balance < gameState.bet}
                >
                  Double Down
                </button>
              )}
            </div>
          )}

          {gameState.gamePhase === "finished" && (
            <div className="finished">
              <button onClick={startNewGame} disabled={loading}>
                {loading ? "Starting..." : "New Hand"}
              </button>
              <button onClick={() => setGameState(null)}>Cash Out</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
