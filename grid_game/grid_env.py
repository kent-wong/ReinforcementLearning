import tkinter as tk
import time
import random
import sys

from grid import Grid
from drawing import DrawingManager
sys.path.append('./algorithm')
from alg_plugin import ActionSpace


class Agent():
	pass

class GridObject():
	"""A class represents an object(image or text) that resides inside a grid cell"""

	def __init__(self, obj_type, index_or_id, drawing_manager=None, data=None):
		self.obj_type = obj_type
		self.index_or_id = index_or_id
		self.drawing_manager = drawing_manager
		self.data = data  # any type of data can be attached here

	def draw(self):
		if self.drawing_manager != None:
			return self.drawing_manager.draw_object(self.obj_type, self.index_or_id)

	def remove(self):
		if self.drawing_manager != None:
			return self.drawing_manager.delete_object(self.obj_type, self.index_or_id)

	def is_on_cell(self):
		if self.drawing_manager != None:
			return self.drawing_manager.is_object_on_cell(self.obj_type, self.index_or_id)
		
	def has_data(self):
		return self.data != None

class Env():
	# actions
	N = 0
	S = 1
	W = 2
	E = 3
	N_ACTIONS = 4

	# agent
	AGENT_LOC = (0, 0)

	# object type, each grid cell can be placed at most one object on it.
	OBJ_TYPE_TERM = -1  # this object is terminal, an agent stepped on this object will be in a terminal state
	OBJ_TYPE_NONE = 0
	OBJ_TYPE_PICKABLE = 1  # agent can pick this object

#	class CellData():
#		def __init__(self, cell_id, reward=0, preset_value=None, is_terminal=False):
#			self.cell_id = cell_id	# unique Id
#			self.reward = reward	# the reward given when an agent accessing this block
#			self.preset_value = preset_value
#			self.is_terminal = is_terminal

	def __init__(self, grid_dimension=(10, 10), cell_size=(120, 90), default_rewards=0):
		# initialize agent info
		self.default_agent_location = Env.AGENT_LOC
		self.default_agent_orientation = Env.E
		self.agent_location = Env.AGENT_LOC
		self.agent_orientation = Env.E

		# create grid and add data to it
		self.grid = Grid(grid_dimension)
		for cell_id in range(self.grid.n_cells):
			self.grid.all_cells().append(None)

		# create a drawing manager, which creates a tkinter window in a new thread
		self.drawing_manager = DrawingManager(grid_dimension, cell_size).wait()
		# draw grid
		self.drawing_manager.draw_grid()

		self.reset()
		self.default_rewards = default_rewards

	def train(self, plugin, n_episodes, delay_per_step=0, show=True):
		assert plugin != None
		assert n_episodes > 0

		preset_states = []
		for obj in self.grid.all_cells():
			if obj != None and obj.data[2] != 0:
				preset_states.append((obj.data[0], obj.data[2], obj.data[3]))

		action_space = ActionSpace(range(Env.N_ACTIONS))
		# notify plugin environment layout and query plugin to show some info
		plugin.layout(1, action_space, preset_states)
		for cell_id in range(self.grid.n_cells):
			text = plugin.get_text_to_display(cell_id)
			self.show_text(cell_id, text)

		for episode in range(n_episodes):
			self.reset(show)  # reset agent's location
			time.sleep(delay_per_step)

			#print("training episode {} ...".format(episode))
			state = self.grid.insure_id(self.agent_location)  # starting state
			action = plugin.episode_start(episode, state)

			is_terminal = False
			while is_terminal == False:
				#action = plugin.next_action(state_next)  # query plugin for next action

				# tell environment what action to move
				reward, state_next, is_terminal = self.step(action, show)
				time.sleep(delay_per_step)

				# notify plugin this step
				action = plugin.one_step(state, action, reward, state_next, is_terminal)

				# try to show some info on grid, the info to show is decided by plugin
				if show == True:
					text = plugin.get_text_to_display(state)
					self.show_text(state, text)

				state = state_next

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
				reward, state_next, is_terminal = self.step(action)
				time.sleep(delay_per_step)

	def add_object(self, obj_type, index_or_id, reward=0, value=0, is_terminal=False):
		dm = self.drawing_manager
		assert dm != None

		# create an object and attach it to grid
		cell_id = self.grid.insure_id(index_or_id)
		obj = GridObject(obj_type, index_or_id, drawing_manager=self.drawing_manager, data=[cell_id, reward, value, is_terminal])
		self.grid.set_cell(cell_id, obj)

		# draw object
		obj.draw()

		#if is_terminal == True:
		#	dm.draw_object('red_solid_circle', index_or_id)
		#elif value >= 0:
		#	dm.draw_object('yellow_star', index_or_id)
		#else:
		#	dm.draw_object('gray_box', index_or_id)

	def remove_object(self, obj_type, index_or_id):
		obj = self.grid.cell(index_or_id)
		if obj != None:
			obj.remove()
			self.grid.set_cell(index_or_id, None)

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

	def reset(self, show=True):
		self.agent_location = Env.AGENT_LOC
		self.agent_orientation = Env.E

		angle = self.angle_from_orientation(self.agent_orientation)

		if show == True:
			self.drawing_manager.remove_agent()
			self.drawing_manager.draw_agent(self.agent_location, angle)
			# delete previous traces so we don't mess up the environment
			self.drawing_manager.delete_trace()
		
	def step(self, action, show=True):
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
		if self.agent_orientation != action and show == True:
			self.drawing_manager.rotate_agent(index, angle)

		# move agent to its new location
		if index_new != index and show == True:
			self.drawing_manager.move_agent(index, index_new)
			self.drawing_manager.draw_trace(index, angle)

		self.agent_location = index_new
		self.agent_orientation = action

		cur_obj = self.grid.cell(index)
		reward = cur_obj.data[1] if cur_obj != None else self.default_rewards

		state_next = self.grid.insure_id(index_new)
		next_obj = self.grid.cell(index_new)
		is_terminal = next_obj.data[3] if next_obj != None else False

		return (reward, state_next, is_terminal)

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
	from q_learning import QLearning
	from sarsa import Sarsa

	# set the environment
	env = Env((8, 8), (120, 90), default_rewards=0)
	env.add_object('red_solid_circle', (3, 3), value=100, is_terminal=True)
	env.add_object('red_solid_circle', (5, 6), value=200, is_terminal=True)
	#env.add_object((3, 5), value=-100, is_terminal=True)
	#env.add_object((5, 3), value=-100, is_terminal=True)
	#env.add_object((6, 4), value=100, is_terminal=True)
	#env.add_object((1, 5), value=1000)

	# test for TD learning algorithms
	# hyperparameters
	alpha = 0.1
	gamma = 1
	epsilon = 0.5
	lambda_ = 0.7
	n_episodes = 1000

	plugin = QLearning(alpha, gamma, epsilon)
	print(GridObject.__doc__)
	#plugin = Sarsa(alpha, gamma, lambda_, epsilon)
	env.train(plugin, n_episodes, delay_per_step=0, show=True)

	print("agent is now walking ...")
	env.test(plugin)
	#env.test(plugin, 100, only_exploitation=False)

	print("end ...")
	env.remove_object('red_solid_circle', (3, 3))

