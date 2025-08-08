import type { Card as CardType } from "../types";

interface CardProps {
  card: CardType;
  hidden?: boolean;
}

export function Card({ card, hidden = false }: CardProps) {
  if (hidden) {
    return (
      <div className="card card-hidden">
        <div className="card-back">🂠</div>
      </div>
    );
  }

  const getSuitSymbol = (suit: string) => {
    switch (suit.toLowerCase()) {
      case "hearts":
        return "♥️";
      case "diamonds":
        return "♦️";
      case "clubs":
        return "♣️";
      case "spades":
        return "♠️";
      default:
        return suit;
    }
  };

  const getSuitColor = (suit: string) => {
    return suit.toLowerCase() === "hearts" || suit.toLowerCase() === "diamonds"
      ? "red"
      : "black";
  };

  return (
    <div className={`card card-${getSuitColor(card.suit)}`}>
      <div className="card-value">{card.value}</div>
      <div className="card-suit">{getSuitSymbol(card.suit)}</div>
    </div>
  );
}
