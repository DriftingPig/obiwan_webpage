"""
for a given brick, prints whether each rs* obiwan job finished or not
"""
import qdo
import os
import numpy as np
from glob import glob
from collections import defaultdict


QDO_RESULT= ['running', 'succeeded', 'failed']

def get_brickdir(outdir,obj,brick):
  return os.path.join(outdir,obj,brick[:3],brick)

def get_logdir(outdir,obj,brick,rowstart):
  return os.path.join( get_brickdir(outdir,obj,brick),
                       'rs%s' % rowstart)

def get_logfile(outdir,obj,brick,rowstart):
  return os.path.join( get_logdir(outdir,obj,brick,rowstart),
                       'log.%s' % brick)

def get_slurm_files(outdir):
  return glob( outdir + '/slurm-*.out')

def rs_from_logfile(log):
    logdir= os.path.dirname(log)
    return logdir[logdir.rfind('/rs')+3:]

def writelist(lis,fn):
  if os.path.exists(fn):
    os.remove(fn)
  with open(fn,'w') as foo:
    for li in lis:
      foo.write('%s\n' % li)
  print('Wrote %s' % fn)
  if len(lis) == 0:
    print('Warning: %s is empty list' % fn) 


class QdoList(object):
  def __init__(self,outdir,obj='elg',que_name='obiwan'):
    self.outdir= outdir
    self.obj= obj
    self.que_name= que_name
    print(self)

  def __str__(self):
    text= type(self).__name__ + ':' +'\n'
    for attr in ['outdir','obj','que_name']:
      text += '%s= %s\n' % (attr, getattr(self,attr) )
    return text

  def get_tasks_logs_slurms(self):
    """get tasks, logs, slurms for the three types of qdo status
    Running, Succeeded, Failed"""
    # Logs for all Failed tasks
    tasks={}
    ids={}
    logs= defaultdict(list)
    slurms= defaultdict(list)
    slurm_fns= get_slurm_files(self.outdir)
    assert(len(slurm_fns) > 0)
    print('slurm_fns=',slurm_fns)
    #err= defaultdict(lambda: [])
    print('qdo Que: %s' % self.que_name)
    q = qdo.connect(self.que_name)
    for res in QDO_RESULT:
      # List of "brick rs" for each QDO_RESULT  
      tasks[res] = [a.task 
                    for a in q.tasks(state= getattr(qdo.Task, res.upper()))]
      ids[res] = [a.id 
                    for a in q.tasks(state= getattr(qdo.Task, res.upper()))]
      # Corresponding log, slurm files  
      for task in tasks[res]:
        # Logs
        brick,rs= task.split(' ')
        logfn= get_logfile(self.outdir,self.obj,brick,rs)
        logs[res].append( logfn )
        # Slurms
        found= False
        for slurm_fn in slurm_fns:
          with open(slurm_fn,'r') as foo:
            text= foo.read()
          if logfn in text:
            found=True
            slurms[res].append( slurm_fn )
        if not found: 
            print('didnt find %s in slurms: ' % logfn,slurm_fn)
    return tasks,ids,logs,slurms

  def rerun_tasks(self,task_ids, debug=True):
    """set qdo tasks state to Pending for these task_ids
    
    Args:
      debug: False to actually reset the qdo tasks state AND to delete
      all output files for that task
    """
    q = qdo.connect(self.que_name)
    if not debug:
      print('resetting state for %d tasks' % len(task_ids))
    for task_id in task_ids:
      try:
        task_obj= q.tasks(id= task_id)
        brick,rs= task_obj.task.split(' ')
        logdir= get_logdir(self.outdir,self.obj,brick,rs)
        if debug:
          print('would remove dir %s' % logdir, 'for task obj',task_obj)
        else:
          task_obj.set_state(qdo.Task.PENDING)
          #os.removedirs(logdir)
      except ValueError:
        print('cant find task_id=%d' % task_id)

class RunStatus(object):
  """Tallys which QDO_RESULTS actually finished, what errors occured, etc.
  
  Args:
    tasks: dict, each key is list of qdo tasks
    logs: dict, each key is list of log files for each task
    err_list: text to search for in log file to classify as that type of err
  """
    
  def __init__(self,tasks,logs):
    self.tasks= tasks
    self.logs= logs
    self.err_list= ['Error A']

  def get_tally(self):
    tally= defaultdict(list)
    for res in ['succeeded','failed']:
      if res == 'succeeded':
        for log in self.logs[res]:
          with open(log,'r') as foo:
            text= foo.read()
          if "decals_sim:All done!" in text:
            tally[res].append( 1 )
          else:
            tally[res].append( 0 )
      elif res == 'failed':
        for log in self.logs[res]:
          with open(log,'r') as foo:
            text= foo.read()
          found_err= False
          for err in self.err_list:
            if err in text:
              tally[res].append(err)
              found_err=True
              break
          if not found_err:
            tally[res].append('Other')
    return tally

  def print_tally(self,tally):
    for res in self.tasks.keys():
      print('--- Tally %s ---' % res)
      if res == 'succeeded':
         print('done: %d/%d' % (np.sum(tally[res]), len(tally[res])))
      elif res == 'failed':
        for err in R.err_list + ['Other']:
          print('%s: %d/%d' % (err,
                   np.where(tally[res] == err)[0].size, len(tally[res])))
      elif res == 'running':
         print('assuming rerun: %d/%d' % (len(tally[res]),len(tally[res])))


if __name__ == '__main__':
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument('--outdir',default='/global/cscratch1/sd/kaylanb/obiwan_out/123/1238p245',help='',required=False)
  parser.add_argument('--obj',default='elg',help='',required=False)
  parser.add_argument('--brick',default='1238p245',help='',required=False)
  args = parser.parse_args()
  print(args)

  Q= QdoList(args.outdir,args.obj,que_name='obiwan_9deg')
  tasks,ids,logs,slurms= Q.get_tasks_logs_slurms()
  
  # Write log fns so can inspect
  for res in logs.keys():
    writelist(logs[res],"%s_logfns.txt" % res)
    writelist(slurms[res],"%s_slurmfns.txt" % res)

  R= RunStatus(tasks,logs)
  tally= R.get_tally()
  R.print_tally(tally)

  Q.rerun_tasks(ids['running'], debug=False)
  raise ValueError('done')

  cmd= os.path.join( get_brickdir(args.outdir,args.obj,args.brick) + '/*/' + 'log.*')
  logs= glob( cmd)
  assert(len(logs) > 0)

  status= defaultdict(dict)
  for log in logs:
    rs= rs_from_logfile(log)
    with open(log,'r') as foo:
      text= foo.read()
    if "INFO:decals_sim:All done!" in text:
      status[args.brick][rs]='done'
    else:
      status[args.brick][rs]='not'
  # Print results
  for brick in status.keys():
    for rs in status[brick].keys():
      print('%s %s: %s' % (brick,rs,status[brick][rs]))

  raise ValueError()



