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
