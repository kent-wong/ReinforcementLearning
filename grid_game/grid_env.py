import tkinter as tk
from grid import Grid
from drawing import DrawingManager
import time
import random

class Block():
	def __init__(self, block_id, reward=0, value=0, is_terminal=False):
		self.block_id = block_id	# unique Id
		self.reward = reward		# the reward given when an agent accessing this block
		self.value = value
		self.is_terminal = is_terminal

class Env():
	# actions
	N = 0
	S = 1
	W = 2
	E = 3
	N_ACTIONS = 4

	def __init__(self, grid_dimension, agent_location=(0, 0), block_size=(50, 50), default_rewards=0):
		# create a drawing manager, which creates a tkinter window in a new thread
		self.drawing_manager = DrawingManager(grid_dimension, block_size)
		self.drawing_manager.wait_untill_ready()

		# create grid and add blocks to it
		self.grid = Grid(grid_dimension)
		for i in range(self.grid.block_count):
			block = Block(i, reward=default_rewards)
			self.grid.all_blocks().append(block)

			text = '0' + '\n(' + str(default_rewards) + ')'
			self.drawing_manager.draw_block(self.grid.index_from_blockid(i), None, text)

		# store agent location
		self.agent_location = agent_location
		self.agent_orientation = Env.E

	def get_terminals(self):
		result = []
		for i in range(self.grid.block_count):
			block = self.grid.all_blocks()[i]
			if block.is_terminal == True:
				result.append((i, block.value))
		return result	

	def get_block(self, index):
		return self.grid.block_from_index(index)
		
	def set_block(self, index, reward, value, is_terminal):
		block = self.grid.block_from_index(index)
		block.reward = reward
		block.value = value
		block.is_terminal = is_terminal

		shape = None
		text = str(value) + '\n(' + str(reward) + ')'
		if is_terminal == True:
			shape = DrawingManager.DRAWING_SHAPE_RED_CIRCLE
		elif reward > 0:
			shape = DrawingManager.DRAWING_SHAPE_YELLOW_STAR

		self.drawing_manager.draw_block(index, shape, text)

	# setup the layout of environment
	# you can experiment algorithms by changing this 'layout'
	def set_layout(self):
		self.set_block((6, 6), 100, 0, True)
		self.set_block((8, 8), 10,  0, False)
		self.set_block((6, 7), 10,  0, False)

	def angle_from_orientation(self, ori):
		angle = 0

		if Env.N == ori:
			angle = 90
		elif Env.S == ori:
			angle = 270
		elif Env.W == ori:
			angle = 180

		return angle

	def reset(self, agent_location, orientation):
		self.agent_location = agent_location
		self.agent_orientation = orientation

		angle = self.angle_from_orientation(orientation)
		self.drawing_manager.draw_agent(agent_location, angle)
		
	def step(self, action):
		index = self.agent_location
		block = self.get_block(index) 
		state = block.block_id
		reward = block.reward

		index_new = list(index)

		if action == Env.N:
			index_new[1] -= 1
		elif action == Env.S:
			index_new[1] += 1
		elif action == Env.W:
			index_new[0] -= 1
		elif action == Env.E: 
			index_new[0] += 1
		else:
			assert False
			return None

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
			#self.drawing_manager.draw_trace(index, angle, 0.4)

		block_next = self.get_block(index_new)
		state_next = block_next.block_id
		is_terminal = block_next.is_terminal

		return (state, action, reward, state_next, is_terminal)


if __name__ == '__main__':
	env = Env((10, 10), (0, 0), (80, 80), -1)
	env.set_layout()

	env.reset((0, 0), Env.E)
	n = 0
	action = 0
	while n < 500:
		n += 1
		action = random.choice([Env.N, Env.S, Env.W, Env.E, Env.E, Env.S])
		env.step(action)
		time.sleep(0.2)


	print("end...")
