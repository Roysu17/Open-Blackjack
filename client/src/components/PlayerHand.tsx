import { Card } from "./Card";
import type { Player } from "../types";

interface PlayerHandProps {
  player: Player;
  isActive: boolean;
  isCurrentPlayer: boolean;
}

export function PlayerHand({ player, isActive, isCurrentPlayer }: PlayerHandProps) {
  const getPlayerStatus = () => {
    if (player.winner === 'win') return '🎉 Won!';
    if (player.winner === 'lose') return '😞 Lost';
    if (player.winner === 'push') return '🤝 Push';
    if (player.total > 21) return '💥 Bust!';
    if (player.total === 21 && player.hand.length === 2) return '🃏 Blackjack!';
    return '';
  };

  const statusMessage = getPlayerStatus();

  return (
    <div className={`player-hand ${isActive ? 'active' : ''} ${isCurrentPlayer ? 'current' : ''}`}>
      <div className="player-header">
        <h3>{player.name}</h3>
        <div className="player-info">
          <div className="balance">Balance: ${player.balance}</div>
          {player.bet > 0 && <div className="bet">Bet: ${player.bet}</div>}
        </div>
      </div>
      
      <div className="cards">
        {player.hand.map((card, index) => (
          <Card key={index} card={card} />
        ))}
      </div>
      
      <div className="hand-total">
        {player.hand.length > 0 ? `Total: ${player.total}` : 'No cards yet'}
      </div>
      
      {statusMessage && (
        <div className={`status-message ${player.winner || 'info'}`}>
          {statusMessage}
        </div>
      )}
      
      {isActive && (
        <div className="active-indicator">
          👆 Your turn!
        </div>
      )}
    </div>
  );
}