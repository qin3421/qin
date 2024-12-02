from __future__ import print_function
import sys
from optparse import OptionParser
import random


def random_seed(seed):
    try:
        random.seed(seed, version=1)
    except:
        random.seed(seed)
    return

parser = OptionParser()
parser.add_option("-s", "--seed", default=0, help="随机种子", action="store", type="int", dest="seed")
parser.add_option("-j", "--jobs", default=3, help="系统中的作业数量", action="store", type="int", dest="jobs")
parser.add_option("-l", "--jlist", default="", help="提供一个逗号分隔的运行时间列表，而不是随机生成作业", action="store", type="string", dest="jlist")
parser.add_option("-m", "--maxlen", default=10, help="作业的最大长度", action="store", type="int", dest="maxlen")
parser.add_option("-p", "--policy", default="FIFO", help="使用的调度策略：SJF, FIFO, RR", action="store", type="string", dest="policy")
parser.add_option("-q", "--quantum", help="轮转调度（RR）策略下的时间片长度", default=1, action="store", type="int", dest="quantum")
parser.add_option("-c", help="计算答案", action="store_true", default=False, dest="solve")

(options, args) = parser.parse_args()

random_seed(options.seed)

print('参数策略', options.policy)
if options.jlist == '':
    print('参数作业', options.jobs)
    print('参数最大长度', options.maxlen)
    print('参数种子', options.seed)
else:
    print('参数作业列表', options.jlist)
print('')

print('这是作业列表，每个作业的运行时间：')

import operator

joblist = []
if options.jlist == '':
    for jobnum in range(0, options.jobs):
        runtime = int(options.maxlen * random.random()) + 1
        joblist.append([jobnum, runtime])
        print('  作业', jobnum, '( 长度 = ' + str(runtime) + ' )')
else:
    jobnum = 0
    for runtime in options.jlist.split(','):
        joblist.append([jobnum, float(runtime)])
        jobnum += 1
    for job in joblist:
        print('  作业', job[0], '( 长度 = ' + str(job[1]) + ' )')
print('\n')

if options.solve == True:
    print('** 解决方案 **\n')
    if options.policy == 'SJF':
        joblist = sorted(joblist, key=operator.itemgetter(1))
        options.policy = 'FIFO'
    
    if options.policy == 'FIFO':
        thetime = 0
        print('执行跟踪：')
        for job in joblist:
            print('  [ 时间 %3d ] 执行作业 %d 需要 %.2f 秒 ( 完成时间 %.2f )' % (thetime, job[0], job[1], thetime + job[1]))
            thetime += job[1]

        print('\n最终统计数据：')
        t     = 0.0
        count = 0
        turnaroundSum = 0.0
        waitSum       = 0.0
        responseSum   = 0.0
        for tmp in joblist:
            jobnum  = tmp[0]
            runtime = tmp[1]
            
            response   = t
            turnaround = t + runtime
            wait       = t
            print('  作业 %3d -- 响应时间: %3.2f  周转时间 %3.2f  等待时间 %3.2f' % (jobnum, response, turnaround, wait))
            responseSum   += response
            turnaroundSum += turnaround
            waitSum       += wait
            t += runtime
            count = count + 1
        print('\n  平均值 -- 响应时间: %3.2f  周转时间 %3.2f  等待时间 %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count))
                     
    if options.policy == 'RR':
        print('执行跟踪：')
        turnaround = {}
        response = {}
        lastran = {}
        wait = {}
        quantum  = float(options.quantum)
        jobcount = len(joblist)
        for i in range(0, jobcount):
            lastran[i] = 0.0
            wait[i] = 0.0
            turnaround[i] = 0.0
            response[i] = -1

        runlist = []
        for e in joblist:
            runlist.append(e)

        thetime  = 0.0
        while jobcount > 0:
            job = runlist.pop(0)
            jobnum  = job[0]
            runtime = float(job[1])
            if response[jobnum] == -1:
                response[jobnum] = thetime
            currwait = thetime - lastran[jobnum]
            wait[jobnum] += currwait
            if runtime > quantum:
                runtime -= quantum
                ranfor = quantum
                print('  [ 时间 %3d ] 执行作业 %3d 需要 %.2f 秒' % (thetime, jobnum, ranfor))
                runlist.append([jobnum, runtime])
            else:
                ranfor = runtime
                print('  [ 时间 %3d ] 执行作业 %3d 需要 %.2f 秒 ( 完成时间 %.2f )' % (thetime, jobnum, ranfor, thetime + ranfor))
                turnaround[jobnum] = thetime + ranfor
                jobcount -= 1
            thetime += ranfor
            lastran[jobnum] = thetime

        print('\n最终统计数据：')
        turnaroundSum = 0.0
        waitSum       = 0.0
        responseSum   = 0.0
        for i in range(0, len(joblist)):
            turnaroundSum += turnaround[i]
            responseSum += response[i]
            waitSum += wait[i]
            print('  作业 %3d -- 响应时间: %3.2f  周转时间 %3.2f  等待时间 %3.2f' % (i, response[i], turnaround[i], wait[i]))
        count = len(joblist)
        
        print('\n  平均值 -- 响应时间: %3.2f  周转时间 %3.2f  等待时间 %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count))

    if options.policy != 'FIFO' and options.policy != 'SJF' and options.policy != 'RR': 
        print('错误：策略', options.policy, '不可用。')
        sys.exit(0)
else:
    print('计算每个作业的周转时间、响应时间和等待时间。')
    print('完成后，请再次运行此程序，使用相同的参数，')
    print('但是加上 -c，这样程序就会为您提供答案。您可以使用')
    print('-s <某个数字> 或者您自己的作业列表（例如 -l 10,15,20）')
    print('来生成不同的题目。')
    print('')

