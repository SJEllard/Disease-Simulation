"""
Disease Simulation


"""

import numpy as np
import pygame
import sys

WHITE=(255,255,255)
BLACK=(0,0,0)

GREY=(133,133,133)
RED=(170,20,35)
BLUE=(75,95,160)
GREEN=(150,180,150)
BACKGROUND = WHITE


# Ball Constructor
class Ball(pygame.sprite.Sprite):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        color=GREY,
        radius=5,
        velocity=[0,0],
    ):
        super().__init__()
        self.image = pygame.Surface(
            [radius*2,radius*2]
        )
        self.image.fill(BACKGROUND)
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


    # how long does infection last & mortality rate 
    def infection(self, infection_time=200, death_rate=0.02):
        self.infected=True
        self.infection_time=infection_time
        self.death_rate=death_rate

class Sim:
    def __init__(self, width=800, height=600):
        self.WIDTH=width
        self.HEIGHT=height

        self.susceptible_container = pygame.sprite.Group()
        self.infected_container = pygame.sprite.Group()
        self.recovered_container = pygame.sprite.Group()
        self.population_container = pygame.sprite.Group()

        self.steps = 2000
        self.infection_time = 200
        self.death_rate = 0.02

    def start(self):

        self.n=self.n_susceptible+self.n_infected

        for b in range(self.n_susceptible):
            #random location not on edge
            x = np.random.randint(6, self.WIDTH-6)
            y = np.random.randint(6, self.HEIGHT-6)

            # velocity ordered pair, 2 numbers between -2 and 2
            vel = np.random.rand(2)*4-2

            ball = Ball(x,y, self.WIDTH, self.HEIGHT, color=GREY, velocity=vel)
            
            self.susceptible_container.add(ball)
            self.population_container.add(ball)

        for b in range(self.n_infected):
            x = np.random.randint(5, self.WIDTH-5)
            y = np.random.randint(5, self.HEIGHT-5)

            vel = np.random.rand(2)*4-2

            ball = Ball(x,y, self.WIDTH, self.HEIGHT, color=RED, velocity=vel)
            ball.infection()

            self.infected_container.add(ball)
            self.population_container.add(ball)

        pygame.init()
        screen = pygame.display.set_mode((self.WIDTH,self.HEIGHT))
        clock = pygame.time.Clock()
        pygame.display.set_caption("Disease Simulation")

        # Icon, image by Freepik: https://www.freepik.com/
        icon = pygame.image.load('/Users/Shane/projects/diseasesim/Disease-Simulation/images/coronavirus.png')
        pygame.display.set_icon(icon)

        # SIM LOOP
        turn_on = True
        while turn_on:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    turn_on = False
                    pygame.quit()
                    sys.exit()

            self.population_container.update()
            screen.fill(BACKGROUND)

            # Likelihood to pass on virus
            probability = 0.05
            num = np.random.rand()
            if num >= 1 - probability:
                infected_collision_group = pygame.sprite.groupcollide(
                    self.susceptible_container,
                    self.infected_container,
                    True,
                    False
                )

                for ball in infected_collision_group:
                    new_ball = ball.respawn(RED)
                    ball.vel = np.random.rand(2)*4-2
                    new_ball.vel = np.random.rand(2)*4-2
                    new_ball.infection(
                            self.infection_time,
                            self.death_rate
                    )
                    self.infected_container.add(new_ball)
                    self.population_container.add(new_ball)

            recovered=[]
            for ball in self.infected_container:
                if ball.recovered:
                    new_ball = ball.respawn(GREEN)
                    self.recovered_container.add(new_ball)
                    self.population_container.add(new_ball)
                    recovered.append(ball)

            if len(recovered)>0:
                self.infected_container.remove(*recovered)
                self.population_container.remove(*recovered)

            self.population_container.draw(screen)
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()

if __name__ == "__main__":
    sim = Sim()
    sim.n_susceptible=299
    sim.n_infected=1

    sim.start()