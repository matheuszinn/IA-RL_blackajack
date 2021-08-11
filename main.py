from game import Game

alpha = 0.60
gamma = 0.75
epsilon = 0.01

results = Game(alpha=alpha, gamma=gamma, epsilon=epsilon).run(
    epochs=10, episodes=100)

with open(f'results_a{alpha}_{gamma}.md', 'w') as file:
    file.write(''.join(results))
