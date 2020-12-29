import numpy as np
import pygame

# Color Palette
WHITE=(255,255,255)
BLACK=(0,0,0)

RED = (247,82,95)
YELLOW = (214,198,1)
BLUE = 	(58,141,222)
GREY=(113,113,113)
LIGHT_GREY=(223,223,223)

# Ball Constructor
class Ball(pygame.sprite.Sprite):
    def __init__(
        self,x,y,width,height,color=GREY,radius=5,velocity=[0,0]
    ):
        super().__init__()
        self.image = pygame.Surface(
            [radius*2,radius*2]
        )
        self.image.fill(-1)
        pygame.draw.circle(
            self.image, color, (radius, radius), radius
        )

        self.rect = self.image.get_rect()
        self.pos = np.array([x,y], dtype=np.float64)
        self.vel = np.asarray(velocity,dtype=np.float64)

        self.infected = False
        self.recovered = False

        self.WIDTH=width
        self.HEIGHT=height
    
    def update(self):
        self.pos += self.vel
        x,y=self.pos

        # Bounce off the walls
        if x <= 0 or x >= self.WIDTH - 10: 
            self.vel[0] *= -1
        if y <= 0 or y >= self.HEIGHT - 10: 
            self.vel[1] *= -1

        self.rect.x=x
        self.rect.y=y

        if self.infected:
            self.infection_time -= 1

            if self.infection_time == 0:
                self.infected = False
                num = np.random.rand()
                if self.death_rate > num:
                    #built in function in sprite class
                    self.kill()
                else:
                    self.recovered = True

    def respawn(self,color,radius=5):
        return Ball(
            self.rect.x,
            self.rect.y,
            self.WIDTH,
            self.HEIGHT,
            color=color,
            velocity=self.vel
        )
 
    def infection(self, infection_time=0, death_rate=0):
        self.infected=True
        self.infection_time=infection_time
        self.death_rate=death_rate
