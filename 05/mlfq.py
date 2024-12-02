#! /usr/bin/env python

from __future__ import print_function
import sys
from optparse import OptionParser
import random

# 为了让Python2和Python3表现一致——真傻
def random_seed(seed):
    try:
        random.seed(seed, version=1)
    except:
        random.seed(seed)
    return

# 查找最高优先级的非空队列
# 如果队列都为空，返回-1
def FindQueue():
    q = hiQueue
    while q > 0:
        if len(queue[q]) > 0:
            return q
        q -= 1
    if len(queue[0]) > 0:
        return 0
    return -1

def Abort(str):
    sys.stderr.write(str + '\n')
    exit(1)


#
# 解析参数
#

parser = OptionParser()
parser.add_option('-s', '--seed', help='随机种子', 
                  default=0, action='store', type='int', dest='seed')
parser.add_option('-n', '--numQueues',
                  help='MLFQ中的队列数量（如果不使用-Q）', 
                  default=3, action='store', type='int', dest='numQueues')
parser.add_option('-q', '--quantum', help='时间片的长度（如果不使用-Q）',
                  default=10, action='store', type='int', dest='quantum')
parser.add_option('-a', '--allotment', help='配额长度（如果不使用-A）',
                  default=1, action='store', type='int', dest='allotment')
parser.add_option('-Q', '--quantumList',
                  help='每个队列级别的时间片长度，指定为x,y,z,...，其中x是最高优先级队列的时间片长度，y是下一个优先级，依此类推', 
                  default='', action='store', type='string', dest='quantumList')
parser.add_option('-A', '--allotmentList',
                  help='每个队列级别的时间配额，指定为x,y,z,...，其中x是最高优先级队列的时间配额，y是下一个优先级，依此类推', 
                  default='', action='store', type='string', dest='allotmentList')
parser.add_option('-j', '--numJobs', default=3, help='系统中的作业数量',
                  action='store', type='int', dest='numJobs')
parser.add_option('-m', '--maxlen', default=100, help='作业的最大运行时间（如果随机生成）', action='store', type='int',
                  dest='maxlen')
parser.add_option('-M', '--maxio', default=10,
                  help='作业的最大I/O频率（如果随机生成）',
                  action='store', type='int', dest='maxio')
parser.add_option('-B', '--boost', default=0,
                  help='多长时间将所有作业的优先级提升到高优先级', action='store', type='int', dest='boost')
parser.add_option('-i', '--iotime', default=5,
                  help='I/O操作的持续时间（固定常数）',
                  action='store', type='int', dest='ioTime')
parser.add_option('-S', '--stay', default=False,
                  help='当发出I/O请求时，是否重置并保持在同一优先级',
                  action='store_true', dest='stay')
parser.add_option('-I', '--iobump', default=False,
                  help='如果指定，完成I/O的作业将立即移到当前队列的前面',
                  action='store_true', dest='iobump')
parser.add_option('-l', '--jlist', default='',
                  help='以逗号分隔的作业列表，以x1,y1,z1:x2,y2,z2:...的形式，其中x是开始时间，y是运行时间，z是作业发出I/O请求的频率',
                  action='store', type='string', dest='jlist')
parser.add_option('-c', help='计算答案', action='store_true',
                  default=False, dest='solve')

(options, args) = parser.parse_args()

random.seed(options.seed)

# MLFQ: 队列数量
numQueues = options.numQueues

quantum = {}
if options.quantumList != '':
    # 解析队列数量及其时间片长度
    quantumLengths = options.quantumList.split(',')
    numQueues = len(quantumLengths)
    qc = numQueues - 1
    for i in range(numQueues):
        quantum[qc] = int(quantumLengths[i])
        qc -= 1
else:
    for i in range(numQueues):
        quantum[i] = int(options.quantum)

allotment = {}
if options.allotmentList != '':
    allotmentLengths = options.allotmentList.split(',')
    if numQueues != len(allotmentLengths):
        print('指定的配额数量必须与时间片数量匹配')
        exit(1)
    qc = numQueues - 1
    for i in range(numQueues):
        allotment[qc] = int(allotmentLengths[i])
        if qc != 0 and allotment[qc] <= 0:
            print('配额必须为正整数')
            exit(1)
        qc -= 1
else:
    for i in range(numQueues):
        allotment[i] = int(options.allotment)

hiQueue = numQueues - 1

# MLFQ: I/O 模型
# 每个I/O操作的时间：使用固定时间并不是很好，但...
ioTime = int(options.ioTime)

# 跟踪I/O和其他中断何时完成
ioDone = {}

# 存储所有作业信息
job = {}

# 初始化随机数生成器
random_seed(options.seed)

