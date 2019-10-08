
import pygame, sys, math
from random import randint
from pygame.locals import *

BLACK    = (0, 0, 0)
GREEN    = (0, 255, 0)
RED      = (255, 0, 0)
WHITE    = (255, 255, 255)
GREY     = (150, 150, 150)

FPS = 30
WIDTH = 700
HEIGHT = 500

class Ball(pygame.sprite.Sprite):
	def __init__(self, color, x, y):
		super().__init__()
		
		self.r = 6

		# Set the background color and set it to be transparent
		self.image = pygame.Surface([self.r*2, self.r*2])
		self.image.fill(BLACK)
		self.image.set_colorkey(BLACK)

		pygame.draw.circle(self.image, color, [self.r, self.r], self.r)

		self.velocity = [randint(4,8),randint(-8,8)]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

	def update(self):
		self.rect.x += self.velocity[0]
		self.rect.y += self.velocity[1]

	def bounce(self):
		self.velocity[0] = -self.velocity[0]
		self.velocity[1] = randint(-8,8)

class Paddle(pygame.sprite.Sprite):
	def __init__(self, color, x, y):
		super().__init__()
		
		self.w = 10
		self.h = 100

		# Set the background color and set it to be transparent
		self.image = pygame.Surface([self.w, self.h])
		self.image.fill(BLACK)
		self.image.set_colorkey(BLACK)

		pygame.draw.rect(self.image, color, [0, 0, self.w, self.h])
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

	def move(self, y):
		self.rect.y += y
		if self.rect.y < 0:
			self.rect.y = 0
		if self.rect.y > HEIGHT-self.h:
			self.rect.y = HEIGHT-self.h


def main():
	global SCREEN
	pygame.init()

	SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))
	pygame.display.set_caption("AI PONG")

	clock = pygame.time.Clock()

	xmargin = 20
	paddleA = Paddle(WHITE, xmargin, HEIGHT//2-50)
	paddleB = Paddle(WHITE, WIDTH-xmargin-10, HEIGHT//2-50)
	ball = Ball(WHITE, WIDTH//2, HEIGHT//2)
	
	# list of all the sprites in the game.
	all_sprites = pygame.sprite.Group()
	
	all_sprites.add(paddleA)
	all_sprites.add(paddleB)
	all_sprites.add(ball)
	
	scoreA = 0
	scoreB = 0

	# -------- Main Program Loop -----------
	while True:
		for event in pygame.event.get():
			#~ print(event)
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
				
		#Moving the paddles when the use uses the arrow keys (player A) or "W/S" keys (player B) 
		keys = pygame.key.get_pressed()
		speed = 8
		if keys[pygame.K_w]:
			paddleA.move(-speed)
		if keys[pygame.K_s]:
			paddleA.move(speed)
		if keys[pygame.K_UP]:
			paddleB.move(-speed)
		if keys[pygame.K_DOWN]:
			paddleB.move(speed)  
		
		# Check if the ball is bouncing against any of the 4 walls:
		if ball.rect.x > WIDTH-ball.r*2:
			scoreA+=1
			ball.velocity[0] = -ball.velocity[0]
		if ball.rect.x < 0:
			scoreB+=1
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


		SCREEN.fill(GREY)

		pygame.draw.line(SCREEN, WHITE, [WIDTH//2, 0], [WIDTH//2, HEIGHT], 5)

		all_sprites.update()
		all_sprites.draw(SCREEN)
		
		#Display scores:
		font = pygame.font.Font(None, 74)
		text = font.render(str(scoreA), 1, WHITE)
		SCREEN.blit(text, (250,10))
		text = font.render(str(scoreB), 1, WHITE)
		SCREEN.blit(text, (420,10))
		
		pygame.display.flip()
		clock.tick(FPS)


if __name__ == '__main__':
	main()

