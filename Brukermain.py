#### INFORMASJON #### 
# Filnavn: brukermain.py
# Forfatter: Jone Måsøy, André Killingmoe og Eirik Kiland
# Inspirert av Maskinlæring i praktisk beslutningstaking av Simen Strandvold og Hans Petter Leines

# Git: https://github.com/beachviolence/bachelor.git


# Beskrivelse:
# Denne koden henter miljøet, trener på det og
# returnerer anbefalt handling og evt. strategien
# Det er denne koden som fungerer opp mot GUI'en

#### INKLUDERTE BIBLIOTEK ####

# Lisenser for Numpy kan leses på
# https://docs.scipy.org/doc/numpy-1.10.0/license.html
import numpy as np

# Lisenser for MatplotLib kan leses på
# https://matplotlib.org/users/license.html
import time
from os.path import exists
import os
from pyproj import Proj, transform
import geopy.distance
import math

# Inkluderte .py filer
from newlabyrinth import grid_world, print_values
from sauterlek import dy, dx, minx, miny, convertStartSlutt

#### HYPERPARAMETERE #### 
GAMMA = 0.9
ALPHA = 0.1
EPSILON = 0.1

#### GLOBALE VARIABLER ####
# Alle mulige handlinger
ALL_POSSIBLE_ACTIONS = ('U', 'D', 'L', 'R')

# Skrur av og på debugverktøy som grafer
DEBUG = True
# Div lagrede variabler
PREV_POLICY = {}
PREV_STATE = ()
PREV_Q = {}

# Antall episoder den skal trene ved neste trening
SECOND_EPISODES = 4000


#### FUNKSJONER ####
# Returnerer argmax og maxverdien fra en dict
def max_dict(d):
  max_key = None
  max_val = float('-inf')
  for k, v in d.items():
    if v > max_val:
      max_val = v
      max_key = k
  return max_key, max_val

# Velger en tilfeldig handling med sannsynlighet = epsilon
def random_action(a, eps=0.1):
  p = np.random.random()
  if p < (1 - eps):
    return a
  else:
    return np.random.choice(ALL_POSSIBLE_ACTIONS)

# Henter opp miljøet fra grid_world + startposisjonen
def run(epoch,Startposisjon,Sluttposisjon):
  startY,startX = convertStartSlutt(Startposisjon,Sluttposisjon)
  startstate = (startY,startX)
  grid, learn = grid_world(startstate)

  # Bestemmer om miljøet er likt eller om det skal
  # læres på nytt
  if learn:
    return q_learn(grid, epoch)
  else:
    return PREV_POLICY, grid.current_state()
  


