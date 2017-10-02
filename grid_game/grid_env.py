import numpy as np
import tkinter as tk


class Block():
	def __init__(self, block_id, reward=0, value=0, is_terminal=False, draw_style=0, text=None):
		self.block_id = block_id	# unique Id
		self.reward = reward		# the reward given when an agent accessing this block
		self.value = value
		self.is_terminal = is_terminal
		self.draw_style = draw_style
		self.text = text

class Grid():
	def __init__(self, dim_x, dim_y, default_rewards=0):
		self.dim_x = dim_x
		self.dim_y = dim_y
		self.total_blocks = dim_x * dim_y

		# creating blocks
		self.blocks = []
		for block_id in range(self.total_blocks):
			self.blocks.append(Block(block_id, reward=default_rewards))
			
		# creating a map representing this grid
		self.minimap = np.arange(self.total_blocks).reshape(dim_x, dim_y)
		
	def blockid_from_xy(self, x, y):
		# range check here

		return (x * self.dim_y) + y

	def xy_from_blockid(self, block_id):
		x = block_id // self.dim_y
		y = block_id % self.dim_y
		return x, y

	def set_block_reward(self, x, y, reward):
		block_id = self.blockid_from_xy(x, y)
		self.blocks[block_id].reward = reward
		
	def set_block_terminal(self, x, y, is_terminal):
		block_id = self.blockid_from_xy(x, y)
		self.blocks[block_id].is_terminal = is_terminal

	def set_block_drawstyle(self, x, y, draw_style):
		block_id = self.blockid_from_xy(x, y)
		self.blocks[block_id].draw_style = draw_style

	def set_block_text(self, x, y, text):
		block_id = self.blockid_from_xy(x, y)
		self.blocks[block_id].text = text

	def set_block(self, x, y, reward, is_terminal, draw_style, text=None):
		block_id = self.blockid_from_xy(x, y)
		self.blocks[block_id].reward = reward
		self.blocks[block_id].is_terminal = is_terminal
		self.blocks[block_id].draw_style = draw_style
		self.blocks[block_id].text = text

	def draw(self, draw_func_list):
		for block in self.blocks:
			index_x, index_y = self.xy_from_blockid(block.block_id)
			draw_func_list[0](index_x, index_y, None) # always draw rectangle
			if block.draw_style != 0:
				draw_func_list[block.draw_style](index_x, index_y, block.text)


"""A class that helps drawing shapes on a tkinter canvas"""
class BlockDrawingHelper():
	def __init__(self, canvas, origin, rect_size):
		self.canvas = canvas
		self.origin = origin
		self.rect_size = rect_size

	def coord_from_index(self, index_x, index_y):
		left = self.rect_size[0] * index_x + self.origin[0]
		top = self.rect_size[1] * index_y + self.origin[1]
		right = left + self.rect_size[0]
		bottom = top + self.rect_size[1]
		return left, top, right, bottom

	def draw_text(self, index_x, index_y, text):
		if text == None:
			return
		x0, y0, x1, y1 = self.coord_from_index(index_x, index_y)
		x = (x0 + x1) / 2
		y = (y0 + y1) / 2
		self.canvas.create_text(x, y, text=text, font=('Times', 16))
		
	def draw_block(self, index_x, index_y, text):
		x0, y0, x1, y1 = self.coord_from_index(index_x, index_y)
		self.canvas.create_rectangle(x0, y0, x1, y1)
		self.draw_text(index_x, index_y, text)

	def draw_red_solid_circle(self, index_x, index_y, text):
		x0, y0, x1, y1 = self.coord_from_index(index_x, index_y)
		self.canvas.create_oval(x0, y0, x1, y1, fill='red')
		self.draw_text(index_x, index_y, text)

	def draw_yellow_star(self, index_x, index_y, text):
		l, t, r, b = self.coord_from_index(index_x, index_y)
		x0 = l
		y0 = t + (b - t)*2/5
		x1 = r
		y1 = y0
		x2 = l + (r - l)/4
		y2 = b
		x3 = (l + r)/2
		y3 = t
		x4 = l + (r - l)*3/4
		y4 = b

		self.canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, x4, y4, fill='yellow')
		self.draw_text(index_x, index_y, text)


class Env():
	def __init__(self, grid_dimension, agent_location=(0, 0), default_rewards=0):
		self.grid_dimension = grid_dimension
		self.agent_location = agent_location

		# setup grid/blocks
		self.grid = Grid(*grid_dimension, default_rewards)

		# don't show environment by default
		self.drawing_helper = None

	# setup the layout of environment
	# you can experiment algorithms by changing this 'layout'
	def set_layout(self):
		self.grid.set_block(6, 6, 100, True, 1, 'Exit')
		self.grid.set_block(8, 8, 10, False, 2, 'Gold')

	def draw_environment(self, block_size):
		window = tk.Tk()
		window.title('Reinforcement Learning Grid Environment')

		# set window size
		win_width = self.grid_dimension[0]
		win_height = self.grid_dimension[1]
		win_width = win_width * block_size[0] + 20
		win_height = win_height * block_size[1] + 20
		window.geometry(str(win_width)+'x'+str(win_height)+'+500+200')


		# set canvas
		canvas = tk.Canvas(window, width=win_width, height=win_height)
		canvas.grid(row=0, column=0)

		# creating a drawing helper, for the drawing of grid/blocks
		self.drawing_helper = BlockDrawingHelper(canvas, (10, 10), block_size)

		# draw grid
		self.grid.draw([self.drawing_helper.draw_block,
				self.drawing_helper.draw_red_solid_circle,
				self.drawing_helper.draw_yellow_star
				])

		# enter window main loop
		window.mainloop()







if __name__ == '__main__':
	env = Env((10, 10), (0, 0))
	env.set_layout()
	env.draw_environment((60, 60))
