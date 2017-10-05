import tkinter as tk
import threading
from grid import Grid

class DrawingHelperFunc():
	def __init__(self, canvas):
		self.canvas = canvas
		
	def draw_block_rect(self, x0, y0, x1, y1, ratio=1):
		return self.canvas.create_rectangle(x0, y0, x1, y1)

	def draw_red_solid_circle(self, x0, y0, x1, y1, ratio=1):
		return self.canvas.create_oval(x0, y0, x1, y1, fill='red')
	 
	def draw_yellow_star(self, l, t, r, b, ratio=1):
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

		return self.canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, x4, y4, fill='yellow')
	
	def draw_trace(self, x0, y0, x1, y1, angle=0, ratio=1):
		centerx = (x0 + x1) / 2
		centery = (y0 + y1) / 2

		start = 35 + angle
		extent = 290
		canvas_id = self.canvas.create_arc(x0, y0, x1, y1, start=start, extent=extent, fill='#f0fff8')
		self.canvas.scale(canvas_id, centerx, centery, ratio, ratio)
		return canvas_id

	def draw_pacman(self, x0, y0, x1, y1, rotate_angle=0, ratio=1):
		start = 35 + rotate_angle
		extent = 290
		return self.canvas.create_arc(x0, y0, x1, y1, start=start, extent=extent, fill='blue')

	def draw_text(self, x0, y0, x1, y1, text):
		if text == None:
			return None

		x = (x0 + x1) / 2
		y = (y0 + y1) / 2
		return self.canvas.create_text(x, y, text=text, font=('Times', 16), justify=tk.CENTER)
		
	def get_shape_func(self, shape):
		func_list = [self.draw_block_rect, self.draw_red_solid_circle, self.draw_yellow_star, self.draw_trace]
		return func_list[shape]


"""A class that helps drawing shapes on a tkinter canvas"""
class DrawingManager(threading.Thread):
	# block drawing shape
	DRAWING_SHAPE_EMPTY = 0
	DRAWING_SHAPE_RED_CIRCLE = 1
	DRAWING_SHAPE_YELLOW_STAR = 2
	DRAWING_SHAPE_TRACE = 3

	class DrawingInfo():
		def __init__(self, shape, text):
			self.shape = shape
			self.text = text
			self.shape_canvas_id = None
			self.text_canvas_id = None

	def __init__(self, grid_dimension, block_size):
		threading.Thread.__init__(self)

		self.grid_dimension = grid_dimension
		self.block_size = block_size
		self.agent_canvas_id = None
		self.lock = threading.Lock()

		# start running in new thread, use a lock to protect initializing stage
		self.lock.acquire()
		self.start()

	def wait_untill_ready(self):
		# wait untill tkinter window is established
		self.lock.acquire()
		self.lock.release()

	def coord_from_index(self, index):
		"""Get block coordinate from block index"""

		left = self.block_size[0] * index[0] + self.origin[0]
		top = self.block_size[1] * index[1] + self.origin[1]
		right = left + self.block_size[0]
		bottom = top + self.block_size[1]
		return (left, top, right, bottom)

	def draw_block(self, index, shape, text):
		x0, y0, x1, y1 = self.coord_from_index(index)
		draw_info = self.grid.block_from_index(index)

		if shape != None:
			self.canvas.delete(draw_info.shape_canvas_id)
			draw_info.shape_canvas_id = self.drawing_helper.get_shape_func(shape)(x0, y0, x1, y1)

		if text != None:
			self.canvas.delete(draw_info.text_canvas_id)
			draw_info.text_canvas_id = self.drawing_helper.draw_text(x0, y0, x1, y1, text)

	def draw_trace(self, index, angle=0, ratio=1):
		x0, y0, x1, y1 = self.coord_from_index(index)
		draw_info = self.grid.block_from_index(index)

		if draw_info.shape_canvas_id == None:
			draw_info.shape_canvas_id = self.drawing_helper.draw_trace(x0, y0, x1, y1, angle, ratio)
		
	def draw_agent(self, index, rotate_angle=0):
		x0, y0, x1, y1 = self.coord_from_index(index)
		self.agent_canvas_id = self.drawing_helper.draw_pacman(x0, y0, x1, y1, rotate_angle)
		
	def remove_agent(self):
		self.canvas.delete(self.agent_canvas_id)

	def rotate_agent(self, index, rotate_to):
		x0, y0, x1, y1 = self.coord_from_index(index)

		# tkinter doesn't support rotate a canvas element, so we delete then draw again
		self.canvas.delete(self.agent_canvas_id)
		self.agent_canvas_id = self.drawing_helper.draw_pacman(x0, y0, x1, y1, rotate_to)

	def move_agent(self, index, index_new):
		x0, y0, x1, y1 = self.coord_from_index(index)
		xx0, yy0, xx1, yy1 = self.coord_from_index(index_new)
		
		move_x = xx0 - x0
		move_y = yy0 - y0
		self.canvas.move(self.agent_canvas_id, move_x, move_y)
		#print("agent_canvas_id:{}, index:{}".format(self.agent_canvas_id, index_new))
		#self.canvas.move(self.agent_canvas_id, 30, 30)

	def run(self):
		# create tkinter window
		window = tk.Tk()
		window.title('Reinforcement Learning Grid Environment')

		# set window size
		width = self.grid_dimension[0] * self.block_size[0] + 20
		height = self.grid_dimension[1] * self.block_size[1] + 20
		window.geometry(str(width)+'x'+str(height)+'+500+200')

		# set canvas
		canvas = tk.Canvas(window, width=width, height=height)
		canvas.grid(row=0, column=0)

		# save parameters
		self.window = window
		self.canvas = canvas
		self.origin = (10, 10)	# canvas has 10 pixels margin from window borders

		# create grid and add block drawing info to it
		self.grid = Grid(self.grid_dimension)
		for i in range(self.grid.block_count):
			info = DrawingManager.DrawingInfo(DrawingManager.DRAWING_SHAPE_EMPTY, None)
			self.grid.all_blocks().append(info)


		# creat a drawing helper
		self.drawing_helper = DrawingHelperFunc(canvas)

		# now drawing bounding rectangle for every block
		for i in range(self.grid.block_count):
			index = self.grid.index_from_blockid(i)
			x0, y0, x1, y1 = self.coord_from_index(index)
			self.drawing_helper.get_shape_func(DrawingManager.DRAWING_SHAPE_EMPTY)(x0, y0, x1, y1)

		self.lock.release()

		# enter window mainloop
		self.window.mainloop()
