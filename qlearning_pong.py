
import numpy as np
import pygame, sys
from pygame.locals import *
from pong import Ball, Paddle

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
	ball.reset(WIDTH//2, HEIGHT//2)
	
	#Return the initial positions
	return (paddleA.rect.center, paddleB.rect.center, ball.rect.center)
	
def render():
	#Display routine
	SCREEN.fill(GREY)
	pygame.draw.line(SCREEN, WHITE, [WIDTH//2, 0], [WIDTH//2, HEIGHT], 5)
	all_sprites.update()
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
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
			
	#Moving the paddles according to action given... -1, 0 or 1
	speed = 8
	paddleA.move(action[0] * speed)
	paddleB.move(action[1] * speed)
	
	# Check if the ball is bouncing against any of the 4 walls:
	if ball.rect.x > WIDTH-ball.r*2:
		paddleA.score +=1
		ball.velocity[0] = -ball.velocity[0]
	if ball.rect.x < 0:
		paddleB.score +=1
		ball.velocity[0] = -ball.velocity[0]
	if ball.rect.y > HEIGHT-ball.r*2:
		ball.velocity[1] = -ball.velocity[1]
	if ball.rect.y < 0:
		ball.velocity[1] = -ball.velocity[1]     
 
	# Detect collisions between the ball and the paddles
	if pygame.sprite.collide_rect(ball, paddleA) and ball.velocity[0]<0 :
		ball.bounce()
		ball.rect.x = paddleA.rect.x + paddleA.w
	if pygame.sprite.collide_rect(ball, paddleB) and ball.velocity[0]>0 :
		ball.bounce()
		ball.rect.x = paddleB.rect.x - ball.r*2
	
	state = (paddleA.rect.center, paddleB.rect.center, ball.rect.center)
	reward = (paddleA.score, paddleB.score)
	done = (paddleA.score == 1, paddleB.score == 1)		#condition can be changed
	return (state, reward, done)


#Now comes the Q-learning part...
reset()
while 1:
	render()
	step((-1,1))
