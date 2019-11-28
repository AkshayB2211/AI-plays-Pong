
import numpy as np
import pygame, sys
from pygame.locals import *
from pong import Ball, Paddle
from matplotlib import pyplot as plt

BLACK    = (0, 0, 0)
WHITE    = (255, 255, 255)
GREY     = (150, 150, 150)

FPS = 30
WIDTH = 700
HEIGHT = 500

pygame.init()
SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("AI PONG")
clock = pygame.time.Clock()

xmargin = 20
paddleA = Paddle(WHITE, xmargin, HEIGHT//2)
paddleB = Paddle(WHITE, WIDTH-xmargin, HEIGHT//2)
ball = Ball(WHITE, WIDTH//2, HEIGHT//2)

# list of all the sprites in the game.
all_sprites = pygame.sprite.Group()
all_sprites.add(paddleA)
all_sprites.add(paddleB)
all_sprites.add(ball)

def reset():
	paddleA.reset(xmargin, HEIGHT//2)
	paddleB.reset(WIDTH-xmargin, HEIGHT//2)
	ball.reset(WIDTH//2, HEIGHT)

	#Return the initial positions
	a_observation = np.array((paddleA.rect.centery, ball.rect.centery))
	b_observation = np.array((paddleB.rect.centery, ball.rect.centery))
	return (a_observation, b_observation)

def render():
	#Display routine
	SCREEN.fill(GREY)
	pygame.draw.line(SCREEN, WHITE, [WIDTH//2, 0], [WIDTH//2, HEIGHT], 5)
	all_sprites.draw(SCREEN)

	#Display scores:
	font = pygame.font.Font(None, 74)
	text = font.render(str(paddleA.score), 1, WHITE)
	SCREEN.blit(text, (250,10))
	text = font.render(str(paddleB.score), 1, WHITE)
	SCREEN.blit(text, (420,10))

	pygame.display.flip()
	clock.tick(FPS)

def step(action):
	all_sprites.update()
	
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()

	# Moving the paddles according to action given... -1, 0 or 1
	speed = 8
	paddleA.move((action[0]-1) * speed)			# map from 0,1,2 to -1,0,1
	paddleB.move((action[1]-1) * speed)	

	# Check if the ball is bouncing against any of the 4 walls:
	if ball.rect.x > WIDTH-ball.r*2:
		paddleA.score +=1
		paddleB.reward -= 10
		ball.velocity[0] = -ball.velocity[0]
	if ball.rect.x < 0:
		paddleB.score +=1
		paddleA.reward -= 10
		ball.velocity[0] = -ball.velocity[0]
	if ball.rect.y > HEIGHT-ball.r*2:
		ball.velocity[1] = -ball.velocity[1]
	if ball.rect.y < 0:
		ball.velocity[1] = -ball.velocity[1]

	# Detect collisions between the ball and the paddles
	if pygame.sprite.collide_rect(ball, paddleA) and ball.velocity[0]<0 :
		paddleA.collided(ball)
		print('a hit')
	if pygame.sprite.collide_rect(ball, paddleB) and ball.velocity[0]>0 :
		paddleB.collided(ball)
		print('b hit')
		
	# If limit reached then done...
	if paddleA.score > 20 or paddleB.score > 20:
		paddleA.done = True
		paddleB.done = True



	# return observations... 1 for each paddle and ball(only y-axis)
	a_observation = np.array((paddleA.rect.centery, ball.rect.centery))
	b_observation = np.array((paddleB.rect.centery, ball.rect.centery))

	state = (a_observation, b_observation)
	reward = (paddleA.reward, paddleB.reward)
	done = (paddleA.done, paddleB.done)
	return (state, reward, done)


# Now comes the Q-learning part...

LEARNING_RATE = 0.1
DISCOUNT = 0.95
EPISODES = 4000
SHOW_EVERY = 500
STATS_EVERY = 100

# Exploration settings
epsilon = 1  	# not a constant, going to be decayed
START_EPSILON_DECAYING = 1
END_EPSILON_DECAYING = EPISODES
epsilon_decay_value = epsilon/(END_EPSILON_DECAYING - START_EPSILON_DECAYING)


# There are 2 observation space, so table will be 2D

TABLE_SIZE = [30, 30]       # this should not hard coded but yet...
action_space = 3			# 3 actions... -1,0,1
num_agents = 2



def get_discrete_state(state):
	# Normalize the state... position value / table_size
	discrete_state = state / TABLE_SIZE
	return tuple(discrete_state.astype(np.int))
	# we use this tuple to look up the 3 Q values for the available actions in the q-table



# Train first one then second, for given episodes....
for i in range(num_agents):
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
		s = reset()
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
				new_state, reward, done = step((action, 1))
			else:
				new_state, reward, done = step((1, action))
				
			episode_reward += reward[i]

			new_discrete_state = get_discrete_state(new_state[i])

			if(episode % SHOW_EVERY == 0):
				render()
			
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
					q_table[discrete_state + (action,)] = 0

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
	q_table = np.load("qtables/best_ones/qtable_{}_best.npy".format(i))
	print('file found')
except:
	print('file not found')
	

