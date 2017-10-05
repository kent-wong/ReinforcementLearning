import tkinter as tk
import threading
from grid import Grid
import env_utils as utils

def draw_cell_bbox(canvas, bbox):
	return canvas.create_rectangle(*bbox)

def draw_red_solid_circle(canvas, bbox):
	return canvas.create_oval(*bbox, fill='red')

def draw_black_box(canvas, bbox):
	return canvas.create_rectangle(*bbox, fill='black')

def draw_yellow_star(canvas, bbox):
	l, t, r, b = bbox
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

	return canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, x4, y4, fill='yellow')

def draw_pacman(canvas, bbox, rotate_angle=0):
	start = 35 + rotate_angle
	extent = 290
	return canvas.create_arc(*bbox, start=start, extent=extent, fill='blue')

def draw_text(canvas, bbox, text):
	if text == None:
		return None

	x0, y0, x1, y1 = bbox
	x = (x0 + x1) / 2
	y = (y0 + y1) / 2
	return canvas.create_text(x, y, text=text, font=('Times', 16), justify=tk.CENTER)

def draw_trace(canvas, bbox, angle=0):
	x0, y0, x1, y1 = bbox
	centerx = (x0 + x1) / 2
	centery = (y0 + y1) / 2

	start = 35 + angle
	extent = 290
	canvas_id = canvas.create_arc(*bbox, start=start, extent=extent, fill='#f0fff8')
	#self.canvas.scale(canvas_id, centerx, centery, ratio, ratio)
	return canvas_id

draw_func_list = [draw_red_solid_circle, draw_black_box, draw_yellow_star]


"""A class that helps drawing shapes on a tkinter canvas"""
class DrawingManager(threading.Thread):
	# image type on cell
	IMAGE_RED_CIRCLE = 0
	IMAGE_BLACK_BOX = 1
	IMAGE_YELLOW_STAR = 2

	class DrawingInfo():
		def __init__(self):
			self.image_canvas_id = None
			self.text_canvas_id = None

	def __init__(self, grid_dimension, cell_size):
		threading.Thread.__init__(self)

		self.grid_dimension = grid_dimension
		self.cell_size = cell_size
		self.agent_canvas_id = None
		self.lock = threading.Lock()

		# start running in new thread, use a lock to protect initializing stage
		self.lock.acquire()
		self.start()

	def wait(self):
		# wait untill tkinter window is established
		self.lock.acquire()
		self.lock.release()

		return self

	def bounding_box(self, cell_id_or_index):
		"""Get a cell's bounding box coordinates"""

		cell_index = cell_id_or_index
		if isinstance(cell_id_or_index, int) == True:
			cell_index = utils.cell_index_from_id(cell_id_or_index, self.grid_dimension)

		left = self.cell_size[0] * cell_index[0] + self.origin[0]
		top = self.cell_size[1] * cell_index[1] + self.origin[1]
		right = left + self.cell_size[0]
		bottom = top + self.cell_size[1]
		return (left, top, right, bottom)

	# draw the whole 'chess board' for this grid environment
	def draw_grid(self):
		n_cells = self.grid_dimension[0] * self.grid_dimension[1]
		for cell_id in range(n_cells):
			cell_index = utils.cell_index_from_id(cell_id)
			bbox = self.bbox_from_index(cell_index)
			draw_cell_bbox(self.canvas, bbox)
	
	def draw_on_cell(self, cell_id_or_index, image=None, text=None):
		bbox = self.bounding_box(cell_id_or_index)
		draw_info = self.grid.cell(cell_id_or_index)

		if image != None:
			self.canvas.delete(draw_info.image_canvas_id)
			draw_info.image_canvas_id = draw_func_list[image](self.canvas, bbox)

		if text != None:
			self.canvas.delete(draw_info.text_canvas_id)
			draw_info.text_canvas_id = draw_text(self.canvas, bbox, text)

	#def draw_trace(self, index, angle=0, ratio=1):
	#	x0, y0, x1, y1 = self.coord_from_index(index)
	#	draw_info = self.grid.block_from_index(index)

	#	if draw_info.shape_canvas_id == None:
	#		draw_info.shape_canvas_id = self.drawing_helper.draw_trace(x0, y0, x1, y1, angle, ratio)
		
	def draw_agent(self, cell_id_or_index, rotate_angle=0):
		bbox = self.bounding_box(cell_id_or_index)
		self.agent_canvas_id = draw_pacman(self.canvas, bbox, rotate_angle)
		
	def remove_agent(self):
		self.canvas.delete(self.agent_canvas_id)

	def rotate_agent(self, cell_id_or_index, rotate_to):
		bbox = self.bounding_box(cell_id_or_index)

		# tkinter doesn't support rotate a canvas element, so we delete then draw again
		self.canvas.delete(self.agent_canvas_id)
		self.agent_canvas_id = draw_pacman(self.canvas, bbox, rotate_angle)

	def move_agent(self, cell_id_or_index, cell_id_or_index_next):
		bbox = self.bounding_box(cell_id_or_index)
		bbox_next = self.bounding_box(cell_id_or_index_next)

		x0, y0, x1, y1 = self.coord_from_index(index)
		xx0, yy0, xx1, yy1 = self.coord_from_index(index_new)
		
		move_x = bbox_next[0] - bbox[0]
		move_y = bbox_next[1] - bbox[1]
		self.canvas.move(self.agent_canvas_id, move_x, move_y)
		#print("agent_canvas_id:{}, index:{}".format(self.agent_canvas_id, index_new))
		#self.canvas.move(self.agent_canvas_id, 30, 30)

	def run(self):
		# create tkinter window
		window = tk.Tk()
		window.title('Reinforcement Learning Grid Environment')

		# set window size
		width = self.grid_dimension[0] * self.cell_size[0] + 20
		height = self.grid_dimension[1] * self.cell_size[1] + 20
		window.geometry(str(width)+'x'+str(height)+'+500+200')

		# set canvas
		canvas = tk.Canvas(window, width=width, height=height)
		canvas.grid(row=0, column=0)

		# save parameters
		self.window = window
		self.canvas = canvas
		self.origin = (10, 10)	# canvas has 10 pixels margin from window borders

		# create grid for saving drawing info
		self.grid = Grid(self.grid_dimension)
		for i in range(self.grid.n_cells):
			info = DrawingManager.DrawingInfo()
			self.grid.all_cells().append(info)

		self.lock.release()

		# enter window mainloop
		self.window.mainloop()
