"""A class representing grid in the environment"""
class Grid():
	def __init__(self, dimension):
		self.dimension = dimension
		self.block_count = dimension[0] * dimension[1]
		self.block_list = []

	def all_blocks(self):
		return self.block_list
		
	def foreach(self, func):
		for i, block in enumerate(self.block_list):
			func(i, block)

	def index_from_blockid(self, blockid):
		index_x = blockid // self.dimension[1]
		index_y = blockid % self.dimension[1]
		return (index_x, index_y)

	def blockid_from_index(self, index):
		return (index[0] * self.dimension[1]) + index[1]

	def block_from_id(self, blockid):
		return self.block_list[blockid]

	def block_from_index(self, index):
		blockid = self.blockid_from_index(index)
		return self.block_list[blockid]
