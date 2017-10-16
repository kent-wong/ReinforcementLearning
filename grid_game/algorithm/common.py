"""A class that provide selection algorithms"""
import numpy as np

def argmax_multi(data):
	assert len(data) > 0
	max = data[0]
	indexes = []
	for i, v in enumerate(data):
		if v > max:
			max = v
			indexes = [i]  # this assignment operation may also delete previous max(now is not any more) elements
		elif v == max:
			indexes.append(i)
	return indexes

def index_sub(a, b):
	a = set(a)
	b = set(b)
	return list(a - b)

def epsilon_greedy(epsilon, action_values):
	n_actions = len(action_values)
	assert n_actions >= 1
	if n_actions == 1:
		return 0
	indexes = argmax_multi(action_values)
	if np.random.random() > epsilon and len(indexes) < n_actions:
		indexes = index_sub(range(n_actions), indexes)
	return np.random.choice(indexes)

def explore(steps, action_values):
	explore_start = 1.0
	explore_stop = 0.4
	decay_rate = 0.00001

	explore_rate = explore_stop + (explore_start - explore_stop)*np.exp(-decay_rate*steps)

	# wk_debug
	#if steps % 1000 == 0:
		#print("step: {}, explore_rate: {}".format(steps, explore_rate))

	return epsilon_greedy(1-explore_rate, action_values)


if __name__ == "__main__":
	a = explore(100000, [1, 2, 3, 4])
	print(a)
