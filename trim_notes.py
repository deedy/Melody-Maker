from IPython.core.debugger import Tracer
import read_music
import sys
import os
import parse_wav
from pydub import AudioSegment
import numpy as np
import glob

FREQUENCY_TO_CAPTURE = 250

def main(filepath_aiff_dir,filepath_wave_save_dir):
  files = read_music.get_song_files(filepath_aiff_dir,'.',filepath_wave_save_dir,force_unprocessed=True)
  wav_files = []
  for f in files:
    save_path = os.path.join(filepath_wave_save_dir, os.path.split(os.path.splitext(f)[0])[1]) +'.wav'
    wav_files.append(save_path)
    if len(glob.glob(save_path+'*')) == 0:
      aiff = AudioSegment.from_file(f,'aiff')
      aiff.export(save_path, format='wav')
  for wf in wav_files:
    path, data, freq = parse_wav.parse_wav(wf)
    loud = np.where(np.abs(data) > FREQUENCY_TO_CAPTURE)
    start_ms = loud[0][0]*1000/parse_wav.STANDARD_FREQUENCY # millisec to start with
    end_ms   = loud[0][-1]*1000/parse_wav.STANDARD_FREQUENCY # millisec to end with
    wav = AudioSegment.from_wav(wf)
    wav = wav[start_ms:end_ms]
    wav.export(wf,format='wav')


if __name__ == '__main__':
  if len(sys.argv) < 3:
    raise Exception('Needs load_path_dir and save_path_dir.')
  elif len(sys.argv) > 3:
    print('Only accepts two arguments at this moment.')
  load = os.path.isdir(sys.argv[1])
  save = os.path.isdir(sys.argv[2])
  if load and save:
    main(sys.argv[1],sys.argv[2])
  elif not load:
    raise Exception(sys.argv[1] + ' is not a directory.')
  else:
    raise Exception(sys.argv[2] + ' is not a directory.')
    