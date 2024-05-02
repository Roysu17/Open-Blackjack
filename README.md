# Open-Blackjack
 A python black jack game imitating old mechanical slots. This project is open source and free for all!

# Blackjack Rules (Default rules with `game.py`)

Blackjack is a popular casino game where the goal is to beat the dealer by having a hand total closer to 21 than the dealer's hand, without going over 21.

## Card Values

- **2 to 10**: Face value of the card.
- **Face Cards (Jack, Queen, King)**: 10 points each.
- **Aces**: Worth 1 or 11, whichever is more beneficial for the hand.

## Game Play

Blackjack typically uses multiple decks, but here it's played with one deck by default. You can modify the number of decks in `game.py`.

1. **Placing Bets**: Place your bet in the betting area.
2. **Dealing Cards**: You and the dealer each receive two cards. Your cards are dealt face up, while the dealer has one face up and one face down (the hole card).

## Your Turn

- **Hit**: Request another card. Repeat until you are satisfied with your total or you bust (exceed 21).
- **Stand**: Keep your current total.
- **Double Down**: Double your bet and receive only one more card. Note: This option is not available in all versions of the game.

## Dealer's Turn

The dealer must hit until their cards total at least 17, including a soft 17 where an Ace is counted as 11.

## Winning and Losing

- **Winning**: You win if your total is closer to 21 than the dealer's without going over. Winnings are paid at 1:1.
- **Push**: If you and the dealer have the same total, the bet is returned.
- **Losing**: You lose your bet if you bust or if the dealer's total is closer to 21.
- **Blackjack**: If your first two cards are an Ace and a 10-value card, it is called a 'Blackjack', which usually pays 3:2.

## Additional Tips

- Use basic strategy charts available online to optimize your play decisions based on your hand and the dealer's visible card.
- Remember, Blackjack is a game of chance, and the house has an inherent advantage.

Understanding the rules thoroughly can enhance your enjoyment and effectiveness in the game.
