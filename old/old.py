"""
Pandemic/Disease Simulation: 
Simulates the spread of a virus. The simulation starts with
some population of "healthy balls" and one (or more) "infected balls", which float around
the screen in a random direction. If an infected ball collides with a healthy ball there
is some chance it passes on the infection. User can choose for some percent of the population
to "quarantine" (move at near zero velocity), time of infection, probability of infection, and 
some other paramters. Some basic results & stats are graphed/displayed on the screen

Last updated: 2020-12-27

Possible future updates:
- Add increased death rate if certain % of population infected (hospital capicity)
- Add start, stop buttons
- Let user input parameter values on menu screen
- Fix sticking on wall & top left corner flashing ball bug
"""

import numpy as np
import pygame
import sys

# Color Palette
WHITE=(255,255,255)
BLACK=(0,0,0)
BACKGROUND = WHITE

RED = (247,82,95)
YELLOW = (214,198,1)
BLUE = 	(58,141,222)
GREY=(113,113,113)
LIGHT_GREY=(223,223,223)

# Disease & Simulation Parameters
infection_time = 400
infection_prob = 0.05
death_rate = 0.25
starting_pop = 600
simulation_length = 2300

percentage_quarantine = .75

# Text variables
starting_pop = starting_pop
deaths = 0
attack_rate = 0
n_recovered = 0
n_infected = 0


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
 
    def infection(self, infection_time=infection_time, death_rate=death_rate):
        self.infected=True
        self.infection_time=infection_time
        self.death_rate=death_rate

