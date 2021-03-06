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
import copy
import cPickle as pickle
from main import preprocessor
import os
import re
import math
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (generate_binary_structure, iterate_structure, binary_erosion)

#----- GLOBALS ----------

POPULATION = 100
DEFAULT_PERIOD_MS = 4000
EVALUATIONS = 0
BEST_DISTANCE_SO_FAR = sys.maxint
MAX_EVALUTATIONS = 10000
SELECTION_METHOD = 'truncation'
NUMBER_OF_HALFBEATS_PER_PERIOD = 8
LOGGER = Logger('log.txt', True)
SAVE_DIR_FOR_SOUNDS = 'data'
SONG_AUDIOBITE = None # Song AudioBite
NOTE_AUDIOBITES = None # dict (note -> AudioBite)


RESET_NOTES = False
OVERWRITE_SONG = False
DATA_DIR = 'data'
PROCESSED_DIR = 'processed'
NOTESET_DIR = DATA_DIR + '/noteset/'
# INPUT_SONG = DATA_DIR + '/songs/full_scale.wav'
SONG_NAME = 'full_scale_spread'
INPUT_SONG = DATA_DIR + '/songs/{0}.wav'.format(SONG_NAME)
PROCESSED_NOTESETS = PROCESSED_DIR + '/noteset.pik'
PROCESSED_SONG = '{0}.pik'.format(os.sep.join([PROCESSED_DIR] + INPUT_SONG.split(os.sep)[1:]))

# notes
NOTES = ['C5','Db5','D5','Eb5','E5','F5','Gb5','G5','Ab5','A5','Bb5','B5']
NOTE_INDEX_DICT = {NOTES[i]: i for i in xrange(len(NOTES))}

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


DEFAULT_AMP_MIN = 20
PEAK_NEIGHBORHOOD_SIZE = 20

def get_2D_peaks(arr2D, plot=False, amp_min=DEFAULT_AMP_MIN):
    # http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.morphology.iterate_structure.html#scipy.ndimage.morphology.iterate_structure
    struct = generate_binary_structure(2, 1)
    neighborhood = iterate_structure(struct, PEAK_NEIGHBORHOOD_SIZE)

    # find local maxima using our fliter shape
    local_max = maximum_filter(arr2D, footprint=neighborhood) == arr2D
    background = (arr2D == 0)
    eroded_background = binary_erosion(background, structure=neighborhood,
                                       border_value=1)

    # Boolean mask of arr2D with True at peaks
    detected_peaks = local_max - eroded_background

    # extract peaks
    amps = arr2D[detected_peaks]
    j, i = np.where(detected_peaks)

    amps = amps.flatten()
    peaks = zip(i, j, amps)
    peaks_filtered = [x for x in peaks if x[2] > amp_min]  # freq, time, amp

    # get indices for frequency and time
    frequency_idx = [x[1] for x in peaks_filtered]
    time_idx = [x[0] for x in peaks_filtered]
        # scatter of the peaks
    if plot:
        fig, ax = plt.subplots()
        ax.scatter(time_idx, frequency_idx, color ='black')

        ax.imshow(arr2D, aspect='auto')
        ax.set_xlabel('Time')
        ax.set_ylabel('Frequency')
        ax.set_title("Spectrogram")
        plt.gca().invert_yaxis()
        plt.show()
    return peaks_filtered



def main():
  global BEST_DISTANCE_SO_FAR
  global SONG_AUDIOBITE
  global NOTE_AUDIOBITES
  generations = 0
  records = []

  SONG_AUDIOBITE, NOTE_AUDIOBITES = setup()
  #numsamples ~= 256 * windows
  # numsamples /44100. = time in seconds

  #GENERATING RANDOM SONGS
  music_samples = []
  dists = []
  for n in range(POPULATION*2):
    sound = random_sound_factory()
    print sound.dist
    dists.append(sound.dist)
    music_samples.append(sound) # Append random music representation
  music_samples.sort(key=lambda e: e.dist) # Sort based on distance / fitness (whatever we're naming it)
  music_samples = music_samples[:POPULATION]

  print music_samples[0]
  best_dist = music_samples[0].dist
  perfect = EvolvedSound([['C5'],[],['D5'],[],['E5'],[],['F5'],[]])

  print 'Starting evolution...'

  while EVALUATIONS < MAX_EVALUTATIONS:
    # ensure no halfbeats
    for sample in music_samples:
      sample.note_list = [sample.note_list[i] if i % 2 == 0 else [] for i in xrange(len(sample.note_list)) ]


    generations += 1
    random.shuffle(music_samples)
    new_music_samples = []
    for i in xrange(0, int(len(music_samples)*0.8), 2): # P_CROSSOVER
      son, daughter = crossover(music_samples[i], music_samples[i+1])
      new_music_samples.append(son)
      new_music_samples.append(daughter)
    for sample in music_samples:
      if random.random() < 0.4: # P_MUTATION
        child = mutation(sample)
        new_music_samples.append(child)
    for new_sample in new_music_samples:
      new_sample.dist = new_sample.calculate_distance()
    music_samples += new_music_samples
    #Selection step
    music_samples.sort(key=lambda e: e.dist)
    music_samples = truncation(music_samples)


    record = [generations, EVALUATIONS, music_samples[0].dist, np.mean([i.dist for i in music_samples]), music_samples[0].note_list]
    records.append(record)

    print `EVALUATIONS` + " " + `music_samples[0].dist`
    BEST_DISTANCE_SO_FAR = music_samples[0].dist

  #Saving equations and figures
  # TODO Some sort of saving of the log
  new_file = open('music_logs/{0}--{1}--{1}.csv'.format(SONG_NAME, music_samples[0].dist, time.strftime("%Y.%m.%d-%H.%M.%S")),'w')
  new_file.write('\n'.join([','.join([str(ele) for ele in rec]) for rec in records]))
  new_file.close()
  read_music.save_representation_as_song(music_samples[0], '.', '{0}--{1}--{2}.wav'.format(SONG_NAME, music_samples[0].dist, time.strftime("%Y.%m.%d-%H.%M.%S")),DEFAULT_PERIOD_MS/8)

