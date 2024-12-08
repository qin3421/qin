#! /usr/bin/env python

from __future__ import print_function
import sys
from optparse import OptionParser
import random
import math

# 使Python2和Python3的随机数行为一致
def random_seed(seed):
    try:
        random.seed(seed, version=1)
    except:
        random.seed(seed)
    return

# 转换大小单位
def convert(size):
    length = len(size)
    lastchar = size[length-1]
    if (lastchar == 'k') or (lastchar == 'K'):
        m = 1024
        nsize = int(size[0:length-1]) * m
    elif (lastchar == 'm') or (lastchar == 'M'):
        m = 1024*1024
        nsize = int(size[0:length-1]) * m
    elif (lastchar == 'g') or (lastchar == 'G'):
        m = 1024*1024*1024
        nsize = int(size[0:length-1]) * m
    else:
        nsize = int(size)
    return nsize

# 缓存命中与未命中的标识函数
def hfunc(index):
    if index == -1:
        return '未命中'
    else:
        return '命中'

# 被替换页面的标识函数
def vfunc(victim):
    if victim == -1:
        return '-'
    else:
        return str(victim)

# 主程序
parser = OptionParser()
parser.add_option('-a', '--addresses', default='-1',   help='要访问的一组以逗号分隔的页面；-1表示随机生成',          action='store', type='string', dest='addresses')
parser.add_option('-f', '--addressfile', default='',   help='包含大量地址的文件',                                      action='store', type='string', dest='addressfile')
parser.add_option('-n', '--numaddrs', default='10',    help='如果-a选项为-1，生成的地址数量',                          action='store', type='string', dest='numaddrs')
parser.add_option('-p', '--policy', default='FIFO',    help='页面替换策略：FIFO, LRU, OPT, UNOPT, RAND, CLOCK',        action='store', type='string', dest='policy')
parser.add_option('-b', '--clockbits', default=2,      help='用于CLOCK策略的时钟位数量',                              action='store', type='int', dest='clockbits')
parser.add_option('-C', '--cachesize', default='3',    help='页面缓存的大小（以页为单位）',                            action='store', type='string', dest='cachesize')
parser.add_option('-m', '--maxpage', default='10',     help='如果随机生成页面访问，这是最大页面编号',                  action='store', type='string', dest='maxpage')
parser.add_option('-s', '--seed', default='0',         help='随机数种子',                                            action='store', type='string', dest='seed')
parser.add_option('-N', '--notrace', default=False,    help='不输出详细跟踪信息',                                    action='store_true', dest='notrace')
parser.add_option('-c', '--compute', default=False,    help='为我计算答案',                                          action='store_true', dest='solve')

(options, args) = parser.parse_args()

print('参数 地址', options.addresses)
print('参数 地址文件', options.addressfile)
print('参数 地址数量', options.numaddrs)
print('参数 策略', options.policy)
print('参数 时钟位', options.clockbits)
print('参数 缓存大小', options.cachesize)
print('参数 最大页面', options.maxpage)
print('参数 随机种子', options.seed)
print('参数 不追踪', options.notrace)
print('')

addresses   = str(options.addresses)
addressFile = str(options.addressfile)
numaddrs    = int(options.numaddrs)
cachesize   = int(options.cachesize)
seed        = int(options.seed)
maxpage     = int(options.maxpage)
policy      = str(options.policy)
notrace     = options.notrace
clockbits   = int(options.clockbits)

random_seed(seed)

addrList = []
if addressFile != '':
    fd = open(addressFile)
    for line in fd:
        addrList.append(int(line))
    fd.close()
else:
    if addresses == '-1':
        # 需要生成地址
        for i in range(0,numaddrs):
            n = int(maxpage * random.random())
            addrList.append(n)
    else:
        addrList = addresses.split(',')

if options.solve == False:
    print('假设替换策略为 %s，缓存大小为 %d 页，' % (policy, cachesize))
    print('请判断以下每个页面引用是命中还是未命中。\n')

    for n in addrList:
        print('访问: %d  命中/未命中?  内存状态？' % int(n))
    print('')

