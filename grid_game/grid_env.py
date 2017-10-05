import tkinter as tk
from grid import Grid
from drawing import DrawingManager
from env_plugin import EnvPlugin
import time
import random

class Env():
	# actions
	N = 0
	S = 1
	W = 2
	E = 3
	N_ACTIONS = 4

	class CellData():
		def __init__(self, cell_id, reward=0, value=0, is_terminal=False):
			self.cell_id = cell_id	# unique Id
			self.reward = reward	# the reward given when an agent accessing this block
			self.value = value
			self.is_terminal = is_terminal

	def __init__(self, grid_dimension=(10, 10), agent_location=(0, 0), cell_size=(50, 50), default_rewards=0):
		# initialize agent info
		self.agent_location = agent_location
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

	def train(self, n_episodes):
		plugin = self.env_plugin
		assert plugin != None

		plugin.layout(self.grid_dimension, Env.N_ACTIONS)
		for episode in range(n_episodes):
			self.reset()  # reset agent's location

			state_next = self.grid.insure_id(self.agent_location)  # starting state
			plugin.episode_started(state_next)

			is_terminal = False
			while is_terminal == False:
				action = plugin.next_action(state_next)
				state, action, reward, state_next, is_terminal = self.step(action)
				plugin.walked_one_step(state, action, reward, state_next, is_terminal)

			plugin.episode_ended()

			
		
	def plug_and_play(self, env_plugin):
		self.env_plugin = env_plugin
		self.train()
		
	#def get_terminals(self):
	#	result = []
	#	for i in range(self.grid.block_count):
	#		block = self.grid.all_blocks()[i]
	#		if block.is_terminal == True:
	#			result.append((i, block.value))
	#	return result	

	def show_text(self, cell_id_or_index, text):
		self.drawing_manager.draw_on_cell(cell_id_or_index, text=text)
		
	def add_object(self, index_or_id, reward, value, is_terminal):
		self.env_plugin.set_value(index_or_id, value, is_terminal)

		cell = self.grid.cell(index_or_id)
		cell.reward = reward
		cell.value = value
		cell.is_terminal = is_terminal

		if is_terminal == True:
			image = self.drawing_manager.IMAGE_RED_CIRCLE
		elif value >= 0:
			image = self.drawing_manager.IMAGE_YELLOW_STAR
		else:
			image = self.drawing_manager.IMAGE_BLACK_BOX

		self.drawing_manager.draw_on_cell(index_or_id, image)

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

	def reset(self):
		self.agent_location = (0, 0)
		self.agent_orientation = Env.E

		self.drawing_manager.remove_agent()
		angle = self.angle_from_orientation(self.agent_orientation)
		self.drawing_manager.draw_agent(self.agent_location, angle)
		
	def step(self, action):
		index = self.agent_location
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

		cell = self.grid.cell(index)
		cell_next = self.grid.cell(index_new)

		return (cell.cell_id, action, cell.reward, cell_next.cell_id, cell_next.is_terminal)

	def walk_by_orders(self, action_list):
		self.reset()
		for action in action_list:
			self.step(action)


if __name__ == '__main__':
	env = Env((10, 10), (0, 0), (80, 80), -1)
	env.set_layout()

	env.reset()
	n = 0
	action = 0
	while n < 500:
		n += 1
		action = random.choice([Env.N, Env.S, Env.W, Env.E, Env.E, Env.S])
		env.step(action)
		time.sleep(0.2)


	print("end...")