# ----- VARIATION METHODS ----------------

# Hill climber
def mutation(inisound):
  ''' Takes a random note and changes it. Doesn't hurt (mutate) the parent. '''
  sound = copy.deepcopy(inisound)

  # TODO change this later... assumes that

  # take a random note and change it
  random_i = random.randint(0,len(sound.note_list)-1)
  # Assume only one on no notes plays at a halfbeat
  if len(sound.note_list[random_i]) == 0:
    sound.note_list[random_i].append(random.choice(NOTES))
  else: # len == 1
    if random.random() < 0.25:
      sound.note_list[random_i].pop()
    else:
      note_index = NOTE_INDEX_DICT[sound.note_list[random_i][0]]
      change = random.choice([-1, 1])
      sound.note_list[random_i] = [NOTES[(note_index + change) % len(NOTES)]]
  # random_note = random.choice(notes_to_pick_from)
  # random.shuffle(sound.note_list[random_i])

  # if len(sound.note_list[i]) > 0 and random.randint(0,1): # either delete or not.
  #   sound.note_list[i].pop
  # elif random.randint(0,1): # either add a note or not
  #   sound.note_list[i].append(random_note)
  return sound

def crossover(dad,mom):
  '''
  Takes two songs and performs a 2 slice crossover to return two songs.
  Does not harm mom or dad. :)
  '''
  # Take two random slices and then swap
  son      = copy.deepcopy(dad)
  daughter = copy.deepcopy(mom)
  assert len(son.note_list) == len(daughter.note_list)
  rand_i = random.randint(0,len(son.note_list))
  rand_j = random.randint(0,len(son.note_list))
  random_i = min(rand_i,rand_j)
  random_j = max(rand_i,rand_j)
  son_middle = son.note_list[random_i:random_j]
  daughter_middle = daughter.note_list[random_i:random_j]
  son.note_list = son.note_list[0:random_i] + daughter_middle + son.note_list[random_j:]
  daughter.note_list = daughter.note_list[0:random_i] + son_middle + daughter.note_list[random_j:]
  return (son,daughter)

# ----- SELECTION METHODS ----------------

def truncation(songs):
  '''
  Selects the top portion of the population to reproduce
  Precondition: songs is sorted based on song distance
  '''
  return songs[:POPULATION]


# ----- REPRESENTATION ----------------


