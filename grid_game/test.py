import sys
sys.path.append('./algorithm')
from q_learning import QLearning
from grid_env import Env

# parameters
param_grid_size = 10
param_block_size = 80
param_default_reward = 0
param_agent_loc = (0, 0)
param_alpha = 0.1
param_gamma = 0.99
param_epsilon = 0.9
hyper_n_episodes = 10

env = Env((param_grid_size, param_grid_size), param_agent_loc, (param_block_size, param_block_size), param_default_reward)
env.set_block((6, 6), param_default_reward, 100, True)
#env.set_block((8, 8), 10,  0, False)
#env.set_block((6, 7), 10,  0, False)

q = QLearning(param_alpha, param_gamma, param_epsilon, Env.N_ACTIONS)
terms = env.get_terminals()
print(terms)
for state, value in terms:
	q.set_terminal(state, value)

for episode in range(hyper_n_episodes):
	env.reset((0, 0), Env.E)
	is_terminal = False
	state = 0
	action = q.episode_start(state)
	while is_terminal == False:
		state, action, reward, state_next, is_terminal = env.step(action)
		print("agent from state {} --> state {}, take action {}".format(state, state_next, action))
		if is_terminal == True:
			print("episode {}: agent reached terminal".format(episode))
		action = q.step(state, action, reward, state_next)
	q.episode_end()
