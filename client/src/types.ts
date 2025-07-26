export interface Card {
  value: string;
  suit: string;
}

export interface Player {
  id: number;
  name: string;
  hand: Card[];
  total: number;
  balance: number;
  bet: number;
  canDoubleDown: boolean;
  isActive: boolean;
  isFinished: boolean;
  winner?: 'win' | 'lose' | 'push';
}

export interface GameState {
  players: Player[];
  dealerHand: Card[];
  dealerTotal: number;
  gamePhase: 'setup' | 'betting' | 'playing' | 'dealer' | 'results' | 'finished';
  currentPlayerIndex: number;
  message: string;
  allPlayersFinished: boolean;
}

export interface GameResponse {
  success: boolean;
  gameState: GameState;
  message?: string;
}