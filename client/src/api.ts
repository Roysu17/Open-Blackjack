import type { GameResponse } from "./types";

const API_BASE = "/api";

export const api = {

  async startGame(player1Name: string, player2Name: string, balance: number): Promise<GameResponse> {
    const response = await fetch(`${API_BASE}/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ player1Name, player2Name, balance }),
    });
    return response.json();
  },


  async placeBet(playerId: number, bet: number): Promise<GameResponse> {
    const response = await fetch(`${API_BASE}/bet`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ playerId, bet }),

    });
    return response.json();
  },


  async hit(playerId: number): Promise<GameResponse> {
    const response = await fetch(`${API_BASE}/hit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ playerId }),
    });
    return response.json();
  },


  async stand(playerId: number): Promise<GameResponse> {
    const response = await fetch(`${API_BASE}/stand`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ playerId }),

    });
    return response.json();
  },


  async doubleDown(playerId: number): Promise<GameResponse> {
    const response = await fetch(`${API_BASE}/double`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ playerId }),
    });
    return response.json();
  },

  async nextRound(): Promise<GameResponse> {
    const response = await fetch(`${API_BASE}/next-round`, {
      method: "POST",

    });
    return response.json();
  },

  async getGameState(): Promise<GameResponse> {
    const response = await fetch(`${API_BASE}/state`);
    return response.json();
  },
};
