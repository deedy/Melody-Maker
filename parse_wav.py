from pydub import AudioSegment # Reading Audio data
import os
import numpy as np
import time
from IPython.core.debugger import Tracer


STANDARD_FREQUENCY = 44100

def parse_wav(path):
  print('-------------------------------------------')
  print('   BEGINNING TO PARSE {0}'.format(os.path.basename(path)))
  print('-------------------------------------------\n')

  print('Decoding audio... ')
  decode_start_time = time.time()
  audio = AudioSegment.from_file(path)
  print('Done decoding in {0} seconds to decode {1:.2f} seconds of audio.\n'.format(time.time() - decode_start_time, len(audio)/1000.0))

  # No need to crop audio because gtzan is guaranteed to be 30 seconds

  # np.int16 according to specification
  data = np.fromstring(audio._data, np.int16)

  # Pick 1st stereo stream
  # data = data[1::2]

  # No need to separate channels because it is Mono audio

  return path, data, STANDARD_FREQUENCY