# jlist 'startTime,runTime,ioFreq:startTime,runTime,ioFreq:...'
jobCnt = 0
if options.jlist != '':
    allJobs = options.jlist.split(':')
    for j in allJobs:
        jobInfo = j.split(',')
        if len(jobInfo) != 3:
            print('作业字符串格式错误。应为 x1,y1,z1:x2,y2,z2:...')
            print('其中x是开始时间，y是运行时间，z是I/O频率。')
            exit(1)
        assert(len(jobInfo) == 3)
        startTime = int(jobInfo[0])
        runTime   = int(jobInfo[1])
        ioFreq    = int(jobInfo[2])
        job[jobCnt] = {'currPri':hiQueue, 'ticksLeft':quantum[hiQueue],
                       'allotLeft':allotment[hiQueue], 'startTime':startTime,
                       'runTime':runTime, 'timeLeft':runTime, 'ioFreq':ioFreq, 'doingIO':False,
                       'firstRun':-1}
        if startTime not in ioDone:
            ioDone[startTime] = []
        ioDone[startTime].append((jobCnt, '作业开始'))
        jobCnt += 1
else:
    # 随机生成作业
    for j in range(options.numJobs):
        startTime = 0
        runTime   = int(random.random() * (options.maxlen - 1) + 1)
        ioFreq    = int(random.random() * (options.maxio - 1) + 1)
        
        job[jobCnt] = {'currPri':hiQueue, 'ticksLeft':quantum[hiQueue],
                       'allotLeft':allotment[hiQueue], 'startTime':startTime,
                       'runTime':runTime, 'timeLeft':runTime, 'ioFreq':ioFreq, 'doingIO':False,
                       'firstRun':-1}
        if startTime not in ioDone:
            ioDone[startTime] = []
        ioDone[startTime].append((jobCnt, '作业开始'))
        jobCnt += 1


numJobs = len(job)

print('这是输入列表：')
print('选项 作业数',            numJobs)
print('选项 队列数',          numQueues)
for i in range(len(quantum)-1,-1,-1):
    print('选项 队列 %2d 的配额为 %3d' % (i, allotment[i]))
    print('选项 队列 %2d 的时间片长度为 %3d' % (i, quantum[i]))
print('选项 提升频率',           options.boost)
print('选项 I/O时间',          options.ioTime)
print('选项 I/O后保持优先级',     options.stay)
print('选项 I/O后提升优先级',          options.iobump)

print('\n')
print('对于每个作业，给出了三个关键特征：')
print('  startTime : 作业进入系统的时间')
print('  runTime   : 作业完成所需的总CPU时间')
print('  ioFreq    : 每过ioFreq时间单位，作业发出一个I/O请求')
print('              （I/O操作需要ioTime时间单位来完成）\n')

print('作业列表：')
for i in range(numJobs):
    print('  作业 %2d: startTime %3d - runTime %3d - ioFreq %3d' % (i, job[i]['startTime'], job[i]['runTime'], job[i]['ioFreq']))
print('')

if options.solve == False:
    print('计算给定工作负载的执行跟踪。')
    print('如果需要，还可以计算每个作业的响应时间和周转时间。')
    print('')
    print('使用 -c 标志在完成时获得准确的结果。\n')
    exit(0)
# 初始化 MLFQ 队列
queue = {}
for q in range(numQueues):
    queue[q] = []

# 时间是核心
currTime = 0

# 用这些来知道何时完成
totalJobs    = len(job)
finishedJobs = 0

print('\n执行跟踪：\n')

