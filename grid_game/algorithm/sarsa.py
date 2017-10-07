from td_learning import TDLearning

class Sarsa(TDLearning):
	def __init__(self, alpha, gamma, lambda_, epsilon):
		super().__init__(alpha, gamma, lambda_, epsilon, True)

if __name__ == '__main__':
	sarsa = Sarsa(0.1, 0.99, 0, 0.9)

