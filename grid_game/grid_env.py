import numpy as np
import tkinter as tk
import time
import random
import sys

from grid import Grid
from drawing import DrawingManager
sys.path.append('./algorithm')
from alg_plugin import ActionSpace
from memory import Memory


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
	
		self._label = None

	def draw(self):
		if self.drawing_manager != None:
			self.drawing_manager.draw_object(self.obj_type, self.index_or_id)
			if self.label != None:
				self.drawing_manager.draw_text(self.index_or_id, {'C':self.label})

	def remove(self):
		if self.drawing_manager != None:
			self.drawing_manager.delete_object(self.obj_type, self.index_or_id)
			self.drawing_manager.delete_text(self.index_or_id)

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

	@property
	def label(self):
		return self._label

	@label.setter
	def label(self, text):
		self._label = text
		if text != None:
			self.drawing_manager.draw_text(self.index_or_id, {'C':text})


class Agent():
	def __init__(self, born_at=(0, 0), facing='E', drawing_manager=None):
		# save parameters and don't change after init
		self._born_at = born_at
		self._born_facing = facing
		self.drawing_manager = drawing_manager

		# current location and facing, reset after each episode
		self.cur_at = born_at
		self.cur_facing = facing

		# credit
		self._credit = 0

		# bag that stores objects this agent picked up
		self.bag = []

		# wk_debug
		self.pickup_all = 0

	def _angle_from_facing(self, facing):
		angle = {'N':90, 'S':270, 'W':180, 'E':0}
		return angle[facing]

	def reset(self, show=True):
		self.cur_at = self.born_at
		self.cur_facing = self.facing

		if show == True:
			angle = self._angle_from_facing(self.cur_facing)
			self.drawing_manager.remove_agent()
			self.drawing_manager.draw_agent(self.cur_at, angle)

			# delete previous traces so we don't mess up the environment
			self.drawing_manager.delete_trace()

	def one_step_to(self, to_index, facing, show=True):
		if show == True:
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

		# wk_debug
		#self.credit *= 10
		#self.credit += obj.reward

		items = len(self.bag)
		if items == 8:
			self.credit = 10000
			self.pickup_all += 1

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
	def bag_of_objects(self):
		return self.bag

	@property
	def born_at(self):
		return self._born_at

	@born_at.setter
	def born_at(self, where):
		if where is None:
			where = (0, 0)  # default
		self._born_at = where
		self.reset()  # set current location to the born place and redraw agent

	@property
	def born_facing(self):
		return self._born_facing

	@born_facing.setter
	def born_facing(self, facing):
		if facing is None:
			facing = 'E'
		self._born_facing = facing
		self.reset()


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

		# create an action space
		self.action_space = ActionSpace(self.env_actions)

		# create agent and set its born location and facing direction
		self.agent = Agent(agent_born_at, agent_born_facing, drawing_manager=self.drawing_manager)
		self.agent.reset()

		# create memory for learning from old experience
		self.history = Memory(2000)

		# keep counts of access times for each cell
		self.access_counter = Grid(grid_dimension)
		self.access_counter.cells = [0] * self.access_counter.n_cells

		# whether environment changes should be displayed on screen
		self._show = True

	@property
	def show(self):
		return self._show

	@show.setter
	def show(self, onoff):
		self._show = onoff

	def calc_state(self):
		factor = self.grid.n_cells
		state = 0
		for obj in self.agent.bag_of_objects:
			cell_id = self.grid.insure_id(obj.index_or_id) + 1
			state += cell_id
			state *= factor

		state += self.grid.insure_id(self.agent.cur_at)
		return state
		
	def index_from_state(self, state):
		factor = self.grid.n_cells
		cell_id = state % factor
		index = self.grid.insure_index(cell_id)
		return index

	def increase_access_counter(self, index_or_id):
		counter = self.access_counter.cell_at(index_or_id)
		counter += 1
		self.access_counter.set_cell(index_or_id, counter)

	def _show_one_counter(self, cell_id, value):
		self.drawing_manager.delete_text(cell_id)
		counter = str(value)
		self.drawing_manager.draw_text(cell_id, {'C':counter})

	def show_access_counters(self):
		self.access_counter.foreach(self._show_one_counter)

		#for cell_id in self.access_counter.n_cells:
		#	drawing_manager.delete_text(cell_id)
		#	counter = self.access_counter.cell_at(cell_id)
		#	counter = str(counter)
		#	drawing_manager.draw_text(cell_id, {'C':counter})

	def record_experience(self, state, action, reward, state_next):
		self.history.add((state, action, reward, state_next))

	def learn_from_experience(self, rl_algorithm, times=200):
		experience = self.history.random_choice(times)
		for s, a, r, s_ in experience:
			rl_algorithm.one_step(s, a, r, s_)

	def pretrain(self):
		self.agent.show = False
		
		while self.history.is_full == False:
			self.reset()
			state = self.calc_state()
			action = self.action_space.random_sample()

			is_terminal = False
			while is_terminal == False:
				reward, state_next, is_terminal = self.step(action)
				# record experience
				self.record_experience(state, action, reward, state_next)

				state = state_next
				action = self.action_space.random_sample()
				
		self.agent.show = True
		self.reset()

	def train(self, rl_algorithm, n_episodes, delay_per_step=0):
		assert rl_algorithm != None
		assert n_episodes > 0

		# pretrain to fullfil memory
		#self.pretrain()

		preset_states = []
		#for obj in self.grid.cells:
		#	if obj != None and obj.value != 0:
		#		state = self.grid.insure_id(obj.index_or_id)
		#		preset_states.append((state, obj.value, obj.terminal))

		# notify rl_algorithm environment layout and query rl_algorithm to show some info
		rl_algorithm.layout(1, self.action_space, preset_states)

		#for cell_id in range(self.grid.n_cells):
		#	self._show_action_values(cell_id, rl_algorithm)

		#rl_algorithm.delayed_learning = True
		for episode in range(n_episodes):
			# reset agent's location at beginning of each episode
			self.reset()
			time.sleep(delay_per_step)

			if episode % 200 == 0:
				print("training episode {}".format(episode))

			if episode % 10 == 0:
				rl_algorithm.delayed_learning_catchup()

			state = self.calc_state()
			action = rl_algorithm.episode_start(episode, state)

			end = False
			while end == False:
				# tell environment what action to move
				reward, state_next, end = self.step(action)
				time.sleep(delay_per_step)

				# notify rl_algorithm this step
				action = rl_algorithm.one_step(state, action, reward, state_next)

				# wk_debug
				#if reward > 0:
					#print("reward: {}, state: {}, end is {}".format(reward, state, end))

				# wk_debug
				#if reward > 0:
				#	action = rl_algorithm.one_step(state, action, reward, state_next)
				#else:
				#	action = rl_algorithm.next_action(state_next)

				# record this step as experience for later learning
				#self.record_experience(state, action, reward, state_next)

				# display value for each action
				if self.show:
					self._show_all_action_values(state, rl_algorithm)

				state = state_next

			rl_algorithm.episode_end()

			# learn from experience
			#self.learn_from_experience(rl_algorithm)

		rl_algorithm.delayed_learning = False


	def test(self, rl_algorithm, repeat=True, delay_per_step=0.5, only_exploitation=True):
		assert rl_algorithm != None

		if only_exploitation == True:
			query_function = rl_algorithm.best_action
		else:
			query_function = rl_algorithm.next_action

		looping = True  # at least loop once
		while looping:
			looping = repeat

			self.reset()  # reset agent's location
			time.sleep(delay_per_step)
		
			#state_next = self.grid.insure_id(self.agent.at)  # starting state
			state_next = self.calc_state()

			is_terminal = False
			while is_terminal == False:
				self._show_all_action_values(state_next, rl_algorithm)
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
		if self.show:
			obj.draw()  # draw object

		return obj

	def restore_object(self, obj):
		# attach object to cell and draw
		self.grid.set_cell(obj.index_or_id, obj)
		if self.show:
			obj.draw()  # draw object

	def remove_object(self, index_or_id):
		obj = self.object_at(index_or_id)
		if obj != None:
			self.grid.set_cell(index_or_id, None)
			if self.show:
				obj.remove()

		return obj

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

	def _show_action_values(self, state, rl_algorithm):
		assert rl_algorithm != None

		index = self.index_from_state(state)
		action_values_dict = rl_algorithm.get_action_values_dict(state)
		if action_values_dict == None:
			return

		for action, value in action_values_dict.items():
			action_values_dict[action] = str(int(value))
		self.drawing_manager.draw_text(index, action_values_dict)
		
	def _show_all_action_values(self, state, rl_algorithm):
		factor = self.grid.n_cells
		state_base = state // factor
		state_base *= factor

		for i in range(factor):
			self._show_action_values(state_base+i, rl_algorithm)

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

		self.increase_access_counter(cur_index)

		self.agent.one_step_to(next_index, action, self.show)

		obj = self.object_at(cur_index)
		if obj != None:
			reward = obj.reward
		else:
			reward = self.default_rewards

		obj = self.object_at(next_index)
		if obj != None:
			terminal = obj.terminal
			# if this object is pickable, let agent pick it up
			if obj.pickable == True:
				self.agent.pickup(obj)
				self.remove_object(next_index)
		else:
			terminal = False

		# notice: calculate state only after agent move a step and (possibly)pick up object
		state_next = self.calc_state()

		if terminal == True:
			reward += self.agent.credit
			bag_of_objects = self.agent.drop()
			for obj in bag_of_objects:
				self.restore_object(obj)

		return (reward, state_next, terminal)

	def reset(self):
		self.agent.reset(self.show)