else:
    if notrace == False:
        print('正在解决...\n')

    # 初始化内存结构
    count = 0  # 当前缓存中页面数量
    memory = []  # 用于存储缓存的页面
    hits = 0  # 命中计数
    miss = 0  # 未命中计数

    if policy == 'FIFO':
        leftStr = '先进页面'
        riteStr = '后进页面'
    elif policy == 'LRU':
        leftStr = '最近最少使用'
        riteStr = '最近最常使用'
    elif policy == 'MRU':
        leftStr = '最近最少使用'
        riteStr = '最近最常使用'
    elif policy in ['OPT', 'RAND', 'UNOPT', 'CLOCK']:
        leftStr = '左边'
        riteStr = '右边'
    else:
        print('策略 %s 尚未实现' % policy)
        exit(1)

    # 跟踪CLOCK策略的引用位
    ref = {}

    cdebug = False  # 调试标志

    # 生成地址
    addrIndex = 0
    for nStr in addrList:
        # 首先查找
        n = int(nStr)
        try:
            idx = memory.index(n)  # 查找页面是否在缓存中
            hits += 1  # 命中计数加1
            if policy in ['LRU', 'MRU']:
                # 更新最近使用页面的位置
                memory.remove(n)
                memory.append(n)  # 将其移到最近最常使用的一侧
        except:
            idx = -1  # 页面不在缓存中
            miss += 1  # 未命中计数加1

        victim = -1  # 被替换的页面，默认值为-1表示没有页面被替换
        if idx == -1:  # 如果未命中
            if count == cachesize:
                # 缓存已满，需要替换页面
                if policy in ['FIFO', 'LRU']:
                    victim = memory.pop(0)  # 删除最早进入的页面
                elif policy == 'MRU':
                    victim = memory.pop(count-1)  # 删除最近最常使用的页面
                elif policy == 'RAND':
                    victim = memory.pop(int(random.random() * count))  # 随机替换页面
                elif policy == 'CLOCK':
                    if cdebug:
                        print('访问页面:', n)
                        print('内存状态:', memory)
                        print('引用位 (前):', ref)

                    victim = -1
                    while victim == -1:
                        page = memory[int(random.random() * count)]
                        if cdebug:
                            print('  扫描页面:', page, ref[page])
                        if ref[page] >= 1:
                            ref[page] -= 1
                        else:
                            # 找到要替换的页面
                            victim = page
                            memory.remove(page)
                            break

                    # 删除被替换页面的引用位
                    del ref[victim]
                    if cdebug:
                        print('被替换页面:', page)
                        print('内存长度:', len(memory))
                        print('内存状态:', memory)
                        print('引用位 (后):', ref)

                elif policy == 'OPT':
                    # 选择最晚被引用的页面
                    maxReplace = -1
                    replaceIdx = -1
                    for pageIndex in range(count):
                        page = memory[pageIndex]
                        whenReferenced = len(addrList)
                        for futureIdx in range(addrIndex+1, len(addrList)):
                            futurePage = int(addrList[futureIdx])
                            if page == futurePage:
                                whenReferenced = futureIdx
                                break
                        if whenReferenced > maxReplace:
                            replaceIdx = pageIndex
                            maxReplace = whenReferenced
                    victim = memory.pop(replaceIdx)

                elif policy == 'UNOPT':
                    # 选择最近将要被使用的页面
                    minReplace = len(addrList) + 1
                    replaceIdx = -1
                    for pageIndex in range(count):
                        page = memory[pageIndex]
                        whenReferenced = len(addrList)
                        for futureIdx in range(addrIndex+1, len(addrList)):
                            futurePage = int(addrList[futureIdx])
                            if page == futurePage:
                                whenReferenced = futureIdx
                                break
                        if whenReferenced < minReplace:
                            replaceIdx = pageIndex
                            minReplace = whenReferenced
                    victim = memory.pop(replaceIdx)
            else:
                # 未命中但缓存未满
                count += 1

            # 将当前页面加入缓存
            memory.append(n)
            if cdebug:
                print('内存长度 (添加后):', len(memory))

        # 更新CLOCK策略的引用位
        if n not in ref:
            ref[n] = 1
        else:
            ref[n] += 1
            if ref[n] > clockbits:
                ref[n] = clockbits

        # 打印跟踪信息
        if notrace == False:
            print('访问: %d  %s %s -> %12s <- %s 替换: %s [命中:%d 未命中:%d]' % (
                n, hfunc(idx), leftStr, memory, riteStr, vfunc(victim), hits, miss))
        addrIndex += 1

    print('')
    print('最终统计 命中数:%d 未命中数:%d 命中率:%.2f%%' % (hits, miss, (100.0 * hits) / (hits + miss)))
    print('')
