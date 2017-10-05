
class EnvPlugin():
	def __init__(self):
		pass

	def layout(self, grid_dimension, n_actions):
		pass
	
	def set_value(self, state, value, is_terminal):
		pass

	def get_text_to_display(self, state):
		pass

	def episode_started(self, starting_state):
		pass

	def walked_one_step(self, state, action, reward, state_next, is_terminal):
		pass

	def episode_ended(self):
		pass

	def next_action(self, state):
		pass
