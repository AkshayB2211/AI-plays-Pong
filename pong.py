
import pygame, sys
from pygame.locals import *
from pong_env import Paddle, Ball

FPS = 30
WIDTH = 700
HEIGHT = 500

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (150, 150, 150)

def main():
	global SCREEN
	pygame.init()

	SCREEN = pygame.display.set_mode((WIDTH,HEIGHT))
	pygame.display.set_caption("PONG")

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
		if pygame.sprite.collide_rect(ball, paddleB) and ball.velocity[0]>0 :
			ball.bounce()

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


if __name__ == '__main__':
	main()

