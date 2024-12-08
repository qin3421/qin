#! /usr/bin/env python

from __future__ import print_function
import random
from optparse import OptionParser

# 为了使 Python2 和 Python3 的行为一致
def random_seed(seed):
    try:
        random.seed(seed, version=1)
    except:
        random.seed(seed)
    return

class malloc:
    def __init__(self, size, start, headerSize, policy, order, coalesce, align):
        # 空间大小
        self.size        = size
        
        # 关于假设头部信息
        self.headerSize  = headerSize

        # 初始化空闲列表
        self.freelist    = []
        self.freelist.append((start, size))

        # 记录指针到大小的映射关系
        self.sizemap     = {}

        # 分配策略
        self.policy       = policy
        assert(self.policy in ['FIRST', 'BEST', 'WORST'])

        # 列表排序方式
        self.returnPolicy = order
        assert(self.returnPolicy in ['ADDRSORT', 'SIZESORT+', 'SIZESORT-', 'INSERT-FRONT', 'INSERT-BACK'])

        # 全列表合并
        self.coalesce     = coalesce

        # 对齐设置（-1表示不对齐）
        self.align        = align
        assert(self.align == -1 or self.align > 0)

    def addToMap(self, addr, size):
        assert(addr not in self.sizemap)
        self.sizemap[addr] = size
        # print('添加', addr, '到映射中，大小为', size)
        
    def malloc(self, size):
        if self.align != -1:
            left = size % self.align
            if left != 0:
                diff = self.align - left
            else:
                diff = 0
            # print('对齐: 为 %d 增加 %d' % (size, diff))
            size += diff

        size += self.headerSize

        bestIdx  = -1
        if self.policy == 'BEST':
            bestSize = self.size + 1
        elif self.policy == 'WORST' or self.policy == 'FIRST':
            bestSize = -1

        count = 0
            
        for i in range(len(self.freelist)):
            eaddr, esize = self.freelist[i][0], self.freelist[i][1]
            count   += 1
            if esize >= size and ((self.policy == 'BEST'  and esize < bestSize) or
                                  (self.policy == 'WORST' and esize > bestSize) or
                                  (self.policy == 'FIRST')):
                bestAddr = eaddr
                bestSize = esize
                bestIdx  = i
                if self.policy == 'FIRST':
                    break

        if bestIdx != -1:
            if bestSize > size:
                # print('分裂', bestAddr, size)
                self.freelist[bestIdx] = (bestAddr + size, bestSize - size)
                self.addToMap(bestAddr, size)
            elif bestSize == size:
                # print('完美匹配 (无分裂)', bestAddr, size)
                self.freelist.pop(bestIdx)
                self.addToMap(bestAddr, size)
            else:
                abort('这里不应该出现')
            return (bestAddr, count)

        # print('*** 未找到合适位置', size)
        return (-1, count)

    def free(self, addr):
        # 简单地将释放的块放回列表末尾，不进行合并
        if addr not in self.sizemap:
            return -1
            
        size = self.sizemap[addr]
        if self.returnPolicy == 'INSERT-BACK':
            self.freelist.append((addr, size))
        elif self.returnPolicy == 'INSERT-FRONT':
            self.freelist.insert(0, (addr, size))
        elif self.returnPolicy == 'ADDRSORT':
            self.freelist.append((addr, size))
            self.freelist = sorted(self.freelist, key=lambda e: e[0])
        elif self.returnPolicy == 'SIZESORT+':
            self.freelist.append((addr, size))
            self.freelist = sorted(self.freelist, key=lambda e: e[1], reverse=False)
        elif self.returnPolicy == 'SIZESORT-':
            self.freelist.append((addr, size))
            self.freelist = sorted(self.freelist, key=lambda e: e[1], reverse=True)

        # 不高效但能合并的逻辑
        if self.coalesce == True:
            self.newlist = []
            self.curr    = self.freelist[0]
            for i in range(1, len(self.freelist)):
                eaddr, esize = self.freelist[i]
                if eaddr == (self.curr[0] + self.curr[1]):
                    self.curr = (self.curr[0], self.curr[1] + esize)
                else:
                    self.newlist.append(self.curr)
                    self.curr = eaddr, esize
            self.newlist.append(self.curr)
            self.freelist = self.newlist
            
        del self.sizemap[addr]
        return 0

    def dump(self):
        print('空闲列表 [大小 %d ]: ' % len(self.freelist), end='')
        for e in self.freelist:
            print('[ 地址:%d 大小:%d ]' % (e[0], e[1]), end='')
        print('')

