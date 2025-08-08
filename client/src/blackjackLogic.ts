// blackjackLogic.ts
// Pure TypeScript implementation of blackjack game logic for static frontend use
import type { GameState, Player, Card, GameResponse } from "./types";

function createDeck(): Card[] {
  const suits = ["♠", "♥", "♦", "♣"];
  const values = [
    "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K",
  ];
  const deck: Card[] = [];
  for (const suit of suits) {
    for (const value of values) {
      deck.push({ value, suit });
    }
  }
  return shuffle(deck);
}

function shuffle(deck: Card[]): Card[] {
  const arr = [...deck];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function cardValue(card: Card): number {
  if (card.value === "A") return 11;
  if (["K", "Q", "J"].includes(card.value)) return 10;
  return parseInt(card.value);
}

function handTotal(hand: Card[]): number {
  let total = 0;
  let aces = 0;
  for (const card of hand) {
    total += cardValue(card);
    if (card.value === "A") aces++;
  }
  while (total > 21 && aces > 0) {
    total -= 10;
    aces--;
  }
  return total;
}


// --- Static game state for the static site ---
let gameState: GameState | null = null;
let deck: Card[] = [];

function resetDeck() {
  deck = createDeck();
}

function dealCard(): Card {
  if (deck.length === 0) resetDeck();
  return deck.pop()!;
}

function startGame(player1Name: string, player2Name: string, balance: number): GameResponse {
  resetDeck();
  const players: Player[] = [
    {
      id: 1,
      name: player1Name,
      hand: [],
      total: 0,
      balance,
      bet: 0,
      canDoubleDown: false,
      isActive: true,
      isFinished: false,
    },
    {
      id: 2,
      name: player2Name,
      hand: [],
      total: 0,
      balance,
      bet: 0,
      canDoubleDown: false,
      isActive: false,
      isFinished: false,
    },
  ];
  gameState = {
    players,
    dealerHand: [],
    dealerTotal: 0,
    gamePhase: 'betting',
    currentPlayerIndex: 0,
    message: 'Place your bets!',
    allPlayersFinished: false,
  };
  return { success: true, gameState };
}

function placeBet(playerId: number, bet: number): GameResponse {
  if (!gameState) return { success: false, gameState: null!, message: 'No game in progress.' };
  const player = gameState.players.find(p => p.id === playerId);
  if (!player || player.bet > 0 || bet > player.balance || bet <= 0) {
    return { success: false, gameState, message: 'Invalid bet.' };
  }
  player.bet = bet;
  player.balance -= bet;
  // Move to next player or start round
  const nextIdx = gameState.players.findIndex(p => p.bet === 0);
  if (nextIdx === -1) {
    // All bets placed, deal cards
    for (const p of gameState.players) {
      p.hand = [dealCard(), dealCard()];
      p.total = handTotal(p.hand);
      p.isActive = false;
      p.isFinished = false;
      p.canDoubleDown = p.balance >= p.bet && p.hand.length === 2;
    }
    gameState.dealerHand = [dealCard(), dealCard()];
    gameState.dealerTotal = handTotal(gameState.dealerHand);
    gameState.gamePhase = 'playing';
    gameState.currentPlayerIndex = 0;
    gameState.players[0].isActive = true;
    gameState.message = `${gameState.players[0].name}'s turn!`;
  } else {
    // Next player bets
    gameState.currentPlayerIndex = nextIdx;
    gameState.players.forEach((p, i) => (p.isActive = i === nextIdx));
    gameState.message = `${gameState.players[nextIdx].name}'s turn to bet!`;
  }
  return { success: true, gameState };
}

function hit(playerId: number): GameResponse {
  if (!gameState) return { success: false, gameState: null!, message: 'No game in progress.' };
  const player = gameState.players.find(p => p.id === playerId);
  if (!player || !player.isActive || player.isFinished) {
    return { success: false, gameState, message: 'Invalid action.' };
  }
  player.hand.push(dealCard());
  player.total = handTotal(player.hand);
  player.canDoubleDown = false;
  if (player.total > 21) {
    player.isFinished = true;
    player.isActive = false;
    return nextPlayerOrDealer();
  }
  return { success: true, gameState };
}

function stand(playerId: number): GameResponse {
  if (!gameState) return { success: false, gameState: null!, message: 'No game in progress.' };
  const player = gameState.players.find(p => p.id === playerId);
  if (!player || !player.isActive || player.isFinished) {
    return { success: false, gameState, message: 'Invalid action.' };
  }
  player.isFinished = true;
  player.isActive = false;
  return nextPlayerOrDealer();
}

function doubleDown(playerId: number): GameResponse {
  if (!gameState) return { success: false, gameState: null!, message: 'No game in progress.' };
  const player = gameState.players.find(p => p.id === playerId);
  if (!player || !player.isActive || player.isFinished || !player.canDoubleDown || player.balance < player.bet) {
    return { success: false, gameState, message: 'Cannot double down.' };
  }
  player.balance -= player.bet;
  player.bet *= 2;
  player.hand.push(dealCard());
  player.total = handTotal(player.hand);
  player.canDoubleDown = false;
  player.isFinished = true;
  player.isActive = false;
  return nextPlayerOrDealer();
}

function nextPlayerOrDealer(): GameResponse {
  if (!gameState) return { success: false, gameState: null!, message: 'No game in progress.' };
  const nextIdx = gameState.players.findIndex(p => !p.isFinished);
  if (nextIdx === -1) {
    // All players finished, dealer's turn
    gameState.gamePhase = 'dealer';
    gameState.players.forEach(p => (p.isActive = false));
    dealerPlay();
    return { success: true, gameState };
  } else {
    gameState.currentPlayerIndex = nextIdx;
    gameState.players.forEach((p, i) => (p.isActive = i === nextIdx));
    gameState.message = `${gameState.players[nextIdx].name}'s turn!`;
    return { success: true, gameState };
  }
}

function dealerPlay() {
  if (!gameState) return;
  while (handTotal(gameState.dealerHand) < 17) {
    gameState.dealerHand.push(dealCard());
  }
  gameState.dealerTotal = handTotal(gameState.dealerHand);
  resolveResults();
}

function resolveResults() {
  if (!gameState) return;
  const dealerTotal = handTotal(gameState.dealerHand);
  for (const player of gameState.players) {
    if (player.total > 21) {
      player.winner = 'lose';
    } else if (dealerTotal > 21 || player.total > dealerTotal) {
      player.winner = 'win';
      player.balance += player.bet * 2;
    } else if (player.total === dealerTotal) {
      player.winner = 'push';
      player.balance += player.bet;
    } else {
      player.winner = 'lose';
    }
    player.bet = 0;
  }
  gameState.gamePhase = 'results';
  gameState.message = 'Round complete!';
  gameState.allPlayersFinished = gameState.players.every(p => p.balance === 0);
  if (gameState.allPlayersFinished) {
    gameState.gamePhase = 'finished';
    gameState.message = 'Game over! All players are out of money.';
  }
}

function nextRound(): GameResponse {
  if (!gameState) return { success: false, gameState: null!, message: 'No game in progress.' };
  if (gameState.allPlayersFinished) {
    return { success: false, gameState, message: 'Game over.' };
  }
  for (const p of gameState.players) {
    p.hand = [];
    p.total = 0;
    p.bet = 0;
    p.canDoubleDown = false;
    p.isActive = false;
    p.isFinished = false;
    p.winner = undefined;
  }
  gameState.dealerHand = [];
  gameState.dealerTotal = 0;
  gameState.gamePhase = 'betting';
  gameState.currentPlayerIndex = 0;
  gameState.players[0].isActive = true;
  gameState.message = 'Place your bets!';
  return { success: true, gameState };
}

function getGameState(): GameResponse {
  if (!gameState) return { success: false, gameState: null!, message: 'No game in progress.' };
  return { success: true, gameState };
}

export {
  createDeck,
  shuffle,
  cardValue,
  handTotal,
  startGame,
  placeBet,
  hit,
  stand,
  doubleDown,
  nextRound,
  getGameState,
};
