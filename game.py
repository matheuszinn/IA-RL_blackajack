from typing import List

import pygame

from hand import Hand
from images_functions import load_card_images
from constants import GameState, Colors

import numpy as np
import random

from constants import Action


class Q:
    def __init__(self,
                 alpha: float = 0.1,
                 gamma: float = 0.6,
                 epsilon: float = 0.01):

        self.q_table = np.zeros((18, 2), dtype=int)

        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

        self.state = 0

    def choose_action(self, state) -> Action:
        if random.uniform(0, 1) < self.epsilon:
            return Action.HIT if random.randint(0, 1) else Action.STOP
        else:
            return Action.HIT if np.argmax(self.q_table[state]) else Action.STOP


class Game:
    def __init__(self,
                 alpha: float = 0.3,
                 gamma: float = 0.15,
                 epsilon: float = 0.01) -> None:
        pygame.init()
        pygame.font.init()

        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.canvas: pygame.Surface = pygame.display.set_mode((1000, 600))
        pygame.display.set_caption('Vinte e um')

        self.loaded_images: List[pygame.Surface] = load_card_images()
        self.font: pygame.font.Font = pygame.font.Font('assets/Early GameBoy.ttf', 16)
        self.bigger_font: pygame.font.Font = pygame.font.Font('assets/Early GameBoy.ttf', 40)

        self.bg = pygame.image.load('assets/background.png').convert()

        self.dealer: Hand = Hand(self.loaded_images, self.canvas, self.font, is_dealer=True)
        self.player: Hand = Hand(self.loaded_images, self.canvas, self.font)

        self.game_state: GameState = GameState.PLAYER_TURN

        self.q = Q(alpha=alpha, gamma=gamma, epsilon=epsilon)

        self.restart_start_time = None
        self.draw_dealer_card = None
        self.draw_player_card = None

        self.episode_number = 0
        self.wins = 0
        self.loses = 0
        self.ties = 0

        self.wins_loses_epoch = []

        self.q.state = self.player.sum_hand()

        self.epochs_number = 0

    def draw(self) -> None:
        self.canvas.fill((0, 0, 0))

        self.canvas.blit(self.bg, [0, 0])

        self.dealer.draw([50, 25])
        self.player.draw([50, 400])

        self.canvas.blit(self.font.render(f'wins: {self.wins}', True, Colors.WHITE), (700, 25))
        self.canvas.blit(self.font.render(f'loses: {self.loses}', True, Colors.WHITE), (700, 50))
        self.canvas.blit(self.font.render(f'ties: {self.ties}', True, Colors.WHITE), (700, 75))

        text_pos = (50, 290)

        for i in range(self.q.q_table.shape[0]):
            self.canvas.blit(
                self.font.render(f"{str(i + 4).center(3)}  {self.q.q_table[i][0]}\t{self.q.q_table[i][1]}", True,
                                 Colors.WHITE),
                (700, 130 + (i * 25))
            )
            pygame.draw.line(self.canvas, Colors.WHITE, (700, 127 + (i * 25)), (980, 127 + (i * 25)), 3)

        pygame.draw.line(self.canvas, Colors.WHITE, (741, 127), (741, 575), 3)

        self.canvas.blit(self.font.render(f'Episode: {self.episode_number}', True, Colors.WHITE),
                         (text_pos[0], text_pos[1] - 13))
        self.canvas.blit(self.font.render(f'Epoch: {self.epochs_number}', True, Colors.WHITE),
                         (text_pos[0], text_pos[1] - 30))

        if self.game_state == GameState.PLAYER_TURN:
            self.canvas.blit(
                self.bigger_font.render("Player turn", True, Colors.WHITE),
                text_pos
            )
        elif self.game_state == GameState.DEALER_TURN:
            self.canvas.blit(
                self.bigger_font.render("Dealer turn", True, Colors.WHITE),
                text_pos
            )
        elif self.game_state == GameState.PLAYER_WON:
            self.canvas.blit(
                self.bigger_font.render("Player won!!!", True, Colors.GREEN),
                text_pos
            )
        elif self.game_state == GameState.PLAYER_LOSE:
            self.canvas.blit(
                self.bigger_font.render("Player lose...", True, Colors.RED),
                text_pos
            )
        elif self.game_state == GameState.GAME_TIED:
            self.canvas.blit(
                self.bigger_font.render("Game tied.", True, Colors.WHITE),
                text_pos
            )

    def change_turn(self) -> None:
        if self.game_state == GameState.PLAYER_TURN:
            self.game_state = GameState.DEALER_TURN
        else:
            self.game_state = GameState.PLAYER_TURN

    def new_episode(self) -> None:
        self.player.generate_hand()
        self.dealer.generate_hand()

        if self.game_state == GameState.PLAYER_WON:
            self.wins += 1
        elif self.game_state == GameState.PLAYER_LOSE:
            self.loses += 1
        elif self.game_state == GameState.GAME_TIED:
            self.ties += 1

        self.game_state = GameState.PLAYER_TURN
        self.episode_number += 1
        self.q.state = self.player.sum_hand()

    def add_reward(self, state, action, reward, new_state=None):

        if new_state is None:
            self.q.q_table[state][action] = self.q.q_table[state][action] + self.q.alpha * (
                    reward - self.q.q_table[state][action])
        else:
            self.q.q_table[state][action] = self.q.q_table[state][action] + self.q.alpha * (
                    reward + self.q.gamma * (np.max(self.q.q_table[new_state])) - self.q.q_table[state][action])

    def next_state(self, state, action):
        if action == Action.HIT:
            card = self.player.pick_card()
            if card.val + self.player.sum_hand() <= 21:
                self.add_reward(state - 4, action, 1000, new_state=(card.val + self.player.sum_hand()) - 4)
                self.player.add_card_to_hand(card=card)
                self.q.state = self.player.sum_hand()
            elif card.val + self.player.sum_hand() > 21:
                self.game_state = GameState.PLAYER_LOSE
                self.add_reward(state - 4, action, -1000 * abs(21 - card.val + self.player.sum_hand()))
        else:
            self.change_turn()

    def new_epoch(self) -> None:
        self.game_state: GameState = GameState.PLAYER_TURN

        self.q = Q(alpha=0.3, gamma=0.15, epsilon=0.01)

        self.restart_start_time = None
        self.draw_dealer_card = None
        self.draw_player_card = None

        self.episode_number = 0
        self.wins = 0
        self.loses = 0
        self.ties = 0

        self.q.state = self.player.sum_hand()
        self.epochs_number += 1

    def run(self, epochs: int = 10, episodes: int = 100) -> List[str]:
        action = None

        results = [f'#### alpha: {self.q.alpha}\n#### gamma: {self.q.gamma}\n#### randomness: {self.q.epsilon}\n\n\n']

        while True:

            if self.episode_number == episodes:
                results.append(
                    f"## Epoch {self.epochs_number + 1}\n- ### win: {self.wins}\n- ### lose: {self.loses}\n- ### tie: {self.ties}\n- ### win/tie: {self.ties + self.wins}\n")
                self.wins_loses_epoch.append(self.ties + self.wins)

                self.new_epoch()
            elif self.epochs_number == epochs:
                results.append(
                    f"\n# Mean Wins/Ties per Epoch = {sum(self.wins_loses_epoch) / len(self.wins_loses_epoch)}")

                return results

            self.clock.tick(60)

            self.draw()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        quit()

            # Player turn
            if self.game_state == GameState.PLAYER_TURN:

                action = self.q.choose_action(self.q.state - 4)

                if self.draw_player_card is None:
                    self.draw_player_card = pygame.time.get_ticks()
                else:
                    dt = (pygame.time.get_ticks() - self.draw_player_card) / 1000

                    if dt > 0.5:
                        self.next_state(self.q.state, action)
                        self.draw_player_card = None

            # Dealer turn
            if self.game_state == GameState.DEALER_TURN:

                if self.dealer.is_hidden:
                    self.dealer.unhide_dealer()

                if self.dealer.sum_hand() < 17:
                    if self.draw_dealer_card is None:
                        self.draw_dealer_card = pygame.time.get_ticks()
                    else:
                        dt = (pygame.time.get_ticks() - self.draw_dealer_card) / 1000

                        if dt > 0.5:
                            self.dealer.add_card_to_hand()
                            self.draw_dealer_card = None
                elif self.dealer.sum_hand() > 21:
                    self.game_state = GameState.PLAYER_WON
                elif self.dealer.sum_hand() == self.player.sum_hand():
                    self.game_state = GameState.GAME_TIED
                else:
                    scores = [self.player.sum_hand(), self.dealer.sum_hand()]
                    winner = scores.index(max(scores))

                    if not winner:
                        self.game_state = GameState.PLAYER_WON
                    else:
                        self.game_state = GameState.PLAYER_LOSE

            if self.game_state in [GameState.PLAYER_WON, GameState.PLAYER_LOSE, GameState.GAME_TIED]:

                if self.restart_start_time is None:
                    self.restart_start_time = pygame.time.get_ticks()
                else:
                    elapsed_time = (pygame.time.get_ticks() - self.restart_start_time) / 1000

                    if elapsed_time > 1:
                        if self.game_state == GameState.GAME_TIED or self.game_state == GameState.PLAYER_WON:
                            self.add_reward(self.q.state - 4, action, 1000)
                        elif self.game_state == GameState.PLAYER_LOSE and self.player.sum_hand() < 21:
                            self.add_reward(self.q.state - 4, action, -1000 * abs(21 - self.player.sum_hand()))
                        self.new_episode()
                        self.restart_start_time = None

            pygame.display.update()
