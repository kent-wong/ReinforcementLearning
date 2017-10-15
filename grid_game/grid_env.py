import numpy as np
import tkinter as tk
import time
import random
import sys

from grid import Grid
from drawing import DrawingManager
sys.path.append('./algorithm')
from alg_plugin import ActionSpace


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


class Agent():
	def __init__(self, born_at=(0, 0), facing='E', show=True, drawing_manager=None):
		# save parameters and don't change after init
		self.born_at = born_at
		self.born_facing = facing
		self.drawing_manager = drawing_manager

		# current location and facing, reset after each episode
		self.cur_at = born_at
		self.cur_facing = facing

		# credit
		self._credit = 0

		# whether agent is displayed on screen
		self._show = show

		# bag that stores objects this agent picked up
		self.bag = []

	def _angle_from_facing(self, facing):
		angle = {'N':90, 'S':270, 'W':180, 'E':0}
		return angle[facing]

	def reset(self):
		self.cur_at = self.born_at
		self.cur_facing = self.facing

		if self.show == True:
			angle = self._angle_from_facing(self.cur_facing)
			self.drawing_manager.remove_agent()
			self.drawing_manager.draw_agent(self.cur_at, angle)

			# delete previous traces so we don't mess up the environment
			self.drawing_manager.delete_trace()

	def one_step_to(self, to_index, facing):
		if self.show == True:
			angle = self._angle_from_facing(facing)
			if self.cur_facing != facing:
				self.drawing_manager.rotate_agent(self.cur_at, angle)
			if self.cur_at != to_index:
				self.drawing_manager.move_agent(self.cur_at, to_index)
				self.drawing_manager.draw_trace(self.cur_at, angle)

		self.cur_at = to_index
		self.cur_facing = facing

	def pickup(self, obj):
		self.bag.append(obj)
		self.credit += obj.reward

	def drop(self):
		objs = self.bag
		self.bag = []
		self.credit = 0
		return objs

	@property
	def credit(self):
		return self._credit

	@credit.setter
	def credit(self, value):
		self._credit = value

	@property
	def at(self):
		return self.cur_at

	@at.setter
	def at(self, where):
		self.cur_at = where
	
	@property
	def facing(self):
		return self.cur_facing

	@facing.setter
	def facing(self, orientation):
		self.cur_facing = orientation

	@property
	def show(self):
		return self._show

	@show.setter
	def show(self, onoff):
		self._show = onoff

	@property
	def bag_of_objects(self):
		return self.bag


