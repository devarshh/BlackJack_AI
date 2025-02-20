import random


class Deck:
    def __init__(self):
        self.cards = [
            (rank, suit) for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
            for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ]
        random.shuffle(self.cards)
        self.running_count = 0  # Track high vs. low cards seen

    def deal_card(self):
        card = self.cards.pop()
        self.update_count(card)
        return card

    def update_count(self, card):
        rank = card[0]
        if rank in ['2', '3', '4', '5', '6']:
            self.running_count += 1  # More low cards mean more high cards left
        elif rank in ['10', 'J', 'Q', 'K', 'A']:
            self.running_count -= 1  # More high cards mean fewer left

    def true_count(self):
        decks_remaining = max(1, len(self.cards) / 52)  # Avoid division by zero
        return self.running_count / decks_remaining  # Normalize count

    def remaining_cards(self):
        return [card[0] for card in self.cards]


class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0  # Track Aces separately

    def add_card(self, card):
        self.cards.append(card)
        rank = card[0]

        if rank in ['J', 'Q', 'K']:
            self.value += 10
        elif rank == 'A':
            self.value += 11  # Assume Ace is 11 initially
            self.aces += 1
        else:
            self.value += int(rank)

        # Adjust for Aces if we go over 21
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1

    def display_hand(self):
        return ', '.join([f"{rank} of {suit}" for rank, suit in self.cards])


class Player:
    def __init__(self, chips=1000, base_bet=10):
        self.chips = chips
        self.base_bet = base_bet
        self.current_bet = base_bet
        self.win_streak = 0  # Track consecutive wins
        self.lose_streak = 0  # Track consecutive losses

    def place_bet(self, true_count):
        true_count = round(true_count, 2)
        if true_count >= 2:
            self.current_bet = min(int(self.current_bet * 2),
                                   self.chips // 3)  # Bet aggressively when deck is favorable
        elif true_count <= 0:
            self.current_bet = max(self.base_bet // 2, 10)  # Bet cautiously when deck is unfavorable
        else:
            self.current_bet = max(self.base_bet, self.current_bet)  # Maintain bet

        self.current_bet = min(self.current_bet, self.chips)  # Ensure AI doesn't overbet
        self.chips -= self.current_bet
        print(f"Player bets {self.current_bet} chips (True Count: {true_count:.2f}).")
        return self.current_bet

    def win_bet(self, multiplier=2):
        self.chips += self.current_bet * multiplier
        self.win_streak += 1  # Increase win streak
        self.lose_streak = 0  # Reset losing streak

    def lose_bet(self):
        self.win_streak = 0  # Reset win streak
        self.lose_streak += 1  # Increase losing streak

    def reset_bet(self):
        pass  # No forced reset; betting logic handles adjustments dynamically

# Player's turn
def player_turn(deck, player_card, dealer_upcard, player):
    print("Player's turn...")
    dealer_value = 10 if dealer_upcard[0] in ['J', 'Q', 'K'] else (
        11 if dealer_upcard[0] == 'A' else int(dealer_upcard[0]))

    while True:
        if player_hand.value >= 17:
            print("AI chooses to stand.")
            break
        elif player_hand.value <= 11:
            print("AI chooses to hit.")
            player_hand.add_card(deck.deal_card())
        elif 12 <= player_hand.value <= 16:
            if dealer_value >= 7:
                print("AI chooses to hit due to strong dealer card.")
                player_hand.add_card(deck.deal_card())
            else:
                print("AI chooses to stand.")
                break
        else:
            break

        print("Player Hand:", player_hand.display_hand(), "| Value:", player_hand.value)
        if player_hand.value > 21:
            print("Bust! Player loses.")
            return False  # Player busted
    return True  # Player stands

# Function to handle dealer turn
def dealer_turn(deck, dealer_hand):
    print("Dealer's turn...")
    while dealer_hand.value < 17:
        dealer_hand.add_card(deck.deal_card())
    print("Dealer Hand:", dealer_hand.display_hand(), "| Value:", dealer_hand.value)


# Function to determine the winner
def determine_winner(player, player_hand, dealer_hand):
    if player_hand.value > 21:
        print("Player busts! Dealer wins.")
        player.lose_bet()
    elif dealer_hand.value > 21 or player_hand.value > dealer_hand.value:
        print("Player wins!")
        player.win_bet()
    elif player_hand.value < dealer_hand.value:
        print("Dealer wins.")
        player.lose_bet()
    else:
        print("It's a tie! Player gets their bet back.")
        player.chips += player.current_bet
    player.reset_bet()


# Main game loop
player = Player()
while True:
    deck = Deck()
    player_hand = Hand()
    dealer_hand = Hand()

    # AI now uses the True Count to adjust its bet
    true_count = deck.true_count()
    player.place_bet(true_count)

    # Deal two cards each
    player_hand.add_card(deck.deal_card())
    player_hand.add_card(deck.deal_card())
    dealer_hand.add_card(deck.deal_card())
    second_dealer_card = deck.deal_card()
    dealer_hand.add_card(second_dealer_card)

    # Player's turn (AI-based)
    if player_turn(deck, player_hand, dealer_hand.cards[0], player):
        dealer_turn(deck, dealer_hand)
        determine_winner(player, player_hand, dealer_hand)

    print(f"Player now has {player.chips} chips.")

    if player.chips <= 0:
        print("Game over! Player is out of chips.")
        break
    cont = input("Do you want to play another round? (y/n): ").lower()
    if cont != 'y':
        break
