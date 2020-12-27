"""
Pandemic/Disease Simulation: 
Simulates the spread of a virus. The simulation starts with
some population of "healthy balls" and one (or more) "infected balls", which float around
the screen in a random direction. If an infected ball collides with a healthy ball there
is some chance it passes on the infection. User can choose for some percent of the population
to "quarantine" (move at near zero velocity), time of infection, probability of infection, and 
some other paramters. Some basic results & stats are graphed/displayed on the screen

version 2: Added menu and ability for user to change parameter values

Last updated: 2020-12-27

Possible future updates:
- Add increased death rate if certain % of population infected (hospital capicity)
- Throw errors if parameter of wrong type
- Fix top left corner flashing ball bug
- Add instructions
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

# Simulation Constructor
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
        self.infection_prob = infection_prob
        self.percentage_quarantine = percentage_quarantine

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
            ball.infection(infection_time=self.infection_time)

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
        sim_font_med = pygame.font.Font("freesansbold.ttf",20)

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
        simulate, click = True, False
        k=0

        while simulate:
            self.population_container.update()
            screen.fill(BACKGROUND)

            #for k in range(self.simulation_length):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    simulate = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == True:
                        click = True   

            # menu button
            mx, my = pygame.mouse.get_pos()

            menu_button = pygame.Rect(340,525,120,32)  

            if menu_button.collidepoint((mx,my)):
                if click:
                    menu()

            click = False

            # update graph variables
            graph_height = graph.get_height()
            graph_width = graph.get_width()

            n_infected = len(self.infected_container)
            n_population = len(self.population_container)
            n_recovered = len(self.recovered_container)

            # update stat variables
            starting_pop = self.n
            deaths = starting_pop - n_population
            attack_rate = (starting_pop+n_infected+n_recovered+deaths)/starting_pop-1

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
            # FIX INFECTION PROB
            prob = self.infection_prob*0.33
            if num >= 1 - prob:
                infected_collision_group = pygame.sprite.groupcollide(
                    self.susceptible_container,
                    self.infected_container,
                    True,
                    False
                )

                for ball in infected_collision_group:
                    new_ball = ball.respawn(RED)
                    num = np.random.rand()
                    if num > self.percentage_quarantine:
                        ball.vel = np.random.rand(2)*4-2
                    else:
                        # or [0,0]
                        ball.vel = np.random.rand(2)*0.1-0.05

                    num = np.random.rand()
                    if num > self.percentage_quarantine:
                        new_ball.vel = np.random.rand(2)*4-2
                    else:
                        # or [0,0]
                        new_ball.vel = np.random.rand(2)*0.1-0.05

                    new_ball.infection(
                            infection_time = self.infection_time,
                            death_rate = self.death_rate
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

            #button
            menu_text = sim_font_med.render('Menu',True,BLACK)
            pygame.draw.rect(screen, LIGHT_GREY, menu_button)
            screen.blit(menu_text, (menu_button.x+35,menu_button.y+7))
            
            
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
        after, click = True, False
        while after:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    after = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == True:
                        click = True   

            mx, my = pygame.mouse.get_pos()
            if menu_button.collidepoint((mx,my)):
                if click:
                    menu()

            click = False

            self.population_container.update()
            screen.fill(BACKGROUND)

            # keep drawing the population for aesthetics 
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

def menu():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))       
    sim_font_large = pygame.font.Font("freesansbold.ttf",32)
    sim_font_med = pygame.font.Font("freesansbold.ttf",20)
    sim_font_small = pygame.font.Font("freesansbold.ttf",14)
    sim_font_vsmall = pygame.font.Font("freesansbold.ttf",10)

    pygame.display.set_caption("Epidemic Simulator: Menu")
    
    icon = pygame.image.load('/Users/Shane/projects/diseasesim/Disease-Simulation/images/coronavirus.png')
    pygame.display.set_icon(icon)

    menu_clock = pygame.time.Clock() 

    # STARTING PARAMETERS 
    starting_pop = 1500
    infection_time = 200
    infection_prob = 0.20
    death_rate = 0.05      
    percentage_quarantine = 0.75

    simulation_length = 2400

    population_size_text = str(starting_pop)
    infection_time_text = str(infection_time)
    infection_prob_text = str(infection_prob)
    death_rate_text = str(death_rate)
    percentage_quarantine_text = str(percentage_quarantine)

    population_input_rect = pygame.Rect(410,440,100,26)
    infection_time_input_rect = pygame.Rect(410,400,100,26)
    infection_prob_input_rect = pygame.Rect(410,280,100,26)
    death_rate_input_rect = pygame.Rect(410,320,100,26)
    percentage_quarantine_input_rect = pygame.Rect(410,360,100,26)

    start_button = pygame.Rect(340,525,120,32)

    run_menu, click = True, False
    pop_text_active = False
    infection_time_text_active = False
    infection_prob_text_active = False
    death_rate_text_active = False
    percentage_quarantine_text_active = False

    # Background balls / decoration
    background_container = pygame.sprite.Group()
    x = np.random.randint(10, 790)
    y = np.random.randint(10, 590)
    background_ball_vel = np.random.rand(2)*4-2
    background_ball = Ball(x,y, 800, 600, color=RED, velocity=background_ball_vel)
    background_container.add(background_ball)

    for ball in range(0,15):
        x = np.random.randint(10, 790)
        y = np.random.randint(10, 590)

        vel = np.random.rand(2)*4-2

        ball = Ball(x,y, 800, 600, color=GREY, velocity=vel)
        
        background_container.add(ball)
  
    while run_menu:
        screen.fill(BACKGROUND)
        background_container.update()
        background_container.draw(screen)
        # start button
        mx, my = pygame.mouse.get_pos()
    
        if start_button.collidepoint((mx,my)):
            if click:
                # generate new sim and launch it
                starting_pop = int(population_size_text)
                infection_time = int(infection_time_text)
                infection_prob = float(infection_prob_text)
                death_rate= float(death_rate_text)
                percentage_quarantine=float(percentage_quarantine_text)

                sim = Sim()
                sim.n_susceptible=int(starting_pop-starting_pop*percentage_quarantine - 1)
                sim.n_infected=1
                sim.n_quarantined=int(starting_pop*percentage_quarantine)
                sim.percentage_quarantine=percentage_quarantine

                sim.death_rate=death_rate
                sim.infection_time=infection_time
                sim.infection_prob=infection_prob

                sim.start()

        start_text = sim_font_med.render('Start',True,BLACK)
        pygame.draw.rect(screen, LIGHT_GREY, start_button)
        screen.blit(start_text, (start_button.x+35,start_button.y+7))

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run_menu = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == True:
                    click = True  

                if population_input_rect.collidepoint(event.pos):
                    pop_text_active = True
                else:
                    pop_text_active = False

                if infection_time_input_rect.collidepoint(event.pos):
                    infection_time_text_active = True
                else:
                    infection_time_text_active = False  

                if infection_prob_input_rect.collidepoint(event.pos):
                    infection_prob_text_active = True
                else:
                    infection_prob_text_active = False

                if death_rate_input_rect.collidepoint(event.pos):
                    death_rate_text_active = True
                else:
                    death_rate_text_active = False

                if percentage_quarantine_input_rect.collidepoint(event.pos):
                    percentage_quarantine_text_active = True
                else:
                    percentage_quarantine_text_active = False               

            if event.type == pygame.KEYDOWN:
                if pop_text_active == True:
                    if event.key == pygame.K_BACKSPACE:
                        if len(population_size_text) == 0:
                            pass
                        else:
                            population_size_text = population_size_text[:-1]
                    elif len(population_size_text) == 4:
                        pass
                    else:
                        population_size_text += event.unicode

                if infection_time_text_active == True:
                    if event.key == pygame.K_BACKSPACE:
                        if len(infection_time_text) == 0:
                            pass
                        else:
                            infection_time_text = infection_time_text[:-1]
                    elif len(infection_time_text) == 4:
                        pass
                    else:
                        infection_time_text += event.unicode

                if infection_prob_text_active == True:
                    if event.key == pygame.K_BACKSPACE:
                        if len(infection_prob_text) == 0:
                            pass
                        else:
                            infection_prob_text = infection_prob_text[:-1]
                    elif len(infection_prob_text) == 4:
                        pass
                    else:
                        infection_prob_text += event.unicode

                if death_rate_text_active == True:
                    if event.key == pygame.K_BACKSPACE:
                        if len(death_rate_text) == 0:
                            pass
                        else:
                            death_rate_text = death_rate_text[:-1]
                    elif len(death_rate_text) == 4:
                        pass
                    else:
                        death_rate_text += event.unicode

                if percentage_quarantine_text_active == True:
                    if event.key == pygame.K_BACKSPACE:
                        if len(percentage_quarantine_text) == 0:
                            pass
                        else:
                            percentage_quarantine_text = percentage_quarantine_text[:-1]
                    elif len(percentage_quarantine_text) == 4:
                        pass
                    else:
                        percentage_quarantine_text += event.unicode

        # Inputs
        if pop_text_active == True:
            pygame.draw.rect(screen, GREY, population_input_rect,1)
        else:
            pygame.draw.rect(screen, BLACK, population_input_rect,1)

        population_size_surface = sim_font_med.render(population_size_text, True, BLACK)
        screen.blit(population_size_surface, (population_input_rect.x+4,population_input_rect.y+4))

        if infection_time_text_active == True:
            pygame.draw.rect(screen, GREY, infection_time_input_rect,1)
        else:
            pygame.draw.rect(screen, BLACK, infection_time_input_rect,1)

        infection_time_surface = sim_font_med.render(infection_time_text, True, BLACK)
        screen.blit(infection_time_surface, (infection_time_input_rect.x+4,infection_time_input_rect.y+4))

        if infection_prob_text_active == True:
            pygame.draw.rect(screen, GREY, infection_prob_input_rect,1)
        else:
            pygame.draw.rect(screen, BLACK, infection_prob_input_rect,1)

        infection_prob_surface = sim_font_med.render(infection_prob_text, True, BLACK)
        screen.blit(infection_prob_surface, (infection_prob_input_rect.x+4,infection_prob_input_rect.y+4))

        if death_rate_text_active == True:
            pygame.draw.rect(screen, GREY, death_rate_input_rect,1)
        else:
            pygame.draw.rect(screen, BLACK, death_rate_input_rect,1)

        death_rate_surface = sim_font_med.render(death_rate_text, True, BLACK)
        screen.blit(death_rate_surface, (death_rate_input_rect.x+4,death_rate_input_rect.y+4))

        if percentage_quarantine_text_active == True:
            pygame.draw.rect(screen, GREY, percentage_quarantine_input_rect,1)
        else:
            pygame.draw.rect(screen, BLACK, percentage_quarantine_input_rect,1)

        percentage_quarantine_surface = sim_font_med.render(percentage_quarantine_text, True, BLACK)
        screen.blit(percentage_quarantine_surface, (percentage_quarantine_input_rect.x+4,percentage_quarantine_input_rect.y+4))

        # Menu Text
        menu_text = sim_font_large.render("Epidemic Simulator",True,BLACK)
        screen.blit(menu_text,(250,100))

        population_text = sim_font_small.render("Initial Population",True,BLACK)
        screen.blit(population_text,(260,440))
        population_subtext = sim_font_vsmall.render("Select the size of the starting population",True,BLACK)
        screen.blit(population_subtext,(198,457))        

        infect_time_text = sim_font_small.render("Length of Infection",True,BLACK)
        screen.blit(infect_time_text,(260,400))
        infect_time_subtext = sim_font_vsmall.render("Select how long the infection lasts",True,BLACK)
        screen.blit(infect_time_subtext,(198,417))  

        infect_prob_text = sim_font_small.render("Contagiousness",True,BLACK)
        screen.blit(infect_prob_text,(260,280))
        infect_prob_subtext = sim_font_vsmall.render("Choose how contagious the disease is",True,BLACK)
        screen.blit(infect_prob_subtext,(198,297))  

        death_text = sim_font_small.render("Death Rate",True,BLACK)
        screen.blit(death_text,(260,320))
        death_subtext = sim_font_vsmall.render("Choose the fatality rate",True,BLACK)
        screen.blit(death_subtext,(198,337))  

        quarantine_text = sim_font_small.render("Quarantine Rate",True,BLACK)
        screen.blit(quarantine_text,(260,360))       
        quarantine_subtext = sim_font_vsmall.render("What percent of the population quarantines?",True,BLACK)
        screen.blit(quarantine_subtext,(198,377))  

        pygame.display.update()
        menu_clock.tick(30)

#launch sim
if __name__ == "__main__":
    print('Welcome to Epidemic Simulator, have fun!')
    menu()