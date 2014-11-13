import sys
from optparse import OptionParser
from pydub import AudioSegment
import pdb
import os
import glob

PARENT_OF_SAVE = 'data'
SAVE_DIR = 'songs'
READ_DIR = 'sheetmusic'
PRENOTE_NAME = 'data/noteset/Piano.ff.'
OFFSET_AT_END_OF_SONG = 250 #milliseconds

def main(path):
  '''
  It runs similiarly to main.py.
  If you pass in a file, it will write the file no matter what.
  If you pass in a dir,  it will write only the ones it's missing.
  '''
  for songfile in get_song_files(path):
    music_notes = read_song(songfile)
    song = create_song(music_notes)
    save_song(song,songfile)

def get_song_files(path):
  ''' Returns a list of song files that need to be created. '''
  to_process = []
  if os.path.isfile(path):
    unprocessed_files = [ path ]
  elif os.path.isdir(path):
    audio_files = [os.path.join(path, audio_file) for audio_file in os.listdir(path) if os.path.isfile(os.path.join(path, audio_file))]

    if len(audio_files) == 0:
      raise Exception('No files were found to read in.')
    to_process = audio_files

    unprocessed_files = []
    for audio_file in audio_files:
      filepath, ext  = os.path.splitext(audio_file)
      if filepath.split(os.sep)[-1] == '.DS_Store':
        continue
      savepath = os.sep.join([PARENT_OF_SAVE,SAVE_DIR] + filepath.split(os.sep)[2:]) # should be data/pianosongs/[userfile] like octave5/scale.txt

      processed_files = glob.glob(savepath+'*')
      if len(processed_files) == 0:
        unprocessed_files.append(audio_file)
    print('Beginning to construct {0} sheet music files in {1}'.format(len(to_process), path))
  else:
    raise Exception('{0} is not a valid directory or path'.format(path))
  return unprocessed_files

def read_song(path):
  with open(path) as f:
    period = int(f.readline().split()[1])
    time   = float(f.readline().split()[1])
    # TODO throw exceptions if format is off
    lst = []
    for line in f:
      if line.strip() == '':
        continue
      print line,
      pair = line.rstrip().split()
      #TODO fix
      measure_num = float(pair[1])-1
      beat_num = (float(pair[2])-1)/time
      position_in_song = period*(measure_num+beat_num)
      lst.append((pair[0],position_in_song))
      print (pair[0],position_in_song)
  lst.sort(key=lambda tup: tup[1])
  return lst

def create_song(notes):
  '''
  Takes in (note, pos (milliseconds))
  '''
  latest_note = notes[-1][1]
  song = AudioSegment.silent(duration=latest_note+OFFSET_AT_END_OF_SONG)
  print 'creating a song of %d seconds long' % ((latest_note+OFFSET_AT_END_OF_SONG)/1000)
  for n in notes:
    song = song.overlay(AudioSegment.from_wav(PRENOTE_NAME + n[0] + '.wav'),n[1])
  return song

def save_song(song,path):
  filepath, ext  = os.path.splitext(path)
  savepath = os.sep.join([PARENT_OF_SAVE,SAVE_DIR] + filepath.split(os.sep)[1:]) + '.wav'
  savedirs = os.sep.join([PARENT_OF_SAVE,SAVE_DIR] + filepath.split(os.sep)[1:-1])
  if not os.path.exists(savedirs):
    os.makedirs(savedirs)
  song.export(savepath, format='wav')

def save_representation_as_song(evolved_sound,save_path,filename,halfbeat_len):
  ''' Saves an evolved_sound at save_path/filename.wav with the halfbeat_len in milliseconds '''
  #create song from representation
  length_of_sound = len(evolved_sound.note_list)*halfbeat_len #in milliseconds
  song = AudioSegment.silent(duration=length_of_sound)
  for notes_index in range(len(evolved_sound.note_list)):
    notes = evolved_sound.note_list[notes_index]
    for note in notes:
      song = song.overlay(AudioSegment.from_wav(PRENOTE_NAME + note + '.wav'),notes_index*halfbeat_len)

  #save song to file
  save_song(song, os.sep.join([save_path,filename]))

if __name__ == '__main__':
  if len(sys.argv) < 2:
    raise Exception('No arguments supplied. Failing.')
  elif len(sys.argv) > 2:
    print('Only accepts one argument at this moment. Using first argument "{0}"'.format(sys.argv[1]))
  main(sys.argv[1])
