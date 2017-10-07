import tkinter as tk
import time
import random
import sys

from grid import Grid
from drawing import DrawingManager

class Env():
	# actions
	N = 0
	S = 1
	W = 2
	E = 3
	N_ACTIONS = 4

	# agent
	AGENT_LOC = (0, 0)

	class CellData():
		def __init__(self, cell_id, reward=0, preset_value=None, is_terminal=False):
			self.cell_id = cell_id	# unique Id
			self.reward = reward	# the reward given when an agent accessing this block
			self.preset_value = preset_value
			self.is_terminal = is_terminal

	def __init__(self, grid_dimension=(10, 10), cell_size=(80, 80), default_rewards=0):
		# initialize agent info
		self.agent_location = Env.AGENT_LOC
		self.agent_orientation = Env.E

		# create grid and add data to it
		self.grid = Grid(grid_dimension)
		for cell_id in range(self.grid.n_cells):
			data = Env.CellData(cell_id, reward=default_rewards)
			self.grid.all_cells().append(data)

		# create a drawing manager, which creates a tkinter window in a new thread
		self.drawing_manager = DrawingManager(grid_dimension, cell_size).wait()
		# draw grid
		self.drawing_manager.draw_grid()

		self.reset()

	def train(self, plugin, n_episodes, delay_per_step=0, dont_show_steps=False):
		assert plugin != None
		assert n_episodes > 0

		preset_states = []
		for cell in self.grid.all_cells():
			if cell.preset_value != None:
				preset_states.append((cell.cell_id, cell.preset_value, cell.is_terminal))

		# notify plugin environment layout and query plugin to show some info
		plugin.layout(self.grid.n_cells, Env.N_ACTIONS, preset_states)
		for cell_id in range(self.grid.n_cells):
			text = plugin.get_text_to_display(cell_id)
			self.show_text(cell_id, text)

		for episode in range(n_episodes):
			self.reset()  # reset agent's location
			time.sleep(delay_per_step)

			print("training episode {} ...".format(episode))
			state_next = self.grid.insure_id(self.agent_location)  # starting state
			plugin.episode_start(episode, state_next)

			is_terminal = False
			while is_terminal == False:
				action = plugin.next_action(state_next)  # query plugin for next action

				# tell environment what action to move
				state, action, reward, state_next, is_terminal = self.step(action)
				time.sleep(delay_per_step)

				# notify plugin this step
				plugin.one_step(state, action, reward, state_next, is_terminal)

				# try to show some info on grid, the info to show is decided by plugin
				text = plugin.get_text_to_display(state)
				self.show_text(state, text)

			plugin.episode_end()

	def test(self, plugin, n_episodes=1, delay_per_step=0.5, only_exploitation=True):
		assert plugin != None
		assert n_episodes > 0

		if only_exploitation == True:
			query_function = plugin.best_action
		else:
			query_function = plugin.next_action

		for episode in range(n_episodes):
			self.reset()  # reset agent's location
			time.sleep(delay_per_step)
		
			state_next = self.grid.insure_id(self.agent_location)  # starting state
			is_terminal = False
			while is_terminal == False:
				action = query_function(state_next)
				state, action, reward, state_next, is_terminal = self.step(action)
				time.sleep(delay_per_step)

	def add_object(self, index_or_id, value, reward=0, is_terminal=False):
		cell_id = self.grid.insure_id(index_or_id)
		cell = Env.CellData(cell_id, reward, value, is_terminal)
		self.grid.set_cell(cell_id, cell)

		if is_terminal == True:
			image = self.drawing_manager.IMAGE_RED_CIRCLE
		elif value >= 0:
			image = self.drawing_manager.IMAGE_YELLOW_STAR
		else:
			image = self.drawing_manager.IMAGE_BLACK_BOX

		self.drawing_manager.draw_on_cell(index_or_id, image)

	def show_text(self, index_or_id, text):
		if text == None:
			return

		if isinstance(text, (list, tuple)) == True:
			text_list = []
			for action, word in enumerate(text):
				if action == Env.N:
					action = tk.N
				elif action == Env.S:
					action = tk.S
				elif action == Env.W:
					action = tk.W
				elif action == Env.E:
					action = tk.E
				else:
					assert False

				text_list.append((word, action))
			self.drawing_manager.draw_text_list(index_or_id, text_list)
		else:	
			self.drawing_manager.draw_on_cell(index_or_id, text=text)
		
	def angle_from_orientation(self, ori):
		angle = 0

		if Env.N == ori:
			angle = 90
		elif Env.S == ori:
			angle = 270
		elif Env.W == ori:
			angle = 180

		return angle

	def reset(self):
		self.agent_location = Env.AGENT_LOC
		self.agent_orientation = Env.E

		self.drawing_manager.remove_agent()
		angle = self.angle_from_orientation(self.agent_orientation)
		self.drawing_manager.draw_agent(self.agent_location, angle)

		# delete previous traces so we don't mess up the environment
		self.drawing_manager.delete_trace()
		
	def step(self, action):
		index = self.agent_location
		index_new = list(index)

		if action == Env.N:
			index_new[0] -= 1
		elif action == Env.S:
			index_new[0] += 1
		elif action == Env.W:
			index_new[1] -= 1
		elif action == Env.E: 
			index_new[1] += 1
		else:
			assert False

		# check boundary condition
		if index_new[0] < 0 or index_new[0] >= self.grid.dimension[0]:
			index_new = index
		elif index_new[1] < 0 or index_new[1] >= self.grid.dimension[1]:
			index_new = index

		angle = self.angle_from_orientation(action)
		# rotate agent if its orientation changed, even if it's not moving
		if self.agent_orientation != action:
			self.drawing_manager.rotate_agent(index, angle)
			self.agent_orientation = action

		# move agent to its new location
		if index_new != index:
			self.drawing_manager.move_agent(index, index_new)
			self.agent_location = index_new
			self.drawing_manager.draw_trace(index, angle)

		cell = self.grid.cell(index)
		cell_next = self.grid.cell(index_new)

		return (cell.cell_id, action, cell.reward, cell_next.cell_id, cell_next.is_terminal)

	def walk_by_orders(self, action_list):
		self.reset()
		for action in action_list:
			self.step(action)

	# setup the layout of environment
	# you can experiment algorithms by changing this 'layout'
	def set_layout(self):
		self.add_object((6, 6), value=100)
		self.add_object((8, 8), value=10)
		self.add_object((6, 7), value=10)


if __name__ == '__main__':
	# import algorithms
	sys.path.append('./algorithm')
	from alg_plugin import AlgPlugin
	from q_learning import QLearning

	# set the environment
	env = Env((10, 10), (120, 90))
	env.add_object((6, 6), value=200, is_terminal=True)
	env.add_object((6, 4), value=100, is_terminal=True)
	env.add_object((3, 3), value=-100, is_terminal=True)

	# test for q-learning algorithm
	# hyperparameters
	alpha = 0.1
	gamma = 0.99
	epsilon = 0.7
	n_episodes = 5000

	plugin = QLearning(alpha, gamma, epsilon)
	env.train(plugin, n_episodes, delay_per_step=0)
	env.test(plugin)


	print("end...")
