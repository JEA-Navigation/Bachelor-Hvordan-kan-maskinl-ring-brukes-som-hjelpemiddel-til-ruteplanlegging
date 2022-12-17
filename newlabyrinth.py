#### INFORMASJON #### 
# Filnavn: newlabyrinth.py
# Forfatter: Jone Måsøy, André Killingmoe og Eirik Kiland
# Inspirert av Maskinlæring i praktisk beslutningstaking av Simen Strandvold og Hans Petter Leines

# Beskrivelse:
# Denne koden generer miljøet som er lesbart
# for brukermain.py eller main.py koden.

# Importerte biblioteker
import numpy as np
from sauterlek import nx, ny, pixels, mazes 

#### HYPERPARAMETERE ####
# Gevinster
GOAL_REWARD = 10000
LAND_REWARD = -10
SHALLOW_REWARD = -5
KINDASHALLOW_REWARD = -3
WAYPOINT_REWARD = 0

STEP_COST = -(60/nx) #For å gjøre denne dynamisk
DYPGANG = -10
vekting = 1.2/nx   #For å gjøre denne dynamisk


# Størrelse på manuelt miljø og antall hinder ønsket
GRID_HEIGHT = nx
GRID_WIDTH = ny
NUM_OBSTACLES = GRID_HEIGHT

# Initsialiserer tilfeldig eller manuelt miljø
RANDOM_REWARDS = False
MAZE = mazes(2)

## GLOBALE VARIABLER ##
PREV_REWARDS = {}
last_action = None
firstscan = True


#### KLASSE SOM INNEHOLDER MILJØET ####
class Grid:
    def __init__(self, height, width, start):
        self.height = height
        self.width = width
        self.i = start[0]
        self.j = start[1]

    # Setter gevinster og lovlige handlinger
    def set(self, rewards, actions):
        self.rewards = rewards
        self.actions = actions

    # Setter tilstanden
    def set_state(self, s):
        self.i = s[0]
        self.j = s[1]

    # Returnerer nåværende tilstand
    def current_state(self):
        return(self.i, self.j)



    # Beveger beslutningstakeren i miljøet
    def move(self, action):
        global last_action
        global firstscan
        # Sjekker om det er en lovlig handling
        ekstrakost = 0
        if action in self.actions[(self.i, self.j)]:
            if action == 'U':
                self.i -= 1
            elif action == 'D':
                self.i += 1
            elif action == 'L':
                self.j -= 1
            elif action == 'R':
                self.j += 1
        # Returnerer gevinst for neste tilstand
        return (self.rewards.get((self.i, self.j), 0))

    # Sjekker om episoden er ferdig
    def game_over(self):
        # True om beslutningstakeren er i mål
        return self.rewards[self.i, self.j] == GOAL_REWARD
    # Retunerer en dict med alle tilstander
    def all_states(self):
        return set(self.actions.keys()) | set(self.rewards.keys())

#### KONSTRUKSJON AV MILJØ ####

# Konstruerer miljø som en dict
def make_grid(y, x, num_obstacles = 0,startstate = (1,1)):
    g = Grid(y, x, startstate)
    rewards = {}

    # Legger til mulige handlinger i hver tilstand
    actions = {
        startstate: ('U', 'D', 'R', 'L'),
        (y-1,x-1): ('U', 'L'),
        (0, x-1): ('D', 'L'),
        (y-1, 0): ('U', 'R'),
        (0, 0): ('D', 'R')
    }

    for i in range(1, x-1):
        actions[(0,i)] = ('D', 'R', 'L')
        actions[(y-1,i)] = ('U', 'R', 'L')
    for j in range(1, y-1):
        actions[(j,0)] = ('U', 'D', 'R')
        actions[(j,x-1)] = ('U', 'D', 'L')
    for k in range(1,x-1):
        for l in range(1,y-1):
            actions[(l,k)] = ('U', 'D', 'R', 'L')
            
    # Legger til steg-gevinst i hver tilstand
    for i in range(x):
        for j in range(y):
            samletreward = 0
            if pixels[(j,i)] > DYPGANG:
                samletreward = samletreward + LAND_REWARD + STEP_COST
            elif pixels[(j,i)] < 9*DYPGANG:
                samletreward = samletreward + STEP_COST
            else:
                dybde = pixels[(j,i)]
                samletreward = samletreward + STEP_COST + vekting*(dybde/(8*DYPGANG) - 1 - 1/8)
            rewards[(j,i)] = samletreward      

    # Leser og tolker labyrinter hentet fra filen sauterlek.py
    if not RANDOM_REWARDS:
        labyrint = MAZE 
        k = 0
        l = 0
        for i in labyrint:
            for j in i:
                if j==10: rewards[(l,k)] = GOAL_REWARD
                k= k+1
            k = 0
            l = l+1
    
    # Lager tilfeldige hindringer i miljøet
    else:
        for _ in range(num_obstacles):
            rewards[(np.random.randint(0,y-1),np.random.randint(0,x-1))] = LAND_REWARD 
        for _ in range(num_obstacles):
            rewards[(np.random.randint(0,y-1),np.random.randint(0,x-1))] = SHALLOW_REWARD 
        rewards[(y-1,x-1)] = GOAL_REWARD
        rewards[startstate] = STEP_COST

    # Setter handlinger og gevinster i klassen Grid
    g.set(rewards, actions)

    # Returnerer et element av klassen Grid
    return g

#### MANUELT MILJØ ####
def manual_grid(startstate):
    # Lager grid [y,x] stor 
    g = make_grid(GRID_HEIGHT,GRID_WIDTH,NUM_OBSTACLES,startstate)
    # Sier at den skal trene hver gang
    train = True
    # Setter startposisjon
    s = startstate
    g.set_state(s)
    # Returnerer element av klassen grid og variablen train
    return g, train

# Funksjonen hentet opp i main.py som inneholder
# hele miljøet i objektet grid
def grid_world(startstate):
    return manual_grid(startstate)

#### PRINT FUNKSJONER ####
def print_values(V, g):
    for i in range(g.height):
        print("-------------------")
        for j in range(g.width):
            v = V.get((i,j), 0)
            if v >= 0:
                print("  %.2f  | " % v, end="")
            else:
                print(" %.2f  |" % v, end=" ") 
        print("")

def print_policy(P, g):
    for i in range(g.height):
        print("-------------------")
        for j in range(g.width):
            a = P.get((i, j), ' ')
            print("  %s  |" % a, end="")
        print("")

