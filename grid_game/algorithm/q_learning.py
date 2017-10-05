from td import TD
import numpy as np

class QLearning():
	class StateRecord():
		def __init__(self, reward, action_values):
			self.reward = reward
			self.action_values = action_values

	def __init__(self, alpha, gamma, epsilon, n_actions):
		self.n_actions = n_actions
		self.qtable = {}

		# this Q-leaning class is actually TD(0) and off-policy
		self.td0 = TD(alpha, gamma, 0, self.value_callback, self.update_callback)

		def argmax_multi(data):
			assert len(data) > 0

			max = data[0]
			indexes = []
			for i, v in enumerate(data):
				if v > max:
					max = v
					indexes = [i]
				elif v == max:
					indexes.append(i)
				
			return indexes

		def index_sub(a, b):
			a = set(a)
			b = set(b)

			return list(a - b)

		def epsilon_greedy(action_values):
			count = len(action_values)
			assert count >= 1
			if count == 1:
				return 0

			indexes = argmax_multi(action_values)
			if np.random.random() > epsilon and len(indexes) < count:
				indexes = index_sub(range(count), indexes)

			return np.random.choice(indexes)

		self.action_selection_func = epsilon_greedy

	#def initialize(self, state, reward, action_values=None, is_terminal=False):
	#	if action_values == None:
	#		action_values = [0] * self.n_actions
	#	if is_terminal == True:
	#		action_values = [reward] * self.n_actions
	#		
	#	record = QLearning.StateRecord(reward, action_values)
	#	self.qtable[state] = record
		
	def value_callback(self, state, action):
		#print("value_callback(): state: {}, action: {}".format(state, action))
		if action == None:
			return np.max(self.qtable[state])
		else:
			return self.qtable[state][action]

	def update_callback(self, state, action, delta):
		#print("update_callback(): state: {}, action: {}, delta: {}".format(state, action, delta))
		self.qtable[state][action] += delta

	def action_values(self, state):
		return self.qtable[state]

	def dump(self):
		for state, record in self.qtable.items():
			print(str(state)+"\t", end='')
			for value in record:
				print(str(float(value)) + '  ', end='')
			print("")

	def next_action(self, state):
		return self.action_selection_func(self.qtable[state])

	def best_action(self, state):
		return np.argmax(self.qtable[state])

	def episode_start(self, state):
		if self.qtable.get(state) == None:
			self.qtable[state] = [0] * self.n_actions
		self.td0.episode_start(state)
		return self.next_action(state)

	def step(self, state, action, reward, state_next):
		if self.qtable.get(state_next) == None:
			self.qtable[state_next] = [0] * self.n_actions
		self.td0.step(state, action, reward, state_next, None)
		return self.next_action(state_next)

	def episode_end(self):
		self.td0.episode_end()

	def set_terminal(self, state, value):
		self.qtable[state] = [value] * self.n_actions
		
	def whole_episode(self, one_episode_record):
		self.episode_start(one_episode_record[0][0])
		for state, action, reward, state_next in one_episode_record:
			self.step(state, action, reward, state_next)

		self.episode_end()


if __name__ == '__main__':
	qlearning = QLearning(0.1, 0.99, 0.9, 4)
	for i in range(20):
		next_action = qlearning.episode_start(i)
		print("next action: ", next_action)
