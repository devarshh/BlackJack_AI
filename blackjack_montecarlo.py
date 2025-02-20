import random

class Deck:
    def __init__(self):
        self.initialize_deck()

    def initialize_deck(self):
        self.cards = [
            (rank, suit) for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
            for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ]
        random.shuffle(self.cards)
        self.running_count = 0

    def deal_card(self):
        if len(self.cards) < 15:
            self.initialize_deck()
        card = self.cards.pop()
        self.update_count(card)
        return card

    def update_count(self, card):
        rank = card[0]
        if rank in ['2', '3', '4', '5', '6']:
            self.running_count += 1
        elif rank in ['10', 'J', 'Q', 'K', 'A']:
            self.running_count -= 1

    def true_count(self):
        decks_remaining = max(1, len(self.cards) / 52)
        return self.running_count / decks_remaining

class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0

    def add_card(self, card):
        self.cards.append(card)
        rank = card[0]

        if rank in ['J', 'Q', 'K']:
            self.value += 10
        elif rank == 'A':
            self.value += 11
            self.aces += 1
        else:
            self.value += int(rank)

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
        self.lose_streak = 0

    def place_bet(self, true_count):
        true_count = round(true_count, 2)

        # Adjust bet dynamically
        if self.lose_streak >= 5:
            self.current_bet = max(self.base_bet // 2, 5)
        elif true_count >= 2:
            self.current_bet = min(int(self.base_bet * 1.5), self.chips // 4)
        elif true_count <= 0:
            self.current_bet = max(self.base_bet // 3, 5)
        else:
            self.current_bet = self.base_bet

        self.current_bet = min(self.current_bet, self.chips)
        self.chips -= self.current_bet
        game_stats["total_bets"] += self.current_bet
        return self.current_bet

    def win_bet(self):
        self.chips += self.current_bet * 2
        self.lose_streak = 0
        game_stats["wins"] += 1

    def lose_bet(self):
        self.lose_streak += 1
        game_stats["losses"] += 1

def player_turn(deck, player_hand, dealer_upcard):
    dealer_value = 10 if dealer_upcard[0] in ['J', 'Q', 'K'] else (
        11 if dealer_upcard[0] == 'A' else int(dealer_upcard[0]))

    while True:
        if player_hand.value == 17 and player_hand.aces > 0:
            player_hand.add_card(deck.deal_card())
        elif player_hand.value >= 17:
            break
        elif player_hand.value <= 11:
            player_hand.add_card(deck.deal_card())
        elif 12 <= player_hand.value <= 16:
            if dealer_value >= 7:
                player_hand.add_card(deck.deal_card())
            else:
                break
        if player_hand.value > 21:
            return False
    return True

def dealer_turn(deck, dealer_hand):
    while dealer_hand.value < 17:
        dealer_hand.add_card(deck.deal_card())

def determine_winner(player, player_hand, dealer_hand):
    if player_hand.value > 21:
        player.lose_bet()
    elif dealer_hand.value > 21 or player_hand.value > dealer_hand.value:
        player.win_bet()
    elif player_hand.value < dealer_hand.value:
        player.lose_bet()
    else:
        player.chips += player.current_bet

game_stats = {
    "wins": 0,
    "losses": 0,
    "ties": 0,
    "total_bets": 0
}

player = Player()
deck = Deck()
total_rounds = 50
round_count = 0

while round_count < total_rounds and player.chips > 0:
    player_hand = Hand()
    dealer_hand = Hand()

    true_count = deck.true_count()
    player.place_bet(true_count)

    player_hand.add_card(deck.deal_card())
    player_hand.add_card(deck.deal_card())
    dealer_hand.add_card(deck.deal_card())
    dealer_hand.add_card(deck.deal_card())

    if player_turn(deck, player_hand, dealer_hand.cards[0]):
        dealer_turn(deck, dealer_hand)
        determine_winner(player, player_hand, dealer_hand)

    round_count += 1

print("\nFinal Performance Statistics:")
print(f"Total Rounds Played: {round_count}")
print(f"Wins: {game_stats['wins']}")
print(f"Losses: {game_stats['losses']}")
print(f"Final Chip Count: {player.chips}")
print(f"Average Bet Size: {game_stats['total_bets'] / max(round_count, 1):.2f}")
