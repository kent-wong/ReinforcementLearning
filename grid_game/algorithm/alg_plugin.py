import random

class ActionSpace():
	"""A class that describes all the actions can an agent can take in a particular environment"""

	def __init__(self, action_list):
		"""
		parameters
			action_list:  a whole list of actions for this action space
		"""
		self._action_list = action_list.copy()
		self._n_actions = len(self._action_list)

	def random_sample(self):
		"""Uniform randomly return an action"""
		return random.choice(self._action_list)

	def action_at(self, index):
		if index < self.n_actions:
			return self._action_list[index]
		else:
			return None

	def action_index(self, action):
		return self._action_list.index(action)	
		
	@property
	def action_list(self):
		"""return action list for read"""
		return self._action_list

	@property
	def action_dict(self):
		"""return action dictionary, key is action, value is the action list index"""
		actions = {v:i for i, v in enumerate(self._action_list)}
		return actions

	@property
	def n_actions(self):
		return self._n_actions
		
		
class AlgPlugin():
	def __init__(self):
		pass

	def layout(self, n_features, action_space, preset_states_list):
		"""Environment uses this function to notify its layout.
		The 'preset_states_list' is a list of tuple of form like: '(state, preset_value, is_terminal)'"""

		print("layout() is called, with arguments:", n_features, action_space, preset_states_list)
	
	def episode_start(self, episode, starting_state):
		print("episode_start() is called, with arguments:", episode, starting_state)

	def one_step(self, state, action, reward, state_next, is_terminal):
		print("one_step() is called, with arguments:", state, action, reward, state_next, is_terminal)

	def episode_end(self):
		print("episode_end() is called")

	def next_action(self, state):
		print("next_action() is called, with arguments:", state)

	def best_action(self, state):
		print("best_action() is called, with arguments:", state)

	def get_action_values(self, state):
		print("get_action_values() is called, with arguments:", state)


if __name__ == "__main__":
	a = ActionSpace(['N', 'S', 'W', 'E', 'C'])
	for _ in range(5):
		print(a.random_sample())

	print(a.action_list)

