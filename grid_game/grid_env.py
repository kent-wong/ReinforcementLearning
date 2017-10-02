import tkinter as tk
from grid import Grid
from drawing import DrawingManager
import threading
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
	W = 1
	E = 2
	S = 3

	def __init__(self, grid_dimension, agent_location=(0, 0), block_size=(50, 50), default_rewards=0):
		self.agent_location = agent_location

		# create grid and add blocks to it
		self.grid = Grid(grid_dimension)
		for i in range(self.grid.block_count):
			block = Block(i)
			self.grid.all_blocks().append(block)

		# create a drawing manager, which creates a tkinter window in a new thread
		self.drawing_manager = DrawingManager(grid_dimension, block_size)
		self.drawing_manager.wait_untill_ready()

	def set_block(self, index, reward, value, is_terminal):
		block = self.grid.block_from_index(index)
		block.reward = reward
		block.value = value
		block.is_terminal = is_terminal

		shape = None
		text = str(value)
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

	def reset(self, index):
		self.agent_location = index
		self.drawing_manager.draw_agent(index)
		
	def step(self, action):
		index = self.agent_location
		state = self.grid.blockid_from_index(index)

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
			return 

		# check boundary condition
		if index_new[0] < 0 or index_new[0] >= self.grid.dimension[0]:
			index_new = index
		elif index_new[1] < 0 or index_new[1] >= self.grid.dimension[1]:
			index_new = index

		# move agent to its new location
		if index_new != index:	
			self.drawing_manager.move_agent(index, index_new)
			self.agent_location = index_new



if __name__ == '__main__':
	env = Env((10, 10), (0, 0))
	env.set_layout()

	env.reset((0, 0))
	n = 0
	action = 0
	while n < 100:
		n += 1
		action = random.choice([Env.N, Env.S, Env.W, Env.E, Env.E, Env.S])
		env.step(action)
		time.sleep(0.1)


	print("end...")
