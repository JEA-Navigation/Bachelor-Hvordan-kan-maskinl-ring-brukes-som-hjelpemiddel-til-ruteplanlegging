#### INFORMASJON #### 
# Filnavn: main.py
# Forfatter: Simon Strandvold og Hans Petter Leines
# Git: https://github.com/beachviolence/bachelor.git

# Inspirert av kursmateriell fra LazyProgrammer Inc. med tillatelse

# Beskrivelse:
# Denne koden henter miljøet, trener på det og
# returnerer anbefalt handling og evt. strategien

#### INKLUDERTE BIBLIOTEK ####

# Lisenser for Numpy kan leses på
# https://docs.scipy.org/doc/numpy-1.10.0/license.html
import numpy as np

# Lisenser for MatplotLib kan leses på
# https://matplotlib.org/users/license.html
import matplotlib.pyplot as plt
import pickle
import time
from os.path import exists

# Inkluderte .py filer
from newlabyrinth2 import grid_world, print_values, print_policy
from sauterlek2 import dy, dx, minx, miny

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
SECOND_EPISODES = 1000

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

# Henter opp miljøet fra grid_world
def run(epoch):
  grid, learn = grid_world()

  # Bestemmer om miljøet er likt eller om det skal
  # læres på nytt
  if learn:
    return q_learn(grid, epoch)
  else:
    return PREV_POLICY, grid.current_state()

#Lager en BOOL verdi for å sjekke om den har lært noe tidligere på denne PC

file_exists = exists('Q_verdier.pkl')

# 
def q_learn(grid, epoch):
  global PREV_Q

  # Starter timer i debug modus
  if DEBUG: t0 = time.time()
  
  
  #Sjekker om eksisterende Q verdier i fil eksisterer
  #Hvis ikke hopper den over denne løkka
  if file_exists:
    pickle_fil = open('Q_verdier.pkl', 'rb')
    PREV_Q = pickle.load(pickle_fil)
    pickle_fil.close()
    
  
  # Importerer start-tilstand
  start_state = grid.current_state()

  # Initsialiserer Q(s,a) ved første kjøring
  # hvis ikke henter den Q(s,a) fra forrige
  if epoch == 0 and not file_exists:
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
  # Funksjon er funnet ved regressjon
  #episode_func = 18.66 * grid.width*grid.height + 5932.01
  
  episode_func = 10000

  # Brukes ved løsning av komplekse miljø hvor det trengs
  # flere episoder
  
  
  if epoch == 0 and not file_exists: num_episodes = episode_func
  else: num_episodes = SECOND_EPISODES

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
    a, _ = max_dict(Q[s])
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

    # Plotter forandringen i delta
    plt.plot(deltas)
    plt.show()
    
    # Plotter oppnådd gevinst pr episode
    plt.plot(sum_reward)
    plt.show()

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
    plt.imshow(rew)
    plt.colorbar()
    plt.show()

    # Visualiserer verdifunksjonen
    val = np.zeros((grid.height, grid.width))
    for i in range (grid.width):
      for j in range(grid.height):
        val[i,j] = V.get((i,j), 0)
    plt.imshow(val)
    plt.colorbar()
    plt.show()

    # Visualiserer strategien fra start til mål
    route = rew
    pos_x, pos_y = start_state[1],start_state[0]
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
      ###### PRINTER POSISJON(ix, iy) I RUTENETT FOR RUTA/STRATEGIEN #########
      print(pos_x, pos_y)
      
      ######### Regner tilbake til Northing og Easting. X- og Y-verdier ####################################
      reverse_ix = -(round((pos_y * dx) + minx))
      reverse_iy = -(round((pos_x * dy) + miny))
      print(reverse_iy, reverse_ix)
      # Plotter strategien til mål
      
    plt.imshow(route)
    plt.colorbar()
    plt.show()
    

    # Printfunksjoner
    print("rewards:")
    print_values(grid.rewards, grid)
    print("values:")
    print_values(V, grid)
    print("policy:")
    print_policy(policy, grid)

 
  # Lagrer Q i ei fil som kan hentes opp ved ny kjøring
  
  PREV_Q = Q
  output = open('Q_verdier.pkl', 'wb')
  pickle.dump(PREV_Q, output)
  output.close()
  
  # Returnerer strategien og start-tilstand
  return policy, start_state

# Kjører trening på valgt miljø og printer anbefalt handling
if __name__ == "__main__":
  epoch = 0
  while True:
    input("Trykk enter")
    policy, s = run(epoch)
    action = policy.get(s)
    print("recommended action:")
    print(action)
    epoch += 1