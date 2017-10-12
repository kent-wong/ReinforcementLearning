import random

class ActionSpace():
	def __init__(self, actions):
		self.actions_list = list(actions).copy()
		self.n_actions = len(self.actions_list)

	def random_sample(self):
		return random.choice(self.actions_list)

	def all_actions(self):
		return self.actions_list.copy()
		
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

	def get_text_to_display(self, state):
		print("get_text_to_display() is called, with arguments:", state)


if __name__ == "__main__":
	a = ActionSpace(range(5))
	for _ in range(5):
		print(a.random_sample())

	print(a.all_actions())