# 
def q_learn(grid, epoch):

  global PREV_Q
  
  
  
  # Starter timer i debug modus
  if DEBUG: t0 = time.time()
  trigstart = False


    
  # Importerer start-tilstand
  start_state = grid.current_state()

  # Initsialiserer Q(s,a) ved første kjøring
  # hvis ikke henter den Q(s,a) fra forrige
  if epoch == 0:
    Q = {}
    states = grid.all_states()
    for s in states:
      Q[s] = {}
      for a in ALL_POSSIBLE_ACTIONS:
        Q[s][a] = 0
  else:
    Q = PREV_Q
    states = grid.all_states() 

  # Holder kontroll på hvor mange ganger Q[s] er oppdatert
  update_counts = {}
  update_counts_sa = {}
  for s in states:
    update_counts_sa[s] = {}
    for a in ALL_POSSIBLE_ACTIONS:
      update_counts_sa[s][a] = 1.0

  # Init variabler
  t = 1.0
  deltas = []
  sum_reward = []

  # Bestemmer antall episoder det skal trenes

  episode_func = 20000

  # Brukes ved løsning av komplekse miljø hvor det trengs
  # flere episoder
  
  if epoch == 0: 
    num_episodes = episode_func
  else: 
    num_episodes = SECOND_EPISODES

  # Starter trening
  for it in range(int(num_episodes)):
    if it % 100 == 0:
      t += 1e-2
    if it % 2000 == 0:
      if DEBUG:
        print("it:", it)

    # Istedenfor å generere en epsisode, spiller vi en
    # episode inne i treningen

    # Henter startstate og setter
    s = start_state 
    grid.set_state(s)
    
    # Den første (s, r) er start-tilstanden og 0 siden vi ikke
    # får en gevinst. Den siste (s, r) er den absorberende tilstanden
    # og den site gevinsten, og er per definisjon 0

    # Init-verdier 
    if not os.path.exists('NX_fil.npy'):
      a, _ = max_dict(Q[s])
    else:
      a, _ = max_dict(PREV_Q[s])
    biggest_change = 0
    sum_episode_rewards = []

    # Gjennomfører én episode
    while not grid.game_over():
      # Utfører en tilfeldig handling med sannsynlighet eps
      a = random_action(a, eps=EPSILON)

      # Beveger seg til valgt tilstand 
      r = grid.move(a)

      # Legger episodens gevinster i en liste
      sum_episode_rewards.append(r)

      # Neste state
      s2 = grid.current_state()
      ###################
      #print(s, s2)
      # Oppdaterer tellingen av Q(s,a)
      update_counts_sa[s][a] += 0.005

      #### OPPDATERINGEN AV Q(s,a)

      # Tar vare på gamle verdien av Q(s,a)
      old_qsa = Q[s][a]

      # Finner argmax_a(Q(s2,a)) og max_a(Q(s2,a))
      a2, max_q_s2a2 = max_dict(Q[s2])

      # Gjør oppdateringen av Q(s,a) i henhold til formel 12, side 20
      Q[s][a] = Q[s][a] + ALPHA*(r + GAMMA*max_q_s2a2 - Q[s][a])

      # Registrerer den største endringen gjort i Q(s,a) i løpet av episoden
      biggest_change = max(biggest_change, np.abs(old_qsa - Q[s][a]))

      # Holder kontroll på hvor mange ganger Q(s) er oppdatert
      update_counts[s] = update_counts.get(s,0) + 1

      # Neste tilstand blir nåværende tilstand
      s = s2
      # Neste handling blir nåværende handling
      a = a2
    
    # Legger største forandring av Q i en liste til bruk i graf
    deltas.append(biggest_change)

    # Legger samlet gevinst pr. episode i en liste til bruk i graf
    sum_reward.append(sum(sum_episode_rewards))

  # Finner strategien fra Q
  # og tilstands-verdifunksjonen V fra handlings-verdifunksjonen Q
  policy = {}
  V = {}
  for s in grid.actions.keys():
    a, max_q = max_dict(Q[s])
    policy[s] = a
    V[s] = max_q

  # Lagerer strategien til bruk i neste iterasjon
  global PREV_POLICY
  PREV_POLICY = policy
  

  
  # Brukes til debugging og demonstrering
  if DEBUG:
    # Stopper timer og utskrift av tid brukt
    t1 = time.time()
    print("Time elapsed: {}".format(t1-t0))

    # Finner laveste delta
    lowest_delta = min(deltas)
    print(lowest_delta)



    # Printer tid brukt i hver tilstand
    print("update counts:")
    total = np.sum(list(update_counts.values()))
    for k, v in update_counts.items():
      update_counts[k] = float(v) / total
    print_values(update_counts, grid)

    # Visualiserer miljø med gevinster
    rew = np.zeros((grid.height, grid.width))
    for i in range (grid.height):
      for j in range(grid.width):
        rew[i,j] = grid.rewards.get((i,j), 0)
 
    # Visualiserer verdifunksjonen
    val = np.zeros((grid.height, grid.width))
    for i in range (grid.width):
      for j in range(grid.height):
        val[i,j] = V.get((i,j), 0)

   
    #For å telle hvor mange piksler ruta går over
    l = 0
     # Visualiserer strategien fra start til mål
    route = rew
    pos_x, pos_y = start_state[1],start_state[0]
    
    #Definerer lister for omregning til latitude og longditude
    NorthList =[]
    EastList = []
    NorthEastArray = ()
    
    while route[pos_y,pos_x] != 5:
      route[pos_y,pos_x] = 5
      if policy.get((pos_y,pos_x)) == 'U': 
        pos_y -= 1
      elif policy.get((pos_y,pos_x)) == 'D': 
        pos_y += 1
      elif policy.get((pos_y,pos_x)) == 'L': 
        pos_x -= 1
      elif policy.get((pos_y,pos_x)) == 'R': 
        pos_x += 1
      l +=1

      ######### Regner tilbake til Northing og Easting. X- og Y-verdier ####################################
      reverse_ix = -round((pos_y * dx) + minx)
      reverse_iy = round((pos_x * dy) + miny)
      
      # Legger disse til en liste
      NorthList.append(reverse_ix)
      EastList.append(reverse_iy)
      
    #Omgjør xyz-koordinater til grader   
    inProj = Proj('+proj=utm +zone=33 +ellps=WGS84')
    outProj = Proj('+proj=longlat')
    EastList_np = np.array(EastList)
    EastList_np = np.column_stack(EastList_np)
    NorthList_np = np.array(NorthList)
    NorthList_np = np.column_stack(NorthList_np)
    
    
    #Initialiserer listene fyllt med 0er med like mange verdier som det finnes koordinater
    # i ruta
    x2 = np.zeros((1,len(NorthList_np)))
    y2 = np.zeros((1,len(NorthList_np)))
    
    # Transformerer hver koordinat fra xyz til grader og legger disse i en array
    for i in range(len(NorthList_np)):
      x2,y2 = transform(inProj,outProj,EastList_np[i],NorthList_np[i])
    NorthEastArray = np.column_stack((y2, x2)) 
    
   
    #Gjør om arrayen til liste slik at HMI kan lese det enkelt
    FerdigList =  NorthEastArray.tolist() 

    #Regner ut avstanden til ruta
    Distanse = 0
    for i in range(len(FerdigList)):
      if i == len(FerdigList) - 1: 
        break
      koordinat1 = FerdigList[i]
      koordinat2 = FerdigList[i+1]
      EnkelDistanse = geopy.distance.geodesic(koordinat1, koordinat2).km 
      Distanse = Distanse + EnkelDistanse   
    
    #Regner ut hvor lang tid ruta tar ved en viss hastighet
    # Distanse / fart = tid
    NautiskMil = Distanse / 1.852
    Knop = 15.5
    Tid = NautiskMil / Knop
    Antallminutter = Tid * 60
    Antallsekunder = ((Antallminutter % 1)*100) * 60/100
    
    print(math.trunc(Antallminutter), ' min ', Antallsekunder, ' s')
    
    #Lagrer så ruta og distansen til fil som HMI kan lese fra
    np.save('Ruta.npy', FerdigList)
    np.save('Distanse.npy', NautiskMil) 

  # Returnerer strategien og start-tilstand
  return policy, start_state