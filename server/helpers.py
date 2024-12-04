import random

def reshuffle_cards(draw_pile, discard_pile):
    """Shuffle discard pile into the draw pile."""
    draw_pile.extend(discard_pile)
    discard_pile.clear()
    random.shuffle(draw_pile)