# SIMULATION
class Sim:
    def __init__(self, width=800, height=600):
        self.WIDTH=width
        self.HEIGHT=height

        self.susceptible_container = pygame.sprite.Group()
        self.infected_container = pygame.sprite.Group()
        self.recovered_container = pygame.sprite.Group()
        self.population_container = pygame.sprite.Group()

        #fixed time
        self.simulation_length = simulation_length

        self.infection_time = infection_time
        self.death_rate = death_rate

        self.n_quarantined = 0

    def start(self):

        self.n=self.n_susceptible+self.n_infected+self.n_quarantined

        # populate healthy, non quarantine, balls
        for b in range(self.n_susceptible):
            #random location not on edge
            x = np.random.randint(10, self.WIDTH-10)
            y = np.random.randint(10, self.HEIGHT-10)

            # random velocity ordered pair, between -2 and 2
            vel = np.random.rand(2)*4-2

            ball = Ball(x,y, self.WIDTH, self.HEIGHT, color=GREY, velocity=vel)
            
            self.susceptible_container.add(ball)
            self.population_container.add(ball)

        # populate infected ball(s)
        for b in range(self.n_infected):
            # could instead choose to start infected ball in center to remove
            # random initial condition
            x = np.random.randint(10, self.WIDTH-10)
            y = np.random.randint(10, self.HEIGHT-10)

            vel = np.random.rand(2)*4-2

            ball = Ball(x,y, self.WIDTH, self.HEIGHT, color=RED, velocity=vel)
            ball.infection()

            self.infected_container.add(ball)
            self.population_container.add(ball)

        # populate healthy, quarantine, balls
        for b in range(self.n_quarantined):
            x = np.random.randint(10, self.WIDTH-10)
            y = np.random.randint(10, self.HEIGHT-10)

            # or just [0,0]
            vel = np.random.rand(2)*0.1-0.05

            ball = Ball(x,y, self.WIDTH, self.HEIGHT, color=GREY, velocity=vel)
            
            self.susceptible_container.add(ball)
            self.population_container.add(ball)

        pygame.init()
        screen = pygame.display.set_mode((self.WIDTH,self.HEIGHT))

        sim_font = pygame.font.Font("freesansbold.ttf",12)

        pygame.display.set_caption("Disease Simulation")
        
        # Icon by Freepik: https://www.freepik.com/
        icon = pygame.image.load('/Users/Shane/projects/diseasesim/Disease-Simulation/images/coronavirus.png')
        pygame.display.set_icon(icon)

        graph = pygame.Surface((self.WIDTH//4,self.HEIGHT//4))
        graph.fill(LIGHT_GREY)
        graph.set_alpha(230)
        graph_position = (self.WIDTH//40,self.HEIGHT//40)

        clock = pygame.time.Clock()

        # SIM LOOP
        simulate = True
        k=0

        while simulate:
            #for k in range(self.simulation_length):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    simulate = False
                    pygame.quit()
                    sys.exit()

            self.population_container.update()
            screen.fill(BACKGROUND)

            # update graph variables
            graph_height = graph.get_height()
            graph_width = graph.get_width()

            n_infected = len(self.infected_container)
            n_population = len(self.population_container)
            n_recovered = len(self.recovered_container)

            # update stat variables
            starting_pop = self.n
            deaths = starting_pop - n_population
            attack_rate = (n_infected+n_recovered+deaths)/starting_pop

            k+=1
            if k >= self.simulation_length:
                break

            #update graph 

            t = int((k/self.simulation_length)*graph_width)
            y_infected = int(graph_height-(n_infected/n_population)*graph_height)
            y_dead = int(((self.n - n_population)/self.n)*graph_height)
            y_recovered = int((n_recovered/n_population)*graph_height)
            
            graph_fig = pygame.PixelArray(graph)
            graph_fig[t, y_infected:] = pygame.Color(*RED)
            graph_fig[t, :y_dead] = pygame.Color(*YELLOW)
            graph_fig[t, y_dead:y_dead+y_recovered] = pygame.Color(*BLUE)

            # Likelihood to pass on virus
            num = np.random.rand()
            if num >= 1 - infection_prob:
                infected_collision_group = pygame.sprite.groupcollide(
                    self.susceptible_container,
                    self.infected_container,
                    True,
                    False
                )

                for ball in infected_collision_group:
                    new_ball = ball.respawn(RED)
                    num = np.random.rand()
                    if num > percentage_quarantine:
                        ball.vel = np.random.rand(2)*4-2
                    else:
                        # or [0,0]
                        ball.vel = np.random.rand(2)*0.1-0.05
                    

                    num = np.random.rand()
                    if num > percentage_quarantine:
                        new_ball.vel = np.random.rand(2)*4-2
                    else:
                        # or [0,0]
                        new_ball.vel = np.random.rand(2)*0.1-0.05

                    new_ball.infection(
                            self.infection_time,
                            self.death_rate
                    )
                    self.infected_container.add(new_ball)
                    self.population_container.add(new_ball)

            recovered=[]
            for ball in self.infected_container:
                if ball.recovered:
                    new_ball = ball.respawn(BLUE)
                    self.recovered_container.add(new_ball)
                    self.population_container.add(new_ball)
                    recovered.append(ball)

            if len(recovered)>0:
                self.infected_container.remove(*recovered)
                self.population_container.remove(*recovered)

            self.population_container.draw(screen)

            del graph_fig
            graph.unlock()
            screen.blit(graph, graph_position)

            #update text
            
            population_text = sim_font.render(f"Inital Population: {starting_pop}",True,BLACK)
            screen.blit(population_text,(20,167))

            deaths_text = sim_font.render(f"Deaths: {deaths}",True,BLACK)
            screen.blit(deaths_text,(20,215))

            attackrate_text = sim_font.render(f"Attack Rate: {round(attack_rate,4)}",True,BLACK)
            screen.blit(attackrate_text,(20,179))

            infected_text = sim_font.render(f"Currently Infected: {n_infected}",True,BLACK)
            screen.blit(infected_text,(20,191))

            recovered_text = sim_font.render(f"Recovered: {n_recovered}",True,BLACK)
            screen.blit(recovered_text,(20,203))            

            pygame.display.flip()
            clock.tick(30)
            
        # After sim is complete, stay on sim screen, have balls bouncing around but 
        # disease mechanics turned off, lets user look at graph & stats
        after = True
        while after:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    sys.exit()
            
            self.population_container.update()
            screen.fill(BACKGROUND)

            self.population_container.draw(screen)

            screen.blit(graph, graph_position)

            screen.blit(population_text,(20,167))
            screen.blit(deaths_text,(20,215))
            screen.blit(attackrate_text,(20,179))
            screen.blit(infected_text,(20,191))
            screen.blit(recovered_text,(20,203))

            pygame.display.update()
            clock.tick(30)

        print('This shouldn\'t print')        

#turn this into start button
if __name__ == "__main__":
    sim = Sim()
    sim.n_susceptible=int(starting_pop-starting_pop*percentage_quarantine - 1)
    sim.n_infected=1
    sim.n_quarantined=int(starting_pop*percentage_quarantine)
    sim.start()