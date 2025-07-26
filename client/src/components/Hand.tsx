import { Card } from "./Card";
import type { Card as CardType } from "../types";

interface HandProps {
  cards: CardType[];
  total: number;
  title: string;
  hideFirstCard?: boolean;
}

export function Hand({
  cards,
  total,
  title,
  hideFirstCard = false,
}: HandProps) {
  return (
    <div className="hand">
      <h3>{title}</h3>
      <div className="cards">
        {cards.map((card, index) => (
          <Card key={index} card={card} hidden={hideFirstCard && index === 1} />
        ))}
      </div>
      <div className="hand-total">
        {hideFirstCard && cards.length > 1 ? "?" : `Total: ${total}`}
      </div>
    </div>
  );
}
