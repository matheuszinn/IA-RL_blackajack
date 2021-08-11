from typing import Tuple, Optional
import pygame


class Card(pygame.sprite.Sprite):

    def __init__(self, card_idx: int, img: pygame.Surface, display: pygame.Surface) -> None:
        super().__init__()
        self.val = card_idx if card_idx <= 9 else 10
        self.img = img
        self.display = display

    def draw(self, pos: Tuple[int, int], hidden_img: Optional[pygame.Surface] = None, hidden: bool = False) -> None:
        if hidden and hidden_img is not None:
            self.display.blit(hidden_img, pos)
        else:
            self.display.blit(self.img, pos)

    def __repr__(self) -> str:
        return f'Value: {self.val}'