if __name__ == '__main__':
	# import algorithms
	sys.path.append('./algorithm')
	from q_learning import QLearning
	from sarsa import Sarsa

	# set the environment
	env = Env((8, 8), (130, 90), default_rewards=0)

	def layout0(env):
		star_credit = 1
		env.add_object('yellow_star', (3, 3), reward=star_credit, pickable=True)
		env.add_object('yellow_star', (7, 1), reward=star_credit, pickable=True)
		env.add_object('yellow_star', (0, 7), reward=star_credit, pickable=True)
		env.add_object('yellow_star', (5, 7), reward=star_credit, pickable=True)
		env.add_object('yellow_star', (6, 6), reward=star_credit, pickable=True)
		env.add_object('yellow_star', (5, 5), reward=star_credit, pickable=True)
		env.add_object('yellow_star', (4, 6), reward=star_credit, pickable=True)
		env.add_object('red_ball', (5, 6), value=0, terminal=True).label = "Exit"

	def layout1(env):
		env.add_object('yellow_star', (3, 3), reward=100, pickable=True).label = "(100)"
		env.add_object('yellow_star', (0, 7), reward=1000, pickable=True).label = "(1000)"
		env.add_object('red_ball', (5, 6), value=0, terminal=True).label = "Exit"
		
	def layout2(env):
		env.agent.born_at = (3, 3)
		env.add_object('yellow_star', (0, 0), reward=100, pickable=True).label = "(100)"
		env.add_object('yellow_star', (0, 7), reward=100, pickable=True).label = "(100)"
		env.add_object('yellow_star', (7, 0), reward=100, pickable=True).label = "(100)"
		env.add_object('yellow_star', (7, 7), reward=100, pickable=True).label = "(100)"
		env.add_object('red_ball', (3, 4), value=0, terminal=True).label = "Exit"
		
	def layout3(env):
		env.agent.born_at = (0, 0)
		env.agent.credit = 100
		env.add_object('red_ball', (3, 4), value=0, terminal=True).label = "Exit"

	def layout4(env):
		env.agent.born_at = (7, 0)
		env.add_object('yellow_star', (0, 0), reward=100, pickable=True).label = "(100)"
		env.add_object('yellow_star', (1, 1), reward=100, pickable=True).label = "(100)"
		env.add_object('yellow_star', (2, 2), reward=100, pickable=True).label = "(100)"
		env.add_object('yellow_star', (3, 3), reward=100, pickable=True).label = "(100)"
		env.add_object('yellow_star', (4, 4), reward=100, pickable=True).label = "(100)"
		env.add_object('yellow_star', (5, 5), reward=100, pickable=True).label = "(100)"
		env.add_object('yellow_star', (6, 6), reward=100, pickable=True).label = "(100)"
		env.add_object('yellow_star', (7, 7), reward=100, pickable=True).label = "(100)"
		env.add_object('red_ball', (0, 7), value=0, terminal=True).label = "Exit"
		
	def layout5(env):
		env.agent.born_at = (5, 0)
		env.add_object('yellow_star', (0, 0), pickable=True)
		env.add_object('yellow_star', (7, 7), pickable=True)
		env.add_object('red_ball', (4, 3), terminal=True).label = "Exit"
		
	# use a layout
	layout4(env)

	# hyperparameters
	alpha = 0.1
	gamma = 0.9
	epsilon = 0.7
	lambda_ = 0.7
	n_episodes = 10000

	rl_algorithm = QLearning(alpha, gamma, epsilon)
	#rl_algorithm = Sarsa(alpha, gamma, lambda_, epsilon)

	env.show = False
	print("training ...")
	env.train(rl_algorithm, n_episodes, delay_per_step=0)
	env.show = True

	#env.show_access_counters()

	# wk_debug
	print("pickup all:", env.agent.pickup_all)

	print("agent is now walking ...")
	env.test(rl_algorithm)
	#env.test(rl_algorithm, 100, only_exploitation=False)

	print("end ...")
	#env.remove_object((3, 3))

