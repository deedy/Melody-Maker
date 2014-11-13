from optparse import OptionParser
from parse_mp3 import parse_mp3
from parse_gtzan import parse_gtzan
from parse_wav import parse_wav
from AudioBite import AudioBite
import os
import glob
import cPickle as pickle


from IPython.core.debugger import Tracer

SAVE_DIR = 'processed'
PARSE_METHODS = {'.mp3': parse_mp3, '.au': parse_gtzan, '.wav':parse_wav}

if __name__ == '__main__':
  usage = "usage: %prog [options] arg"
  parser = OptionParser(usage)
  (options, args) = parser.parse_args()

  if len(args) == 0:
    raise Exception('No arguments supplied. Failing.')
    sys.exit
  if len(args) > 1:
    print('Only accepts one argument at this moment. Using first argument {0}'.format(args[0]))
  path = args[0]

  to_process = []
  if os.path.isfile(path):
    fp, ext = os.path.splitext(path)
    if not ext in PARSE_METHODS:
      raise Exception('Sorry, we currently only support the following types: {0}'.format('\n'.join(PARSE_METHODS.keys())))
    to_process = [ path ]
  elif os.path.isdir(path):
    audio_files = [os.path.join(path, audio_file) for audio_file in os.listdir(path) if os.path.isfile(os.path.join(path, audio_file)) and os.path.splitext(audio_file)[1] in PARSE_METHODS]

    if len(audio_files) == 0:
      raise Exception('Sorry, we currently only support the following file types: {0}, and none of those types were found in {1}'.format(' '.join(PARSE_METHODS.keys()), path))
    to_process = audio_files

    # Add option to reprocess all
    unprocessed_files = []
    for audio_file in audio_files:
      filepath, ext  = os.path.splitext(audio_file)
      savepath = os.sep.join([SAVE_DIR] + filepath.split(os.sep)[1:])
      processed_files = glob.glob(savepath+'*')
      if len(processed_files) == 0:
        unprocessed_files.append(audio_file)
    to_process = unprocessed_files
    print('Beginning to parse {0} mp3 files in {1}'.format(len(to_process), path))
  else:
    raise Exception('{0} is not a valid directory or path'.format(path))

  processed_audio = []
  for audio_file in to_process:
    _, ext  = os.path.splitext(audio_file)
    path, data, freq = PARSE_METHODS[ext](audio_file)
    processed_audio.append(AudioBite(path, data, freq))
    processed_audio[-1].save_spectrogram()
    processed_audio[-1].save_mel_spectrogram(plot_type = 'all')
    processed_audio[-1].save_mfcc()
    processed_audio[-1].save()
  # savepath = os.sep.join([SAVE_DIR,"alldata"])
  # pickle.dump(processed_audio, open('{0}.pik'.format(savepath), 'wb'))
  Tracer()()
  # Shows small difference for i = 2
  # sum(sum(np.square(processed_audio[1].mfcc_cep.T[:processed_audio[i].mfcc_cep.shape[1]] - processed_audio[i].mfcc_cep.T)))
  #[sum(sum(np.square(processed_audio[1].mfcc_cep.T[:processed_audio[i].mfcc_cep.shape[1]] - processed_audio[i].mfcc_cep.T))) for i in xrange(2,len(processed_audio))]

  # [sum(sum(np.square(processed_audio[1].mfcc_cep.T[i:i+processed_audio[j].mfcc_cep.shape[1]] - processed_audio[j].mfcc_cep.T))) for i in xrange(0,processed_audio[1].mfcc_cep.shape[1] - processed_audio[j].mfcc_cep.shape[1])]
  # # MFCCs, Deltas, Delta deltas summed together - Naive
  # alldata_ind = 0
  # [(np.argmin([sum(sum(np.square(processed_audio[alldata_ind].mfcc_cep.T[i:i+processed_audio[j].mfcc_cep.shape[1]] - processed_audio[j].mfcc_cep.T))) for i in xrange(0,processed_audio[alldata_ind].mfcc_cep.shape[1] - processed_audio[j].mfcc_cep.shape[1])]), np.argmin([sum(sum(np.square(processed_audio[alldata_ind].mfcc_delta.T[i:i+processed_audio[j].mfcc_delta.shape[1]] - processed_audio[j].mfcc_delta.T))) for i in xrange(0,processed_audio[alldata_ind].mfcc_delta.shape[1] - processed_audio[j].mfcc_delta.shape[1])]), np.argmin([sum(sum(np.square(processed_audio[alldata_ind].mfcc_delta_deltas.T[i:i+processed_audio[j].mfcc_delta_deltas.shape[1]] - processed_audio[j].mfcc_delta_deltas.T))) for i in xrange(0,processed_audio[alldata_ind].mfcc_delta_deltas.shape[1] - processed_audio[j].mfcc_delta_deltas.shape[1])])) for j in xrange(2, len(processed_audio))]
