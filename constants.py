from enum import Enum, auto, IntEnum

CARDS_FOLDER = r'./assets/cards/'
NUMBER_OF_CARDS = 52

IMG_SIZE = 6


class Action(IntEnum):
    STOP = 0
    HIT = 1


class GameState(Enum):
    PLAYER_TURN = auto()
    DEALER_TURN = auto()
    PLAYER_WON = auto()
    PLAYER_LOSE = auto()
    GAME_TIED = auto()


class Colors:
    WHITE = (255, 255, 255)
    BLACK = (255, 255, 255)
    GOLD = (255, 215, 0)
    GREEN = (20, 255, 0)
    RED = (255, 0, 0)