# 主程序
#
# 参数解析器
parser = OptionParser()
parser.add_option('-s', '--seed',        default=0,          help='随机种子',                             action='store', type='int',    dest='seed')
parser.add_option('-S', '--size',        default=100,        help='堆的大小',                            action='store', type='int',    dest='heapSize') 
parser.add_option('-b', '--baseAddr',    default=1000,       help='堆的基址',                            action='store', type='int',    dest='baseAddr') 
parser.add_option('-H', '--headerSize',  default=0,          help='头部大小',                            action='store', type='int',    dest='headerSize')
parser.add_option('-a', '--alignment',   default=-1,         help='分配单元对齐大小；-1表示无对齐',      action='store', type='int',    dest='alignment')
parser.add_option('-p', '--policy',      default='BEST',     help='分配策略 (BEST, WORST, FIRST)',        action='store', type='string', dest='policy') 
parser.add_option('-l', '--listOrder',   default='ADDRSORT', help='空闲列表排序方式 (ADDRSORT, SIZESORT+, SIZESORT-, INSERT-FRONT, INSERT-BACK)', action='store', type='string', dest='order') 
parser.add_option('-C', '--coalesce',    default=False,      help='是否合并空闲列表？',                   action='store_true',           dest='coalesce')
parser.add_option('-n', '--numOps',      default=10,         help='随机操作的数量',                       action='store', type='int',    dest='opsNum')
parser.add_option('-r', '--range',       default=10,         help='最大分配大小',                         action='store', type='int',    dest='opsRange')
parser.add_option('-P', '--percentAlloc',default=50,         help='分配操作的百分比',                     action='store', type='int',    dest='opsPAlloc')
parser.add_option('-A', '--allocList',   default='',         help='操作列表（+10,-0等），替代随机生成',  action='store', type='string', dest='opsList')
parser.add_option('-c', '--compute',     default=False,      help='是否计算答案？',                        action='store_true',           dest='solve')

(options, args) = parser.parse_args()

m = malloc(int(options.heapSize), int(options.baseAddr), int(options.headerSize),
           options.policy, options.order, options.coalesce, options.alignment)

print('随机种子', options.seed)
print('堆大小', options.heapSize)
print('基址', options.baseAddr)
print('头部大小', options.headerSize)
print('对齐大小', options.alignment)
print('分配策略', options.policy)
print('列表排序方式', options.order)
print('是否合并空闲列表', options.coalesce)
print('操作数量', options.opsNum)
print('分配大小范围', options.opsRange)
print('分配操作百分比', options.opsPAlloc)
print('操作列表', options.opsList)
print('是否计算答案', options.solve)
print('')

percent = int(options.opsPAlloc) / 100.0

random_seed(int(options.seed))
p = {}
L = []
assert(percent > 0)

if options.opsList == '':
    c = 0
    j = 0
    while j < int(options.opsNum):
        pr = False
        if random.random() < percent:
            size     = int(random.random() * int(options.opsRange)) + 1
            ptr, cnt = m.malloc(size)
            if ptr != -1:
                p[c] = ptr
                L.append(c)
            print('指针[%d] = 分配(%d)' % (c, size), end='')
            if options.solve == True:
                print(' 返回 %d (搜索了 %d 个元素)' % (ptr + options.headerSize, cnt))
            else:
                print(' 返回 ?')
            c += 1
            j += 1
            pr = True
        else:
            if len(p) > 0:
                # 随机选择一个释放
                d = int(random.random() * len(L))
                rc = m.free(p[L[d]])
                print('释放(指针[%d])' % L[d], )
                if options.solve == True:
                    print('返回 %d' % rc)
                else:
                    print('返回 ?')
                del p[L[d]]
                del L[d]
                # print('DEBUG p', p)
                # print('DEBUG L', L)
                pr = True
                j += 1
        if pr:
            if options.solve == True:
                m.dump()
            else:
                print('列表状态? ')
            print('')
else:
    c = 0
    for op in options.opsList.split(','):
        if op[0] == '+':
            # 分配操作
            size     = int(op.split('+')[1])
            ptr, cnt = m.malloc(size)
            if ptr != -1:
                p[c] = ptr
            print('指针[%d] = 分配(%d)' % (c, size), end='')
            if options.solve == True:
                print(' 返回 %d (搜索了 %d 个元素)' % (ptr, cnt))
            else:
                print(' 返回 ?')
            c += 1
        elif op[0] == '-':
            # 释放操作
            index = int(op.split('-')[1])
            if index >= len(p):
                print('无效释放: 跳过')
                continue
            print('释放(指针[%d])' % index, )
            rc = m.free(p[index])
            if options.solve == True:
                print('返回 %d' % rc)
            else:
                print('返回 ?')
        else:
            abort('操作数格式错误：必须为 +Size 或 -Index')
        if options.solve == True:
            m.dump()
        else:
            print('列表状态?')
        print('')



