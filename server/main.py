from server.dog import Dog

if __name__ == "__main__":
    game = Dog()
    print("Initial State:", game.get_state())

    # Test resetting the game
    game.reset()
    print("After Reset:", game.get_state())

