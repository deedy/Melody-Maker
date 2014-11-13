import matplotlib.pyplot as plt
import pylab
import sys
import time
import random
import numpy as np
import operator
import pdb
import math
from logger import Logger
import read_music
from IPython.core.debugger import Tracer
import AudioBite
import cPickle as pickle
from main import preprocessor
import os
import re
import math

#----- GLOBALS ----------

POPULATION = 1000
EVALUATIONS = 0
BEST_DISTANCE_SO_FAR = sys.maxint
MAX_EVALUTATIONS = 100000
SELECTION_METHOD = 'truncation'
NUMBER_OF_HALFBEATS_PER_PERIOD = 8
LOGGER = Logger('log.txt', True)
SAVE_DIR_FOR_SOUNDS = 'data'
SONG_AUDIOBITE = None # Song AudioBite
NOTE_AUDIOBITES = None # list of Note AudioBite


RESET_NOTES = False
OVERWRITE_SONG = False
DATA_DIR = 'data'
PROCESSED_DIR = 'processed'
NOTESET_DIR = DATA_DIR + '/noteset/'
INPUT_SONG = DATA_DIR + '/songs/full_scale.wav'
PROCESSED_NOTESETS = PROCESSED_DIR + '/noteset.pik'
PROCESSED_SONG = '{0}.pik'.format(os.sep.join([PROCESSED_DIR] + INPUT_SONG.split(os.sep)[1:]))

# -- SETUP FUNCTIONS ----

def setup():
  if RESET_NOTES or not os.path.isfile(PROCESSED_NOTESETS):
    preprocessor(NOTESET_DIR, PROCESSED_NOTESETS)
  if OVERWRITE_SONG or not os.path.isfile(PROCESSED_SONG):
    preprocessor(INPUT_SONG, PROCESSED_SONG)
  print('Loading notes...')
  note_set = pickle.load( open( PROCESSED_NOTESETS, 'rb' ) )
  print('Loading song...')
  song_sample = pickle.load( open( PROCESSED_SONG, 'rb' ) )
  note_dict = {}
  for note in note_set:
    note_str  = re.search(r'[A-G]b?[0-9]',note.original_path).group()
    if note_str:
      note_dict[note_str] = note
  return (song_sample,  note_dict)

# -- END SETUP FUNCTIONS --

def main():
  global BEST_DISTANCE_SO_FAR
  SONG_AUDIOBITE, NOTE_AUDIOBITES = setup()
  #numsamples ~= 256 * windows
  # numsamples /44100. = time in seconds
  Tracer()()
  evosound = EvolvedSound()
  Tracer()()
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
def mutation(sound):
  # take a random note and change it
  random_i = random.randint(0,len(sound.note_list)-1)
  # pick random note

  # Maybe change its window?
  pass


#
def crossover(dad,mom):
  '''
  Takes two songs and performs a 2 slice crossover to return two songs.
  '''
  # Take two random slices and then swap
  pass

# ----- SELECTION METHODS ----------------

def truncation(songs):
  '''
  Selects the top portion of the population to reproduce
  Precondition: songs is sorted based on song distance
  '''
  return songs[:POPULATION]


# ----- REPRESENTATION ----------------

DEFAULT_PERIOD_MS = 1000
class EvolvedSound(object):
  '''
  A representation of the sound object we are creating.
  The representation is a tuple: (period (milliseconds) * note list list)
  The note list list contains the notes in one "halfbeat".
  The "halfbeat" is defined as the period/NUMBER_OF_HALFBEATS_PER_PERIOD.
  '''
  def __init__(self):
    Tracer()()
    self.period = DEFAULT_PERIOD_MS
    song_len_ms = 1000*(SONG_AUDIOBITE.num_samples / 44100.)
    self.halfbeats = int(math.floor(NUMBER_OF_HALFBEATS_PER_PERIOD * (song_len_ms / self.period)))

    note_list = []
    for i in len(self.halfbeats):
      if random.random() < 0.5:
        note_list.append([])
      else:
        note_list.append([random.choice(NOTE_AUDIOBITES.keys())])
    self.note_list = note_list
    Tracer()()
    self.distance = self.calculate_distance(sound_tuple)

  def __str__(self):
    semicolon_delimited_lst_str = '[[' + ';'.join(map(str,self.note_list[0])) + ']'
    for n in self.note_list[1:]:
      semicolon_delimited_lst_str += ';[' + ';'.join(map(str,n)) + ']'
    semicolon_delimited_lst_str += ']'
    return '"%d;%s"' % (self.period,semicolon_delimited_lst_str)

  def calculate_distance(self,wav_file):
    pass
    # TODO compare song to input wav_file

  def save_sound(self,filename):
    halfbeat = float(self.period)/NUMBER_OF_HALFBEATS_PER_PERIOD
    read_music.save_representation_as_song(self,SAVE_DIR_FOR_SOUNDS,filename,halfbeat)



if __name__ == '__main__':
  main()
