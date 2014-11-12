import matplotlib.pyplot as plt
import pylab
import sys
import time
import random
import numpy as np
import operator
import pdb
import math

#----- GLOBALS ----------

POPULATION = 1000
EVALUATIONS = 0
BEST_DISTANCE_SO_FAR = sys.maxint
MAX_EVALUTATIONS = 100000
SELECTION_METHOD = truncation

# -- SETUP FUNCTIONS ----

def setup():
 pass #TODO any setup?

# -- END SETUP FUNCTIONS --

def main():
  global BEST_DISTANCE_SO_FAR
  setup()

  #GENERATING RANDOM SONGS
  music_samples = []
  for n in range(POPULATION*2):
    music_samples.append() # Append random music representation
  music_samples.sort(key=lambda e: e.dist) # Sort based on distance / fitness (whatever we're naming it)
  music_samples = music_samples[:POPULATION]

  best_dist = music_samples[0].dist

  print 'Starting evolution...'

  while EVALUATIONS < MAX_EVALUTATIONS:
    new_music_samples = []
    for m in music_samples:
      new_music_samples.append(m) #Elitism 

    #Variation step
    for n in range(len(music_samples)):
      #select random parents: 
      if random.randint(1,10) <= 4: # P_CROSSOVER (probability that we crossover, rewrite, this looks bad)
        m1 = random.choice(music_samples)
        m2 = random.choice(music_samples)
        son, daughter = crossover(m1, m2)
        new_music_samples.append(son)
        new_music_samples.append(daughter) 
      else:
        child = mutation(music_samples[n])
        new_music_samples.append(child)

    #Selection step
    new_music_samples.sort(key=lambda e: e.dist)
    music_samples = SELECTION_METHOD(new_function_lst) 

    print `EVALUATIONS` + " " + `music_samples[0].dist`
    BEST_DISTANCE_SO_FAR = music_samples[0].dist

  #Saving equations and figures
  # TODO Some sort of saving of the log
  new_file = open('music_logs/'+`music_samples[0].dist` + '.txt','w')
  new_file.write(print_tree(functions_lst[0].tree))
  new_file.close()



# ----- VARIATION METHODS ----------------

# Hill climber
# Replaces a random node with a tree
# passed in TreeNode object
# Returns new Equation object
def mutation(song):
  pass


# Takes two trees and combines them together to return two Equations
def crossover(dad,mom):
  pass

# ----- SELECTION METHODS ----------------

def truncation(songs):
  '''
  Selects the top portion of the population to reproduce
  Precondition: songs is sorted based on song distance
  '''
  return songs[:POPULATION]

if __name__ == '__main__':
  main()