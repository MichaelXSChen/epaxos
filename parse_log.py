import glob, os
import sys
import pandas as pd
import subprocess as sub

log_dir  = sys.argv[1]

log_dir = os.path.abspath(log_dir)

os.chdir(log_dir)

files = []
for f in glob.glob("*.log"):
    
    sub.call('cat %s | grep Commiting | cut -d \' \' -f 9,14,19 > %s' % (os.path.join(log_dir, f), os.path.join(log_dir, 'out%s.out'%f) ), shell = True)
    
    files.append( os.path.join(log_dir, 'out%s.out'%f) )



for f in files: 
    df = pd.read_csv(f, names=['commit', 'delay', 'total'], header=None, delimiter=' ')
    df = df.iloc[10:]

    commit_mean = df['commit'].mean()
    commit_max = df['commit'].max()


    delay_mean = df['delay'].mean()
    delay_max = df['delay'].max()

    total_mean = df['total'].mean()
    total_max = df['total'].max()

    print('\n\n%s' % f)
    print('      commmit   delay   total')
    print('mean  %0.2fms  %0.2fms  %0.2fms'% (commit_mean/1000, delay_mean/1000, total_mean/1000))
    print('max   %0.2fms  %0.2fms  %0.2fms'% (commit_max/1000, delay_max/1000, total_max/1000))
