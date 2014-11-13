class Logger(object):
  def __init__(self,path,enable):
    self.printer = open(path,'w')
    self.enabled = enable

  def log(self,gen_num,evaluation,best_dist,mean_dist,sound_str):
    if self.enabled:
      self.printer.write("%d,%d,%f,%f,%s" % (gen_num,evaluation,best_dist,mean_dist,sound_str))