class Env():
	def __init__(self, grid_dimension=(10, 10), cell_size=(120, 90), default_rewards=0, agent_born_at=(0, 0), agent_born_facing='E'):
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

		self.default_rewards = default_rewards

		# create agent and set its born location and facing direction
		self.agent = Agent(agent_born_at, agent_born_facing, drawing_manager=self.drawing_manager)

	def train(self, plugin, n_episodes, delay_per_step=0, show=True):
		assert plugin != None
		assert n_episodes > 0

		# turn on/off agent display on screen
		# turn off agent display sometimes can massively reduce training time
		show_old = self.agent.show
		self.agent.show = show

		preset_states = []
		for obj in self.grid.cells:
			if obj != None and obj.value != 0:
				state = self.grid.insure_id(obj.index_or_id)
				preset_states.append((state, obj.value, obj.terminal))

		action_space = ActionSpace(self.env_actions)
		# notify plugin environment layout and query plugin to show some info
		plugin.layout(1, action_space, preset_states)
		for cell_id in range(self.grid.n_cells):
			self._show_action_values(cell_id, plugin)

		for episode in range(n_episodes):
			self.reset()  # reset agent's location
			time.sleep(delay_per_step)

			#print("training episode {} ...".format(episode))
			state = self.grid.insure_id(self.agent.at)  # starting state
			action = plugin.episode_start(episode, state)

			is_terminal = False
			while is_terminal == False:
				#action = plugin.next_action(state_next)  # query plugin for next action

				# tell environment what action to move
				reward, state_next, is_terminal = self.step(action)
				time.sleep(delay_per_step)

				# notify plugin this step
				action = plugin.one_step(state, action, reward, state_next, is_terminal)

				# try to show some info on grid, the info to show is decided by plugin
				if show == True:
					self._show_action_values(state, plugin)

				state = state_next

			plugin.episode_end()

		# restore show property
		self.agent.show = show_old

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
		
			state_next = self.grid.insure_id(self.agent.at)  # starting state
			is_terminal = False
			while is_terminal == False:
				action = query_function(state_next)
				reward, state_next, is_terminal = self.step(action)
				time.sleep(delay_per_step)

	@property
	def object_types(self):
		return ['red_ball', 'yellow_star', 'gray_box', 'pacman'] 

	@property
	def env_actions(self):
		return ['N', 'S', 'W', 'E']

	def add_object(self, obj_type, index_or_id, reward=0, value=0, terminal=False, pickable=False):
		"""Add an object to a grid cell. currently only one object is allowed per grid cell.
		parameters:
			obj_type:  object type, a string specifing what type of object to be drawn
			index_or_id:  grid cell index(row, column), or a single non-negative integer
		"""

		# create an object and attach it to grid
		obj = GridObject(obj_type, index_or_id, reward, value, terminal, pickable, drawing_manager=self.drawing_manager)
		self.grid.set_cell(index_or_id, obj)

		# draw object
		obj.draw()

	def restore_object(self, obj):
		# attach object to cell and draw
		self.grid.set_cell(obj.index_or_id, obj)
		obj.draw()

	def remove_object(self, index_or_id):
		obj = self.object_at(index_or_id)
		if obj != None:
			obj.remove()
			self.grid.set_cell(index_or_id, None)

	def object_at(self, index_or_id):
		return self.grid.cell_at(index_or_id)

	def set_walls(self, walls):
		for wall in walls:
			wall = self.grid.insure_index(wall)
			if self._is_hit_wall(wall) == False:
				self.walls.append(wall)

	def _is_hit_wall(self, index_or_id):
		cell_index = self.grid.insure_index(index_or_id)
		for wall in self.walls:
			if cell_index == wall:
				return True
		return False

	def _show_action_values(self, index_or_id, plugin):
		assert plugin != None
		state = self.grid.insure_id(index_or_id)
		action_values_dict = plugin.get_action_values_dict(state)
		if action_values_dict == None:
			return

		for action, value in action_values_dict.items():
			action_values_dict[action] = str(int(value))
		self.drawing_manager.draw_text(index_or_id, action_values_dict)
		
	def _move_by_orders(self, from_index, actions):
		move = {"N":(-1, 0), "S":(1, 0), "W":(0, -1), "E":(0, 1)}
		destination = np.array(from_index)
		index_next = np.array(from_index)

		if isinstance(actions, (list, tuple)) == False:
			actions = [actions]
			
		for action in actions:
			index_next += np.array(move[action])
			if self._is_hit_wall((int(index_next[0]), int(index_next[1]))) == True:
				break
			else:
				destination += np.array(move[action])

		return (int(destination[0]), int(destination[1]))

	def step(self, action):
		cur_index = self.agent.at
		next_index = self._move_by_orders(cur_index, action)

		self.agent.one_step_to(next_index, action)

		obj = self.object_at(cur_index)
		if obj != None:
			reward = obj.reward
		else:
			reward = self.default_rewards

		state_next = self.grid.insure_id(next_index)
		obj = self.object_at(next_index)
		if obj != None:
			terminal = obj.terminal

			# if this object is pickable, let agent pick it up
			if obj.pickable == True:
				self.agent.pickup(obj)
				self.remove_object(next_index)
		else:
			terminal = False

		if terminal == True:
			reward += self.agent.credit
			bag_of_objects = self.agent.drop()
			for obj in bag_of_objects:
				self.restore_object(obj)

		return (reward, state_next, terminal)

	def reset(self):
		self.agent.reset()


if __name__ == '__main__':
	# import algorithms
	sys.path.append('./algorithm')
	from q_learning import QLearning
	from sarsa import Sarsa

	# set the environment
	env = Env((8, 8), (120, 90), default_rewards=0)
	env.add_object('yellow_star', (3, 3), reward=100, pickable=True)
	env.add_object('red_ball', (5, 6), value=200, terminal=True)
	#env.add_object((3, 5), value=-100, is_terminal=True)
	#env.add_object((5, 3), value=-100, is_terminal=True)
	#env.add_object((6, 4), value=100, is_terminal=True)
	#env.add_object((1, 5), value=1000)


	# test for TD learning algorithms
	# hyperparameters
	alpha = 0.1
	gamma = 0.99
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
	#env.remove_object((3, 3))