#[(0, 573, 573), (0, 513, 512), (233, 559, 559), (104, 1224, 1224), (512, 512, 512), (509, 1224, 1224), (512, 1227, 1227), (1222, 1222, 1054), (1222, 1222, 1222), (1643, 1227, 1227), (1787, 511, 554), (1224, 1224, 1224)]
# [(0, 0, 0), (262, 262, 262), (591, 591, 591), (877, 877, 877), (1141, 1141, 1141), (1938, 1938, 1938), (2359, 2359, 2359), (2906, 2906, 2906), (3502, 3502, 3502), (3961, 3961, 3960), (4419, 4419, 4419), (4712, 4712, 4712)]

# Each MFCC, Delta, Delta Delta summed individually,
# [np.argmin(x) for x in np.array([sum(np.square(processed_audio[alldata_ind].mfcc_cep.T[i:i+processed_audio[2].mfcc_cep.shape[1]] - processed_audio[2].mfcc_cep.T)) for i in xrange(0,processed_audio[alldata_ind].mfcc_cep.shape[1] - processed_audio[2].mfcc_cep.shape[1])]).T]
# [np.argmin(x) for x in np.array([sum(np.square(processed_audio[alldata_ind].mfcc_delta.T[i:i+processed_audio[2].mfcc_delta.shape[1]] - processed_audio[2].mfcc_delta.T)) for i in xrange(0,processed_audio[alldata_ind].mfcc_delta.shape[1] - processed_audio[2].mfcc_delta.shape[1])]).T]
# [np.argmin(x) for x in np.array([sum(np.square(processed_audio[alldata_ind].mfcc_delta_deltas.T[i:i+processed_audio[2].mfcc_delta_deltas.shape[1]] - processed_audio[2].mfcc_delta_deltas.T)) for i in xrange(0,processed_audio[alldata_ind].mfcc_delta_deltas.shape[1] - processed_audio[2].mfcc_delta_deltas.shape[1])]).T]

# # Outlier minimum support (arbitrary 100)
# from scipy.stats import mode
# [ mode([np.argmin(x) for x in np.array([sum(np.sort(np.square(processed_audio[alldata_ind].mfcc_cep.T[i:i+processed_audio[j].mfcc_cep.shape[1]] - processed_audio[j].mfcc_cep.T))[:100]) for i in xrange(0,processed_audio[alldata_ind].mfcc_cep.shape[1] - processed_audio[j].mfcc_cep.shape[1])]).T] + [np.argmin(x) for x in np.array([sum(np.sort(np.square(processed_audio[alldata_ind].mfcc_delta.T[i:i+processed_audio[j].mfcc_delta.shape[1]] - processed_audio[j].mfcc_delta.T))[:100]) for i in xrange(0,processed_audio[alldata_ind].mfcc_cep.shape[1] - processed_audio[j].mfcc_cep.shape[1])]).T] + [np.argmin(x) for x in np.array([sum(np.sort(np.square(processed_audio[alldata_ind].mfcc_delta_deltas.T[i:i+processed_audio[j].mfcc_delta_deltas.shape[1]] - processed_audio[j].mfcc_delta_deltas.T))[:100]) for i in xrange(0,processed_audio[alldata_ind].mfcc_cep.shape[1] - processed_audio[j].mfcc_cep.shape[1])]).T] )[0][0]   for j in xrange(2, len(processed_audio))]

# [0.0, 108.0, 233.0, 396.0, 512.0, 865.0, 1058.0, 1222.0, 1222.0, 1642.0, 1787.0, 1225.0]

  # This is where the fun stuff happens
  # processed_audio.save_spectrogram()
  # processed_audio.save_mel_spectrogram(plot_type = 'all')
  # processed_audio.save_mfcc()
  # processed_audio.save()






