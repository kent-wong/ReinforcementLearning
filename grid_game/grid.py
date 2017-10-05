"""A class representing the underlying grid structure in the environment"""
class Grid():
	def __init__(self, dimension):
		self.dimension = dimension
		self.n_cells = dimension[0] * dimension[1]  # just for convenience
		self.cell_list = []

	def all_cells(self):
		return self.cell_list
		
	def foreach(self, func):
		for i, cell in enumerate(self.cell_list):
			func(i, cell)

	def cell(self, id_or_index):
		cell_id = id_or_index
		if isinstance(id_or_index, (list, tuple)) == True:
			cell_id = cell_id_from_index(id_or_index, self.dimension)	

		return self.cell_list[cell_id]

	def cell_index_from_id(self, cell_id):
		width = self.grid_dimension[0]
		x = cell_id // width
		y = cell_id % width
		return (x, y)

	def cell_id_from_index(self, index):
		return index[0] * self.grid_dimension[0] + index[1]

	def insure_id(self, index_or_id):
		cell_id = index_or_id
		if isinstance(index_or_id, (list, tuple)) == True:
			cell_id = self.cell_id_from_index(index_or_id)

		return cell_id

	def insure_index(self, index_or_id):
		cell_index = index_or_id
		if isinstance(index_or_id, int) == True:
			cell_index = self.cell_index_from_id(index_or_id)

		return cell_index