class EvolvedSound(object):
  clean_notes = {}
  sample_buckets = {}
  '''
  A representation of the sound object we are creating.
  The representation is a tuple: (period (milliseconds) * note list list)
  The note list list contains the notes in one "halfbeat".
  The "halfbeat" is defined as the period/NUMBER_OF_HALFBEATS_PER_PERIOD.
  '''
  def __init__(self, note_list, period=DEFAULT_PERIOD_MS):
    self.period = DEFAULT_PERIOD_MS
    # Strange additional of factor of 2 to account for two tracks
    song_len_ms = 1000*(SONG_AUDIOBITE.num_samples / 44100.) / 2.0
    self.halfbeats = int(math.floor(NUMBER_OF_HALFBEATS_PER_PERIOD * (song_len_ms / self.period)))
    self.windows = SONG_AUDIOBITE.mfcc_cep.shape[1]
    self.windows_per_halfbeat = self.windows/self.halfbeats

    note_list = []
    for i in xrange(self.halfbeats):
      if random.random() < 0.5:
        note_list.append([])
      else:
        note_list.append([random.choice(NOTE_AUDIOBITES.keys())])
      # li = []
      # for i in xrange(random.randint(0,5)):
      #   li.append(random.choice(NOTE_AUDIOBITES.keys()))
      # note_list.append(li)
      # note_list.append([])
      # note_list.append([])
      # note_list.append([])
    self.note_list = note_list

    if len(EvolvedSound.clean_notes) == 0:
      notes = {note: get_2D_peaks(NOTE_AUDIOBITES[note].mel_specgram, amp_min=20) for note in NOTE_AUDIOBITES.keys()}
      # Set cleaned note peaks
      EvolvedSound.clean_notes = {}
      for note in notes:
        cleaned_note = [item for item in notes[note] if item[1] > 25 and item[1] < 50 and item[2] > 20 and item[0] < self.windows_per_halfbeat*2.0]
        EvolvedSound.clean_notes[note] = cleaned_note[0]

    if len(EvolvedSound.sample_buckets) == 0:
      # Set cleaned sample note peaks
      sample = get_2D_peaks(SONG_AUDIOBITE.mel_specgram, amp_min=20)
      clean_sample = [item for item in sample if item[1] > 25 and item[1] < 50 and item[2] > 20]
      EvolvedSound.sample_buckets = {}
      for item in clean_sample:
        index = item[0]/ (self.windows_per_halfbeat*2)
        if not index in self.sample_buckets:
          EvolvedSound.sample_buckets[index] = []
        EvolvedSound.sample_buckets[index].append(item)
    self.dist = self.calculate_distance()

  def __str__(self):
    semicolon_delimited_lst_str = '[[' + ';'.join(map(str,self.note_list[0])) + ']'
    for n in self.note_list[1:]:
      semicolon_delimited_lst_str += ';[' + ';'.join(map(str,n)) + ']'
    semicolon_delimited_lst_str += ']'
    return '"%d;%s"' % (self.period,semicolon_delimited_lst_str)

  def __repr__(self):
    return self.__str__()

  def calculate_distance(self):
    def distance_peak2(p1, p2):
      return math.sqrt(sum([ (p1[1] - p2[1])**2]))
    error = 0
    for bucket in EvolvedSound.sample_buckets:
      note = self.note_list[2*bucket]
      if len(note) == 0:
        error += 300.0
        continue
      note_peak = EvolvedSound.clean_notes[note[0]]
      error += distance_peak2(note_peak, EvolvedSound.sample_buckets[bucket][0])
    global EVALUATIONS
    EVALUATIONS += 1
    return error
    # Tracer()()
    # # concatenate notes to (12,windows per halfbeat)

    # song_data = np.concatenate((SONG_AUDIOBITE.mfcc_cep,SONG_AUDIOBITE.mfcc_delta,SONG_AUDIOBITE.mfcc_delta_deltas),axis=0)
    # # Trim song_data down to fit dimensions of sound_data
    # song_data = song_data[0:,0:windows_per_halfbeat*len(self.note_list)]
    # sound_data = None
    # first = True
    # for notes in self.note_list:
    #   if len(notes) == 0:
    #     if sound_data is None:
    #       sound_data = np.zeros(shape=(36,windows_per_halfbeat))
    #     else:
    #       sound_data = np.concatenate((sound_data,np.zeros(shape=(36,windows_per_halfbeat))),axis=1)
    #     continue
    #   note = notes[0] # TODO Handle more than one note
    #   note_audio = NOTE_AUDIOBITES[note]
    #   cep = note_audio.mfcc_cep[0:,0:windows_per_halfbeat]
    #   delta = note_audio.mfcc_delta[0:,0:windows_per_halfbeat]
    #   ddelta = note_audio.mfcc_delta_deltas[0:,0:windows_per_halfbeat]
    #   note_data = np.concatenate((cep,delta,ddelta),axis=0)
    #   if first:
    #     first = False
    #     sound_data = note_data
    #   else:
    #     sound_data = np.concatenate((sound_data,note_data),axis=1)
    # mat = song_data - sound_data
    # # Tracer()()
    # mean_of_rows = mat.mean(axis=1)
    # stdd_of_rows = mat.std(axis=1)
    # for r in range(12):
    #   mat[r] = ((mat[r]-mean_of_rows[r])/stdd_of_rows[r])**2
    # #TODO: Not sure if there is a better/faster way of computing this ^^^
    # total_error = mat.sum()
    # return total_error


  def save_sound(self,filename):
    halfbeat = float(self.period)/NUMBER_OF_HALFBEATS_PER_PERIOD
    read_music.save_representation_as_song(self,SAVE_DIR_FOR_SOUNDS,filename,halfbeat)

def random_sound_factory():
  '''
  Returns an EvolvedSound object that is completely random.
  '''
  period = DEFAULT_PERIOD_MS
  song_len_ms = 1000*(SONG_AUDIOBITE.num_samples / 44100.)
  halfbeats = int(math.floor(NUMBER_OF_HALFBEATS_PER_PERIOD * (song_len_ms / period)))
  note_list = []
  for i in xrange(halfbeats):
    li = []
    for i in [0] if i % 2 == 0 else []:
      li.append(random.choice(NOTE_AUDIOBITES.keys()))
    note_list.append(li)
  return EvolvedSound(note_list,period)



# ------ NOTE METHODS ------------

def moveNote(note_str,n):
  ''' Moves note n halfsteps up or down from current spot note_str'''
  scale = ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']
  octave = int(note_str[-1])
  note = note_str[:2] if len(note_str) == 3 else note_str[:1]
  i = scale.index(note)
  new_note = scale[(i + n) % len(scale)]
  new_octave = octave + (i + n) / len(scale)
  return str(new_note) + str(new_octave)

if __name__ == '__main__':
  main()







