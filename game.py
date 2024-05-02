import random

def create_deck():
    """Create a deck of cards."""
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    return [{'value': v, 'suit': s} for s in suits for v in values]

def shuffle_deck(deck):
    """Shuffle the deck of cards."""
    random.shuffle(deck)
    return deck

def deal_card(deck):
    """Deal one card from the deck."""
    return deck.pop()

def calculate_hand(hand):
    """Calculate the total value of a hand."""
    total = 0
    aces = 0
    for card in hand:
        if card['value'] in ['Jack', 'Queen', 'King']:
            total += 10
        elif card['value'] == 'Ace':
            aces += 1
            total += 11
        else:
            total += int(card['value'])
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def show_hand(hand, total, hidden=False):
    """Print out the hand."""
    if hidden:
        print("[" + hand[0]['value'] + " of " + hand[0]['suit'] + ", Hidden]")
    else:
        for card in hand:
            print("[" + card['value'] + " of " + card['suit'] + "]", end=" ")
        print("= ", total)

def play_blackjack():
    print("Welcome to Blackjack!")
    quarters = int(input("Insert quarters (1 quarter = $25): "))
    balance = quarters * 25

    while balance > 0:
        deck = create_deck()
        shuffle_deck(deck)
        
        player_hand = [deal_card(deck), deal_card(deck)]
        dealer_hand = [deal_card(deck), deal_card(deck)]
        
        print(f"Your balance: ${balance}")
        bet = int(input("Place your bet: "))
        
        if bet > balance:
            print("You do not have enough balance.")
            continue
        
        print("Dealer's hand:")
        dealer_total = calculate_hand(dealer_hand)
        show_hand(dealer_hand, dealer_total, hidden=True)
        
        print("Your hand:")
        player_total = calculate_hand(player_hand)
        show_hand(player_hand, player_total)
        
        
        while True:
            if player_total == 21:
                print("Blackjack! You win!")
                balance += int(2 * bet)
                break

            choice = input("Type 'hit' to take another card, or 'stand' to hold: ").lower()
            if choice == 'hit':
                new_card = deal_card(deck)
                player_hand.append(new_card)
                print("You drew: [" + new_card['value'] + " of " + new_card['suit'] + "]")
                player_total = calculate_hand(player_hand)
                show_hand(player_hand, player_total)
                if player_total > 21:
                    print("Bust! You lose.")
                    balance -= bet
                    break
            elif choice == 'stand':
                print("Dealer's turn")
                show_hand(dealer_hand, dealer_total)
                while dealer_total < 17:
                    new_card = deal_card(deck)
                    dealer_hand.append(new_card)
                    dealer_total = calculate_hand(dealer_hand)
                show_hand(dealer_hand, dealer_total)
                if dealer_total > 21 or dealer_total < player_total:
                    print("You win!")
                    balance += bet
                elif dealer_total > player_total:
                    print("You lose.")
                    balance -= bet
                else:
                    print("Push (tie).")
                break
        print(f"New balance: ${balance}")

    print("You're out of quarters! Game over.")

if __name__ == "__main__":
    play_blackjack()
