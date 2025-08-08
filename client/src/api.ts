import type { GameResponse } from "./types";
import {
  startGame as logicStartGame,
  placeBet as logicPlaceBet,
  hit as logicHit,
  stand as logicStand,
  doubleDown as logicDoubleDown,
  nextRound as logicNextRound,
  getGameState as logicGetGameState,
} from "./blackjackLogic";

export const api = {
  async startGame(player1Name: string, player2Name: string, balance: number): Promise<GameResponse> {
    return logicStartGame(player1Name, player2Name, balance);
  },
  async placeBet(playerId: number, bet: number): Promise<GameResponse> {
    return logicPlaceBet(playerId, bet);
  },
  async hit(playerId: number): Promise<GameResponse> {
    return logicHit(playerId);
  },
  async stand(playerId: number): Promise<GameResponse> {
    return logicStand(playerId);
  },
  async doubleDown(playerId: number): Promise<GameResponse> {
    return logicDoubleDown(playerId);
  },
  async nextRound(): Promise<GameResponse> {
    return logicNextRound();
  },
  async getGameState(): Promise<GameResponse> {
    return logicGetGameState();
  },
};
