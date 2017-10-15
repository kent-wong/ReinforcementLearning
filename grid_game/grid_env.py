import numpy as np
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

	def __init__(self, obj_type, index_or_id, reward=0, value=0, terminal=False, pickable=False, drawing_manager=None):
		self.obj_type = obj_type
		self.index_or_id = index_or_id
		self.drawing_manager = drawing_manager
		self._reward = reward
		self._value = value
		self._terminal = terminal
		self._pickable = pickable

	def draw(self):
		if self.drawing_manager != None:
			return self.drawing_manager.draw_object(self.obj_type, self.index_or_id)

	def remove(self):
		if self.drawing_manager != None:
			return self.drawing_manager.delete_object(self.obj_type, self.index_or_id)

	def is_on_cell(self):
		if self.drawing_manager != None:
			return self.drawing_manager.is_object_on_cell(self.obj_type, self.index_or_id)
		
	@property
	def terminal(self):
		return self._terminal
	
	@property
	def pickable(self):
		return self._pickable

	@property
	def value(self):
		return self._value

	@property
	def reward(self):
		return self._reward


class Env():
	def __init__(self, grid_dimension=(10, 10), cell_size=(120, 90), default_rewards=0):
		# initialize agent info
		self.default_agent_location = (0, 0)
		self.default_agent_orientation = 'E'
		self.agent_location = (0, 0)
		self.agent_orientation = 'E'

		# create grid and add data to it
		self.grid = Grid(grid_dimension)
		self.grid.cells = [None] * self.grid.n_cells

		# set walls, user can still call .set_walls() to add new walls
		self.walls = []
		height, width = grid_dimension
		for row in range(height):
			self.walls.append((row, -1))
			self.walls.append((row, width))
		for column in range(width):
			self.walls.append((-1, column))
			self.walls.append((height, column))

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
		for obj in self.grid.cells:
			if obj != None and obj.value != 0:
				state = self.grid.insure_id(obj.index_or_id)
				preset_states.append((state, obj.value, obj.terminal))

		action_space = ActionSpace(self.env_actions)
		# notify plugin environment layout and query plugin to show some info
		plugin.layout(1, action_space, preset_states)
		for cell_id in range(self.grid.n_cells):
			self.show_action_values(cell_id, plugin)

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
					self.show_action_values(state, plugin)

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

	def all_object_types(self):
		return ['red_ball', 'yellow_star', 'gray_box', 'pacman'] 

	@property
	def env_actions(self):
		return ['N', 'S', 'W', 'E']

	def add_object(self, obj_type, index_or_id, reward=0, value=0, terminal=False, pickable=False):
		"""Add an object to a grid cell. Currently only one object is allowed per grid cell.
		parameters:
			obj_type:  object type, a string specifing what type of object to be drawn
			index_or_id:  grid cell index(row, column), or a single non-negative integer
		"""
		dm = self.drawing_manager
		assert dm != None

		# create an object and attach it to grid
		obj = GridObject(obj_type, index_or_id, reward, value, terminal, pickable, drawing_manager=self.drawing_manager)
		self.grid.set_cell(index_or_id, obj)

		# draw object
		obj.draw()

	def remove_object(self, obj_type, index_or_id):
		obj = self.grid.cell_at(index_or_id)
		if obj != None:
			obj.remove()
			self.grid.set_cell(index_or_id, None)

	def set_walls(self, walls):
		for wall in walls:
			wall = self.grid.insure_index(wall)
			if self.is_hit_wall(wall) == False:
				self.walls.append(wall)

	def is_hit_wall(self, index_or_id):
		cell_index = self.grid.insure_index(index_or_id)
		for wall in self.walls:
			if cell_index == wall:
				return True
		return False

	def show_action_values(self, index_or_id, plugin):
		assert plugin != None
		state = self.grid.insure_id(index_or_id)
		action_values_dict = plugin.get_action_values_dict(state)
		if action_values_dict == None:
			return

		for action, value in action_values_dict.items():
			action_values_dict[action] = str(int(value))
		self.drawing_manager.draw_text(index_or_id, action_values_dict)
		
	#def show_text(self, index_or_id, text):
	#	if text == None:
	#		return

	#	if isinstance(text, (list, tuple)) == True:
	#		text_list = []
	#		for action, word in enumerate(text):
	#			if action == Env.N:
	#				action = tk.N
	#			elif action == Env.S:
	#				action = tk.S
	#			elif action == Env.W:
	#				action = tk.W
	#			elif action == Env.E:
	#				action = tk.E
	#			else:
	#				assert False

	#			text_list.append((word, action))
	#		self.drawing_manager.draw_text_list(index_or_id, text_list)
	#	else:	
	#		self.drawing_manager.draw_on_cell(index_or_id, text=text)
		
	def angle_from_orientation(self, ori):
		angle = {"N":90, "S":270, "W":180, "E":0}

		return angle[ori]

	def reset(self, show=True):
		self.agent_location = (0, 0)
		self.agent_orientation = 'E'

		angle = self.angle_from_orientation(self.agent_orientation)

		if show == True:
			self.drawing_manager.remove_agent()
			self.drawing_manager.draw_agent(self.agent_location, angle)
			# delete previous traces so we don't mess up the environment
			self.drawing_manager.delete_trace()
		
	def _move_by_orders(self, from_index, actions, walls=None):
		move = {"N":(-1, 0), "S":(1, 0), "W":(0, -1), "E":(0, 1)}
		destination = np.array(from_index)
		index_next = np.array(from_index)
		for action in actions:
			index_next += np.array(move[action])
			if self.is_hit_wall((int(index_next[0]), int(index_next[1]))) == True:
				break
			else:
				destination += np.array(move[action])

		return (int(destination[0]), int(destination[1]))

	def step(self, action, show=True):
		index = self.agent_location
		index_new = self._move_by_orders(index, [action], self.walls)

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

		cur_obj = self.grid.cell_at(index)
		reward = cur_obj.reward if cur_obj != None else self.default_rewards

		state_next = self.grid.insure_id(index_new)
		next_obj = self.grid.cell_at(index_new)
		terminal = next_obj.terminal if next_obj != None else False

		return (reward, state_next, terminal)

	#def walk_by_orders(self, action_list):
	#	self.reset()
	#	for action in action_list:
	#		self.step(action)

	# setup the layout of environment
	# you can experiment algorithms by changing this 'layout'
	#def set_layout(self):
	#	self.add_object((6, 6), value=100)
	#	self.add_object((8, 8), value=10)
	#	self.add_object((6, 7), value=10)


if __name__ == '__main__':
	# import algorithms
	sys.path.append('./algorithm')
	from q_learning import QLearning
	from sarsa import Sarsa

	# set the environment
	env = Env((8, 8), (120, 90), default_rewards=0)
	env.add_object('red_ball', (3, 3), value=100, terminal=True)
	env.add_object('red_ball', (5, 6), value=200, terminal=True)
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