while finishedJobs < totalJobs:
    # 找到优先级最高的作业
    # 执行它直到满足以下条件之一：
    # (a) 作业用完了它的时间片
    # (b) 作业执行了一个I/O操作

    # 检查是否需要提升优先级
    if options.boost > 0 and currTime != 0:
        if currTime % options.boost == 0:
            print('[ 时间 %d ] 提升优先级 (每 %d 时间单位)' % (currTime, options.boost))
            # 从所有队列中移除作业（除了高优先级队列）并把它们放入高优先级队列
            for q in range(numQueues-1):
                for j in queue[q]:
                    if job[j]['doingIO'] == False:
                        queue[hiQueue].append(j)
                queue[q] = []

            # 将优先级改为高优先级
            # 重置所有作业剩余的时间片（仅对较低优先级的作业？）
            # 如果作业没有在执行I/O，就重新添加到最高优先级的队列中
            for j in range(numJobs):
                if job[j]['timeLeft'] > 0:
                    job[j]['currPri']   = hiQueue
                    job[j]['ticksLeft'] = quantum[hiQueue]
                    job[j]['allotLeft'] = allotment[hiQueue]
            # print('BOOST END: 队列情况:', queue)

    # 检查是否有I/O已完成
    if currTime in ioDone:
        for (j, type) in ioDone[currTime]:
            q = job[j]['currPri']
            job[j]['doingIO'] = False
            print('[ 时间 %d ] 作业 %d %s' % (currTime, j, type))
            if options.iobump == False or type == '作业开始':
                queue[q].append(j)
            else:
                queue[q].insert(0, j)

    # 现在找到优先级最高的作业
    currQueue = FindQueue()
    if currQueue == -1:
        print('[ 时间 %d ] 空闲' % (currTime))
        currTime += 1
        continue
            
    # 至少有一个可运行的作业，因此...
    currJob = queue[currQueue][0]
    if job[currJob]['currPri'] != currQueue:
        Abort('当前优先级[%d]与队列[%d]不匹配' % (job[currJob]['currPri'], currQueue))

    job[currJob]['timeLeft']  -= 1
    job[currJob]['ticksLeft'] -= 1

    if job[currJob]['firstRun'] == -1:
        job[currJob]['firstRun'] = currTime

    runTime   = job[currJob]['runTime']
    ioFreq    = job[currJob]['ioFreq']
    ticksLeft = job[currJob]['ticksLeft']
    allotLeft = job[currJob]['allotLeft']
    timeLeft  = job[currJob]['timeLeft']

    print('[ 时间 %d ] 执行 作业 %d 以 优先级 %d [ 时间片 %d 配额 %d 剩余时间 %d（共 %d） ]' % \
          (currTime, currJob, currQueue, ticksLeft, allotLeft, timeLeft, runTime))

    if timeLeft < 0:
        Abort('错误：剩余时间不能小于0')

    # 更新时间
    currTime += 1

    # 检查作业是否结束
    if timeLeft == 0:
        print('[ 时间 %d ] 作业 %d 完成' % (currTime, currJob))
        finishedJobs += 1
        job[currJob]['endTime'] = currTime
        done = queue[currQueue].pop(0)
        assert(done == currJob)
        continue

    # 检查是否需要执行I/O
    issuedIO = False
    if ioFreq > 0 and (((runTime - timeLeft) % ioFreq) == 0):
        # 需要执行I/O操作！
        print('[ 时间 %d ] 作业 %d 开始I/O操作' % (currTime, currJob))
        issuedIO = True
        desched = queue[currQueue].pop(0)
        assert(desched == currJob)
        job[currJob]['doingIO'] = True
        # 这会导致不好的规则 —— 执行I/O时重置该层级的时间
        if options.stay == True:
            job[currJob]['ticksLeft'] = quantum[currQueue]
            job[currJob]['allotLeft'] = allotment[currQueue]
        # 加入I/O队列：但是加入哪个队列呢？
        futureTime = currTime + ioTime
        if futureTime not in ioDone:
            ioDone[futureTime] = []
        print('I/O 完成')
        ioDone[futureTime].append((currJob, 'I/O 完成'))
        
    # 检查时间片是否结束（但记住，仍可能剩余配额）
    if ticksLeft == 0:
        if issuedIO == False:
            # 未执行I/O（因此从队列中移除）
            desched = queue[currQueue].pop(0)
        assert(desched == currJob)

        job[currJob]['allotLeft'] = job[currJob]['allotLeft'] - 1

        if job[currJob]['allotLeft'] == 0:
            # 作业在此层级完成，因此转移到下一个层级
            if currQueue > 0:
                # 在这种情况下，必须更改作业的优先级
                job[currJob]['currPri']   = currQueue - 1
                job[currJob]['ticksLeft'] = quantum[currQueue-1]
                job[currJob]['allotLeft'] = allotment[currQueue-1]
                if issuedIO == False:
                    queue[currQueue-1].append(currJob)
            else:
                job[currJob]['ticksLeft'] = quantum[currQueue]
                job[currJob]['allotLeft'] = allotment[currQueue]
                if issuedIO == False:
                    queue[currQueue].append(currJob)
        else:
            # 作业在此层级仍有时间，因此将其推到队列末尾
            job[currJob]['ticksLeft'] = quantum[currQueue]
            if issuedIO == False:
                queue[currQueue].append(currJob)


# 输出统计信息
print('')
print('最终统计信息：')
responseSum   = 0
turnaroundSum = 0
for i in range(numJobs):
    response   = job[i]['firstRun'] - job[i]['startTime']
    turnaround = job[i]['endTime'] - job[i]['startTime']
    print('  作业 %2d: startTime %3d - 响应时间 %3d - 周转时间 %3d' % (i, job[i]['startTime'], response, turnaround))
    responseSum   += response
    turnaroundSum += turnaround

print('\n  平均响应时间：%.2f - 平均周转时间：%.2f' % (float(responseSum)/numJobs, float(turnaroundSum)/numJobs))
print('\n')

