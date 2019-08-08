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


file = open(os.path.join(log_dir, 'result.txt'), 'w+')


for f in files: 
    df = pd.read_csv(f, names=['commit', 'delay', 'total'], header=None, delimiter=' ')
    df = df.iloc[10:]

    commit_mean = df['commit'].mean()
    commit_max = df['commit'].max()
    commit_std = df['commit'].std()


    delay_mean = df['delay'].mean()
    delay_max = df['delay'].max()
    delay_std = df['delay'].std()

    total_mean = df['total'].mean()
    total_max = df['total'].max()
    total_std = df['total'].std()



    print('\n\n%s' % f)
    print('      commmit   delay   total')
    print('mean  %0.2fms  %0.2fms  %0.2fms'% (commit_mean/1000, delay_mean/1000, total_mean/1000))
    print('max   %0.2fms  %0.2fms  %0.2fms'% (commit_max/1000, delay_max/1000, total_max/1000))
    print('std   %0.2f    %0.2f    %0.2f  '% (commit_std, delay_std, total_std))

    file.write('\n\n%s\n' % f)
    file.write('      commmit   delay   total\n')
    file.write('mean  %0.2fms  %0.2fms  %0.2fms\n'% (commit_mean/1000, delay_mean/1000, total_mean/1000))
    file.write('max   %0.2fms  %0.2fms  %0.2fms\n'% (commit_max/1000, delay_max/1000, total_max/1000))
    file.write('std   %0.2f    %0.2f    %0.2f  \n'% (commit_std, delay_std, total_std))

file.close()