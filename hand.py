import random
import pygame

from typing import List

from card import Card
from constants import Colors
from images_functions import load_blank_card


class Hand(pygame.sprite.Sprite):

    def __init__(self,
                 loaded_images: List[pygame.Surface],
                 display: pygame.Surface,
                 font: pygame.font.Font,
                 is_dealer: bool = False,
                 *groups: pygame.sprite.AbstractGroup) -> None:
        super().__init__(*groups)
        self.loaded_images: List[pygame.Surface] = loaded_images
        self.main_surface: pygame.Surface = display
        self.cards: List[Card] = []
        self.card_values: List[int] = []
        self.font: pygame.font = font
        self.is_dealer: bool = is_dealer
        self.is_hidden: bool = is_dealer

        if is_dealer:
            self.blank_card = load_blank_card()

        self.generate_hand()

    def __show_card(self, card_pos: List[int]) -> None:

        img_width, img_height = self.cards[0].img.get_size()

        for i in range(len(self.cards)):
            self.cards[i].draw(
                (card_pos[0] + (i * (img_width + 5)), card_pos[1]))

        if self.is_dealer:
            self.main_surface.blit(
                self.font.render(
                    f"Dealer's hand: {self.sum_hand()}, {'with a usable ace' if self.usable_ace() else 'with no usable ace.'}",
                    True,
                    Colors.WHITE,
                ),
                (card_pos[0], card_pos[1] + img_height + 10),
            )
        else:
            self.main_surface.blit(
                self.font.render(
                    f"Player's value: {self.sum_hand()}, {'with an usable ace' if self.usable_ace() else 'with no usable ace.'}",
                    True,
                    Colors.WHITE,
                ),
                (card_pos[0], card_pos[1] + img_height + 10),
            )

    def draw(self, card_pos: List[int]) -> None:

        img_width, img_height = self.cards[0].img.get_size()

        if self.is_dealer:

            if self.is_hidden:
                self.cards[0].draw((card_pos[0], card_pos[1]))
                self.cards[1].draw(
                    (card_pos[0] + (img_width + 5), card_pos[1]),
                    hidden_img=self.blank_card,
                    hidden=self.is_hidden
                )

                self.main_surface.blit(
                    self.font.render(
                        f"Dealer's hand: {self.cards[0]}",
                        True,
                        Colors.WHITE,
                    ),
                    (card_pos[0], card_pos[1] + img_height + 10),
                )
            else:
                self.__show_card(card_pos)
        else:
            self.__show_card(card_pos)

    def unhide_dealer(self) -> None:
        if hasattr(self, 'is_hidden'):
            self.is_hidden = not self.is_hidden

    def generate_hand(self) -> None:
        self.cards: List[Card] = [self.pick_card(), self.pick_card()]
        self.card_values: List[int] = [c_val.val for c_val in self.cards]

        self.is_hidden = True

    def pick_card(self) -> Card:
        pick = random.choice(self.loaded_images)
        img_idx = self.loaded_images.index(pick)
        return Card(img_idx + 1, pick, self.main_surface)

    def add_card_to_hand(self, card=None) -> None:
        self.cards.append(self.pick_card() if card is None else card)
        self.card_values: List[int] = [c_val.val for c_val in self.cards]

    def usable_ace(self) -> bool:
        return 1 in self.card_values and sum(self.card_values) + 10 <= 21

    def sum_hand(self) -> int:
        if self.usable_ace():
            return sum(self.card_values) + 10

        return sum(self.card_values)

    def is_natural(self) -> bool:
        return len(self.cards) == 2 and self.sum_hand() == 21
