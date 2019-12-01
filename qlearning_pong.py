
import numpy as np
import pygame, sys
from pygame.locals import *
from pong_env import Pong, Paddle, Ball
from matplotlib import pyplot as plt


# create the environment...
env = Pong()

LEARNING_RATE = 0.1
DISCOUNT = 0.95
EPISODES = 4000
SHOW_EVERY = 500
STATS_EVERY = 100
PLAY = True
#~ PLAY = False

# Exploration settings
epsilon = 1  	# not a constant, going to be decayed
START_EPSILON_DECAYING = 1
END_EPSILON_DECAYING = EPISODES//2
epsilon_decay_value = epsilon/(END_EPSILON_DECAYING - START_EPSILON_DECAYING)

# There are 2 observation space, so table will be 2D
TABLE_SIZE = [30, 30]       			# this should not hard coded but yet...
action_space = env.action_space			# 3 actions... -1,0,1
num_agents = 2


def get_discrete_state(state):
	# Normalize the state... position value / table_size
	discrete_state = state / TABLE_SIZE
	# we use this tuple to look up the 3 Q values for the available actions in the q-table
	return tuple(discrete_state.astype(np.int))


# Train first one then second, for given episodes....
for i in range(num_agents):
	if PLAY:
		break
	epsilon = 1			# reset epsilon and table for next agent
	
	# use the best q-table, if available...
	try:
		q_table = np.load("qtables/best_ones/qtable_{}_best.npy".format(i))
		print('using best ones..')
	except:
		q_table = np.random.uniform(low=-2, high=0, size=(TABLE_SIZE + [action_space]))
	
	# For stats
	ep_rewards = []
	aggr_ep_rewards = {'ep': [], 'avg': [], 'max': [], 'min': []}
	
	for episode in range(EPISODES):
		episode_reward = 0
		s = env.reset()
		done = [False, False]
		print(episode)
		discrete_state = get_discrete_state(s[i])

		while not done[i]:
			if np.random.random() > epsilon :
				# Get action from Q table
				action = np.argmax(q_table[discrete_state])
			else:
				# Get random action
				action = np.random.randint(0, action_space)

			#~ print (action)
			if(i == 0):
				new_state, reward, done = env.step((action, 1))
			else:
				new_state, reward, done = env.step((1, action))
				
			episode_reward += reward[i]
			new_discrete_state = get_discrete_state(new_state[i])

			if(episode % SHOW_EVERY == 0):
				env.render()
			
			# If simulation did not end yet after last step - update Q table
			if not done[i]:
				# Maximum possible Q value in next step (for new state)
				max_future_q = np.max(q_table[new_discrete_state])

				# Current Q value (for current state and performed action)
				current_q = q_table[discrete_state + (action,)]

				# Equation for a new Q value for current state and action
				new_q = (1 - LEARNING_RATE) * current_q + LEARNING_RATE * (reward[i] + DISCOUNT * max_future_q)

				# Update Q table with new Q value
				q_table[discrete_state + (action,)] = new_q


			# Simulation ended (for any reson) - if goal position is achived - update Q value to highest
			else:
				if ((i == 0 and paddleA.reward>=10) or (i == 1 and paddleB.reward>=10)):
					q_table[discrete_state + (action,)] = 100

			discrete_state = new_discrete_state
		
		# Save the Q-table
		if not episode % STATS_EVERY:
			np.save("qtables/qtable_{}_e{}".format(i, episode), q_table)
		
		# Decaying is being done every episode if episode number is within decaying range
		if END_EPSILON_DECAYING >= episode >= START_EPSILON_DECAYING:
			epsilon -= epsilon_decay_value
		
		# Matplot visualize	
		ep_rewards.append(episode_reward)
		if not episode % (STATS_EVERY//10):
			average_reward = sum(ep_rewards[-STATS_EVERY:])/STATS_EVERY
			aggr_ep_rewards['ep'].append(episode)
			aggr_ep_rewards['avg'].append(average_reward)
			aggr_ep_rewards['max'].append(max(ep_rewards[-STATS_EVERY:]))
			aggr_ep_rewards['min'].append(min(ep_rewards[-STATS_EVERY:]))
			#~ print(f'Episode: {episode:>5d}, average reward: {average_reward:>4.1f}, current epsilon: {epsilon:>1.2f}')
			
	plt.plot(aggr_ep_rewards['ep'], aggr_ep_rewards['avg'], label="average rewards")
	plt.plot(aggr_ep_rewards['ep'], aggr_ep_rewards['max'], label="max rewards")
	plt.plot(aggr_ep_rewards['ep'], aggr_ep_rewards['min'], label="min rewards")
	#~ plt.show()	
	plt.savefig("qtables/paddle_{}.png".format(i))	
	plt.clf()
			
			
# After Training, time to play...
try:
	q_table_a = np.load("qtables/best_ones/qtable_0_best.npy")
	q_table_b = np.load("qtables/best_ones/qtable_1_best.npy")
	print('file found')
	found = True
except:
	print('file not found')
	found = False
	
s = env.reset()
while found:
	state_a = get_discrete_state(s[0])
	state_b = get_discrete_state(s[1])
	
	action_a = np.argmax(q_table_a[state_a])
	action_b = np.argmax(q_table_b[state_b])
	s, _, _ = env.step((action_a, action_b))
	env.render()


