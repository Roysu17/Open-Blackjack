import type { GameResponse } from "./types";

const API_BASE = "/api";

export const api = {
  async startGame(balance: number): Promise<GameResponse> {
    const response = await fetch(`${API_BASE}/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ balance }),
    });
    return response.json();
  },

  async placeBet(bet: number): Promise<GameResponse> {
    const response = await fetch(`${API_BASE}/bet`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ bet }),
    });
    return response.json();
  },

  async hit(): Promise<GameResponse> {
    const response = await fetch(`${API_BASE}/hit`, {
      method: "POST",
    });
    return response.json();
  },

  async stand(): Promise<GameResponse> {
    const response = await fetch(`${API_BASE}/stand`, {
      method: "POST",
    });
    return response.json();
  },

  async doubleDown(): Promise<GameResponse> {
    const response = await fetch(`${API_BASE}/double`, {
      method: "POST",
    });
    return response.json();
  },

  async getGameState(): Promise<GameResponse> {
    const response = await fetch(`${API_BASE}/state`);
    return response.json();
  },
};
