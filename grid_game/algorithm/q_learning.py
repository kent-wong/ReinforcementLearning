import numpy as np

from td import TD
from alg_plugin import AlgPlugin

class QLearning(AlgPlugin):
	class StateRecord():
		def __init__(self, reward, action_values):
			self.reward = reward
			self.action_values = action_values

	def __init__(self, alpha, gamma, epsilon):
		super().__init__()

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

	def value_callback(self, state, action):
		#print("value_callback(): state: {}, action: {}".format(state, action))
		if action == None:
			return np.max(self.qtable[state])
		else:
			return self.qtable[state][action]

	def update_callback(self, state, action, delta):
		print("update_callback(): state: {}, action: {}, delta: {}".format(state, action, delta))
		self.qtable[state][action] += delta

	####################################################
	#                                                  #
	#    Below is the implementation of EnvPlugin      #
	#                                                  #
	####################################################
	def layout(self, n_states, n_actions, preset_states_list):
		self.n_state = n_states
		self.n_actions = n_actions
		self.qtable = {}

		for (state, value, is_terminal) in preset_states_list:
			self.qtable[state] = [value] * self.n_actions

	def episode_start(self, episode, state):
		super().episode_start(episode, state)
		if self.qtable.get(state) == None:
			self.qtable[state] = [0] * self.n_actions
		self.td0.episode_start(state)
		return self.next_action(state)

	def one_step(self, state, action, reward, state_next, is_terminal):
		if self.qtable.get(state_next) == None:
			self.qtable[state_next] = [0] * self.n_actions
		self.td0.step(state, action, reward, state_next, None)
		return self.next_action(state_next)

	def episode_end(self):
		self.td0.episode_end()

	def next_action(self, state):
		return self.action_selection_func(self.qtable[state])

	def best_action(self, state):
		return np.argmax(self.qtable[state])

	def get_text_to_display(self, state):
		action_values = self.qtable.get(state)
		if action_values == None:
			return None

		max_value = np.max(self.qtable[state])
		max_value = round(max_value, 2)
		text = str(max_value)
		return text

	def action_values(self, state):
		return self.qtable.get(state)

	def dump(self):
		for state, record in self.qtable.items():
			print(str(state)+"\t", end='')
			for value in record:
				print(str(float(value)) + '  ', end='')
			print("")

	#def set_state_value(self, state, value):
	#	self.qtable[state] = [value] * self.n_actions
		
	def whole_episode(self, one_episode_record):
		self.episode_start(one_episode_record[0][0])
		for state, action, reward, state_next in one_episode_record:
			self.step(state, action, reward, state_next)

		self.episode_end()


if __name__ == '__main__':
	qlearning = QLearning(0.1, 0.99, 0.9)
