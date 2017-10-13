import tkinter as tk
import threading

from grid import Grid

def draw_cell_bbox(canvas, bbox):
	return canvas.create_rectangle(*bbox)

def draw_red_solid_circle(canvas, bbox):
	return canvas.create_oval(*bbox, fill='red')

def draw_gray_box(canvas, bbox):
	return canvas.create_rectangle(*bbox, fill='gray')

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

def draw_pacman(canvas, bbox, angle=0, color='blue', outline='black', ratio=1):
	start = 35 + angle
	extent = 290
	canvas_id = canvas.create_arc(*bbox, start=start, extent=extent, fill=color, outline=outline)

	if ratio < 1:
		x0, y0, x1, y1 = bbox
		centerx = (x0 + x1) / 2
		centery = (y0 + y1) / 2
		canvas.scale(canvas_id, centerx, centery, ratio, ratio)
	
	return canvas_id

def draw_text(canvas, bbox, text, anchor):
	if text == None:
		return None

	x0, y0, x1, y1 = bbox
	if anchor == tk.CENTER:
		x = (x0 + x1) / 2
		y = (y0 + y1) / 2
	elif anchor == tk.N:
		x = (x0 + x1) / 2
		y = y0
	elif anchor == tk.S:
		x = (x0 + x1) / 2
		y = y1
	elif anchor == tk.W:
		x = x0
		y = (y0 + y1) / 2
		text = ' ' + text
	elif anchor == tk.E:
		x = x1
		y = (y0 + y1) / 2
		text = text + ' '
	else:
		assert False

	return canvas.create_text(x, y, text=text, font=('Times', 16), anchor=anchor)


draw_func_list = [draw_red_solid_circle, draw_gray_box, draw_yellow_star]
drawing_function = {'red_solid_circle': draw_red_solid_circle,
			'yellow_star': draw_yellow_star,
			'gray_box': draw_gray_box,
			'pacman': draw_pacman}


"""A class that helps drawing shapes on a tkinter canvas"""
class DrawingManager(threading.Thread):
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

	def bounding_box(self, index_or_id):
		"""Get a cell's bounding box coordinates"""

		cell_index = self.grid.insure_index(index_or_id)

		left = self.cell_size[0] * cell_index[1] + self.origin[0]
		top = self.cell_size[1] * cell_index[0] + self.origin[1]
		right = left + self.cell_size[0]
		bottom = top + self.cell_size[1]
		return (left, top, right, bottom)

	# draw the whole 'chess board' for this grid environment
	def draw_grid(self):
		for cell_id in range(self.grid.n_cells):
			bbox = self.bounding_box(cell_id)
			draw_cell_bbox(self.canvas, bbox)
	
	def draw_object(self, obj_type, index_or_id):
		cell_id = self.grid.insure_id(index_or_id)
		bbox = self.bounding_box(index_or_id)

		tag = obj_type + '_' + str(cell_id)
		tag_of_this_type = obj_type + '_all'

		self.canvas.delete(tag)
		canvas_id = drawing_function[obj_type](self.canvas, bbox)

		self.canvas.addtag_withtag(tag, canvas_id)
		self.canvas.addtag_withtag(tag_of_this_type, tag)

		# wk_debug
		print("tag:", self.canvas.find_withtag(tag))
		print("tag_of_cell:", self.canvas.find_withtag(tag_of_this_type))
		print("non-exist-tag:", self.canvas.find_withtag("abcdefg"))
		print("non-exist-tag len:", len(self.canvas.find_withtag("abcdefg")))

		return canvas_id

	def delete_object(self, obj_type, index_or_id):
		cell_id = self.grid.insure_id(index_or_id)
		tag = obj_type + '_' + str(cell_id)
		#self.canvas.dtag(tag, tag_of_cell)
		self.canvas.delete(tag)

	def is_object_on_cell(self, obj_type, index_or_id):
		cell_id = self.grid.insure_id(index_or_id)
		tag = obj_type + '_' + str(cell_id)
		
		return len(self.canvas.find_withtag(tag))

	def delete_objects_on_cell(self, index_or_id):
		cell_id = self.grid.insure_id(index_or_id)
		tag_of_cell = str(cell_id) + '_cell_id'

		# wk_debug
		print(self.canvas.find_withtag(tag_of_cell))

		self.canvas.delete(tag_of_cell)

#	def draw_on_cell(self, index_or_id, image=None, text=None):
#		cell_id = self.grid.insure_id(index_or_id)
#		bbox = self.bounding_box(index_or_id)
#		draw_info = self.grid.cell(index_or_id)
#
#		if image != None:
#			tag = 'image' + str(cell_id)
#			self.canvas.delete(tag)
#			canvas_id = draw_func_list[image](self.canvas, bbox)
#			self.canvas.addtag_withtag(tag, canvas_id)
#
#		if text != None:
#			tag = 'text' + str(cell_id)
#			self.canvas.delete(tag)
#			canvas_id = draw_text(self.canvas, bbox, text, anchor=tk.CENTER)
#			self.canvas.addtag_withtag(tag, canvas_id)
#
#	def clear_on_cell(self, index_or_id):
#		cell_id = self.grid.insure_id(index_or_id)
#		self.canvas.delete('image' + str(cell_id))
#		self.canvas.delete('text' + str(cell_id))
#		self.canvas.delete('text_list' + str(cell_id))

	def draw_text_list(self, index_or_id, text_anchor_list):
		bbox = self.bounding_box(index_or_id)
		cell_id = self.grid.insure_id(index_or_id)
		tag = 'text_list' + str(cell_id)

		self.canvas.delete(tag)
		for text, anchor in text_anchor_list:
			canvas_id = draw_text(self.canvas, bbox, text, anchor)
			self.canvas.addtag_withtag(tag, canvas_id)

	def draw_trace(self, index_or_id, angle=0, ratio=0.5):
		bbox = self.bounding_box(index_or_id)
		color = '#f8fff8'

		cell_id = self.grid.insure_id(index_or_id)
		tag = 'trace_'+str(cell_id)

		self.canvas.delete(tag)  # delete old trace on this cell
		trace_canvas_id = draw_pacman(self.canvas, bbox, angle, color, color, ratio)
		# move the 'trace' to the lowest layer of canvas elements, so it doesn't block other elements(such as text)
		self.canvas.tag_lower(trace_canvas_id, None)

		self.canvas.addtag_withtag('all_trace', trace_canvas_id)
		self.canvas.addtag_withtag(tag, trace_canvas_id)

	def delete_trace(self):
		self.canvas.delete('all_trace')
		
	def draw_agent(self, index_or_id, angle=0):
		bbox = self.bounding_box(index_or_id)
		self.agent_canvas_id = draw_pacman(self.canvas, bbox, angle)
		
	def remove_agent(self):
		self.canvas.delete(self.agent_canvas_id)

	def rotate_agent(self, index_or_id, rotate_angle):
		bbox = self.bounding_box(index_or_id)

		# tkinter doesn't support rotate a canvas element, so we delete then draw again
		self.canvas.delete(self.agent_canvas_id)
		self.agent_canvas_id = draw_pacman(self.canvas, bbox, rotate_angle)

	def move_agent(self, index_or_id, index_or_id_next):
		bbox = self.bounding_box(index_or_id)
		bbox_next = self.bounding_box(index_or_id_next)

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
