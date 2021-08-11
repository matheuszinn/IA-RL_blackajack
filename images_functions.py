import pygame
import constants
import os
from typing import List


def shrink_image(image: pygame.Surface) -> pygame.Surface:
    width, height = image.get_size()
    return pygame.transform.scale(image, (width // constants.IMG_SIZE, height // constants.IMG_SIZE))


def load_card_images() -> List[pygame.Surface]:
    loaded_images = [pygame.image.load(constants.CARDS_FOLDER + path)
                     for path in os.listdir(constants.CARDS_FOLDER)]

    rescaled_images = [shrink_image(img) for img in loaded_images]
    return rescaled_images


def load_blank_card() -> pygame.Surface:
    return shrink_image(pygame.image.load('assets/BlankCard.png'))
