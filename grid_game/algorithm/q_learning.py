from td_learning import TDLearning

class QLearning(TDLearning):
	def __init__(self, alpha, gamma, epsilon):
		super().__init__(alpha, gamma, 0, epsilon, False)

if __name__ == '__main__':
	qlearning = QLearning(0.1, 0.99, 0.9)
