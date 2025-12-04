import random
import pickle
from collections import defaultdict

class QLearningAgent:
    def __init__(self, states, actions, alpha=0.6, gamma=0.9, epsilon=0.2):
        self.states = states
        self.actions = actions
        self.Q = defaultdict(lambda: {a: 0.0 for a in self.actions})
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def choose_action(self, state):
        _ = self.Q[state]
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        qvals = self.Q[state]
        max_val = max(qvals.values())
        best_actions = [a for a, v in qvals.items() if v == max_val]
        return random.choice(best_actions)

    def update(self, state, action, reward, next_state):
        _ = self.Q[state]
        _ = self.Q[next_state]
        q_sa = self.Q[state][action]
        max_next = max(self.Q[next_state].values()) if self.Q[next_state] else 0.0
        self.Q[state][action] = q_sa + self.alpha * (reward + self.gamma * max_next - q_sa)

    def save(self, filepath):
        with open(filepath, "wb") as f:
            pickle.dump(dict(self.Q), f)

    def load(self, filepath):
        try:
            with open(filepath, "rb") as f:
                qdict = pickle.load(f)
            self.Q = defaultdict(lambda: {a: 0.0 for a in self.actions}, qdict)
        except FileNotFoundError:
            print("⚠️ No previous Q-table found. Starting fresh.")