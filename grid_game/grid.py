"""A class representing the underlying grid structure in the environment"""
class Grid():
	def __init__(self, dimension):
		self.dimension = dimension
		self.n_cells = dimension[0] * dimension[1]  # just for convenience
		self.cell_list = []

	@property
	def cells(self):
		return self.cell_list
		
	@cells.setter
	def cells(self, new_list):
		self.cell_list = new_list

	def foreach(self, func):
		for i, cell in enumerate(self.cell_list):
			func(i, cell)

	def cell_at(self, index_or_id):
		cell_id = self.insure_id(index_or_id)
		return self.cell_list[cell_id]

	def set_cell(self, index_or_id, new_cell):
		cell_id = self.insure_id(index_or_id)
		self.cell_list[cell_id] = new_cell

	def insure_id(self, index_or_id):
		cell_id = index_or_id
		if isinstance(index_or_id, (list, tuple)) == True:
			cell_id = self.cell_id_from_index(index_or_id, self.dimension[0])

		return cell_id

	def insure_index(self, index_or_id):
		cell_index = index_or_id
		if isinstance(index_or_id, int) == True:
			cell_index = self.cell_index_from_id(index_or_id, self.dimension[0])

		return tuple(cell_index)

	@staticmethod
	def cell_index_from_id(cell_id, width):
		x = cell_id // width
		y = cell_id % width
		return (x, y)

	@staticmethod
	def cell_id_from_index(index, width):
		return index[0] * width + index[1]

if __name__ == "__main__":
	cell_id = Grid.cell_id_from_index((1, 1), 10)
	print("cell id:", cell_id)

	cell_index = Grid.cell_index_from_id(11, 10)
	print("cell index:", cell_index)

	grid = Grid((10, 10))
	cell_id = grid.insure_id((1, 1))
	print("insure id:", cell_id)
	cell_index = grid.insure_index(11)
	print("insure index:", cell_index)

	grid.cells
	grid.cells = [1, 2, 3]
