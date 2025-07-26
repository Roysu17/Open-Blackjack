export interface Card {
  value: string;
  suit: string;
}

export interface GameState {
  playerHand: Card[];
  dealerHand: Card[];
  playerTotal: number;
  dealerTotal: number;
  balance: number;
  bet: number;
  gamePhase: 'betting' | 'playing' | 'dealer' | 'finished';
  canDoubleDown: boolean;
  message: string;
  winner?: 'player' | 'dealer' | 'push';
}

export interface GameResponse {
  success: boolean;
  gameState: GameState;
  message?: string;
}