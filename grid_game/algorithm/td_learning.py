import numpy as np

from td import TD
from alg_plugin import AlgPlugin
import common

class TDLearning(AlgPlugin):
	def __init__(self, alpha, gamma, eligibility, epsilon, next_action_considered):
		super().__init__()

		# store the hyper parameters
		self.alpha = alpha
		self.gamma = gamma
		self.eligibility = eligibility
		self.epsilon = epsilon
		self.next_action_considered = next_action_considered

		# use 'epsilon greedy' to chose action while agent is in a state
		self.action_selection = common.epsilon_greedy

		# use TD class to do the actual algorithm
		self.td = TD(alpha, gamma, eligibility, self.value_callback, self.update_callback)

		# filled in when we know environment layout
		self.n_features = None
		self.action_space = None

		# underlying storage for store value per action per state
		# it's called 'q-table' just for convention, actually it can be used for any TD learning
		# as long as the environment has finite number of states
		self.qtable = {}  

	def value_callback(self, state, action):
		"""TD algorithm call this function to query action-value of a state"""

		#print("value_callback(): state: {}, action: {}".format(state, action))

		if action == None:
			return np.max(self.qtable[state])
		else:
			return self.qtable[state][action]

	def update_callback(self, state, action, delta):
		"""TD algorithm call this function to update action-value of a state"""

		#print("update_callback(): state: {}, action: {}, delta: {}".format(state, action, delta))
		self.qtable[state][action] += delta

	##############################################################
	#                                                            #
	#    Below is the implementation of 'AlgPlugin' interface    #
	#                                                            #
	##############################################################
	def layout(self, n_features, action_space, preset_states_list):
		self.n_features = n_features
		self.action_space = action_space
		self.qtable = {}

		for (state, value, is_terminal) in preset_states_list:
			self.qtable[state] = [value] * self.action_space.n_actions

	def episode_start(self, episode, state):
		#super().episode_start(episode, state)
		if self.qtable.get(state) == None:
			self.qtable[state] = [0] * self.action_space.n_actions
		self.td.episode_start(state)
		return self.next_action(state)

	def one_step(self, state, action, reward, state_next):
		if self.qtable.get(state) == None:
			self.qtable[state] = [0] * self.action_space.n_actions

		if self.qtable.get(state_next) == None:
			self.qtable[state_next] = [0] * self.action_space.n_actions

		next_action_index = self._next_action_index(state_next)
		if self.next_action_considered == True:
			use_this_action = next_action_index
		else:
			use_this_action = None

		# need to translate from action to action_index, underlying TD algorithm
		# assume that actions are non-negative integer
		action_index = self.action_space.action_index(action)

		self.td.step(state, action_index, reward, state_next, use_this_action)
		return self.action_space.action_at(next_action_index)

	def episode_end(self):
		self.td.episode_end()

	def _next_action_index(self, state):
		return self.action_selection(self.epsilon, self.qtable[state])

	def next_action(self, state):
		"""Given the current state, based on selection algorithm select next action for agent"""
		action_index = self._next_action_index(state)
		return self.action_space.action_at(action_index)

	def best_action(self, state):
		"""Select the action that has max value in a given state"""
		action_index = np.argmax(self.qtable[state])
		return self.action_space.action_at(action_index)

	def get_action_values(self, state):
		return self.qtable.get(state)

	def get_action_values_dict(self, state):
		action_values = self.qtable.get(state)
		if action_values == None:
			return None
		else:
			action_values_dict = {self.action_space.action_at(i):v for i, v in enumerate(action_values)}
			return action_values_dict

	def whole_episode(self, one_episode):
		self.episode_start(one_episode[0][0])
		for state, action, reward, state_next in one_episode:
			self.step(state, action, reward, state_next)
		self.episode_end()

if __name__ == '__main__':
	state_action = [2, 4, 6, 8]
	a = common.epsilon_greedy(0.8, state_action)
	print(a)
