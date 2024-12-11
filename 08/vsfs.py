#! /usr/bin/env python

from __future__ import print_function
import random
from optparse import OptionParser

# 使得Python2和Python3的行为一致 -- 真是傻
def random_seed(seed):
    try:
        random.seed(seed, version=1)
    except:
        random.seed(seed)
    return

DEBUG = False

def dprint(str):
    if DEBUG:
        print(str)

printOps      = True
printState    = True
printFinal    = True

class bitmap:
    def __init__(self, size):
        self.size = size
        self.bmap = []
        for num in range(size):
            self.bmap.append(0)
        self.numAllocated = 0

    def alloc(self):
        for num in range(len(self.bmap)):
            if self.bmap[num] == 0:
                self.bmap[num] = 1
                self.numAllocated += 1
                return num
        return -1

    def free(self, num):
        assert(self.bmap[num] == 1)
        self.numAllocated -= 1
        self.bmap[num] = 0

    def markAllocated(self, num):
        assert(self.bmap[num] == 0)
        self.numAllocated += 1
        self.bmap[num] = 1

    def numFree(self):
        return self.size - self.numAllocated

    def dump(self):
        s = ''
        for i in range(len(self.bmap)):
            s += str(self.bmap[i])
        return s

class block:
    def __init__(self, ftype):
        assert(ftype == 'd' or ftype == 'f' or ftype == 'free')
        self.ftype = ftype
        # 仅适用于目录，应该是子类，但没关系
        self.dirUsed = 0
        self.maxUsed = 32
        self.dirList = []
        self.data    = ''

    def dump(self):
        if self.ftype == 'free':
            return '[]'
        elif self.ftype == 'd':
            rc = ''
            for d in self.dirList:
                # d的形式是 ('name', inum)
                short = '(%s,%s)' % (d[0], d[1])
                if rc == '':
                    rc = short
                else:
                    rc += ' ' + short
            return '['+rc+']'
            # return '%s' % self.dirList
        else:
            return '[%s]' % self.data

    def setType(self, ftype):
        assert(self.ftype == 'free')
        self.ftype = ftype

    def addData(self, data):
        assert(self.ftype == 'f')
        self.data = data

    def getNumEntries(self):
        assert(self.ftype == 'd')
        return self.dirUsed

    def getFreeEntries(self):
        assert(self.ftype == 'd')
        return self.maxUsed - self.dirUsed

    def getEntry(self, num):
        assert(self.ftype == 'd')
        assert(num < self.dirUsed)
        return self.dirList[num]

    def addDirEntry(self, name, inum):
        assert(self.ftype == 'd')
        self.dirList.append((name, inum))
        self.dirUsed += 1
        assert(self.dirUsed <= self.maxUsed)

    def delDirEntry(self, name):
        assert(self.ftype == 'd')
        tname = name.split('/')
        dname = tname[len(tname) - 1]
        for i in range(len(self.dirList)):
            if self.dirList[i][0] == dname:
                self.dirList.pop(i)
                self.dirUsed -= 1
                return
        assert(1 == 0)

    def dirEntryExists(self, name):
        assert(self.ftype == 'd')
        for d in self.dirList:
            if name == d[0]:
                return True
        return False

    def free(self):
        assert(self.ftype != 'free')
        if self.ftype == 'd':
            # 检查是否只有dot和dotdot
            assert(self.dirUsed == 2)
            self.dirUsed = 0
        self.data  = ''
        self.ftype = 'free'

class inode:
    def __init__(self, ftype='free', addr=-1, refCnt=1):
        self.setAll(ftype, addr, refCnt)

    def setAll(self, ftype, addr, refCnt):
        assert(ftype == 'd' or ftype == 'f' or ftype == 'free')
        self.ftype  = ftype
        self.addr   = addr
        self.refCnt = refCnt

    def incRefCnt(self):
        self.refCnt += 1

    def decRefCnt(self):
        self.refCnt -= 1

    def getRefCnt(self):
        return self.refCnt

    def setType(self, ftype):
        assert(ftype == 'd' or ftype == 'f' or ftype == 'free')
        self.ftype = ftype

    def setAddr(self, block):
        self.addr = block

    def getSize(self):
        if self.addr == -1:
            return 0
        else:
            return 1

    def getAddr(self):
        return self.addr

    def getType(self):
        return self.ftype

    def free(self):
        self.ftype = 'free'
        self.addr  = -1
        

class fs:
    def __init__(self, numInodes, numData):
        self.numInodes = numInodes
        self.numData   = numData
        
        self.ibitmap = bitmap(self.numInodes)
        self.inodes  = []
        for i in range(self.numInodes):
            self.inodes.append(inode())

        self.dbitmap = bitmap(self.numData)
        self.data    = []
        for i in range(self.numData):
            self.data.append(block('free'))
    
        # 根inode
        self.ROOT = 0

        # 创建根目录
        self.ibitmap.markAllocated(self.ROOT)
        self.inodes[self.ROOT].setAll('d', 0, 2)
        self.dbitmap.markAllocated(self.ROOT)
        self.data[0].setType('d')
        self.data[0].addDirEntry('.',  self.ROOT)
        self.data[0].addDirEntry('..', self.ROOT)

        # 这些只是为了假工作负载生成器
        self.files      = []
        self.dirs       = ['/']
        self.nameToInum = {'/':self.ROOT}
    def dump(self):
        print('inode 位图 ', self.ibitmap.dump())
        print('inode 信息  ', end='')
        for i in range(0, self.numInodes):
            ftype = self.inodes[i].getType()
            if ftype == 'free':
                print('[]', end='')
            else:
                print('[%s a:%s r:%d]' % (ftype, self.inodes[i].getAddr(), self.inodes[i].getRefCnt()), end='')
        print('')
        print('数据块位图  ', self.dbitmap.dump())
        print('数据块     ', end='')
        for i in range(self.numData):
            print(self.data[i].dump(), end='')
        print('')

    def makeName(self):
        p = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'k', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        return p[int(random.random() * len(p))]
        p = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 's', 't', 'v', 'w', 'x', 'y', 'z']
        f = p[int(random.random() * len(p))]
        p = ['a', 'e', 'i', 'o', 'u']
        s = p[int(random.random() * len(p))]
        p = ['b', 'c', 'd', 'f', 'g', 'j', 'k', 'l', 'm', 'n', 'p', 's', 't', 'v', 'w', 'x', 'y', 'z']
        l = p[int(random.random() * len(p))]
        return '%c%c%c' % (f, s, l)

    def inodeAlloc(self):
        return self.ibitmap.alloc()

    def inodeFree(self, inum):
        self.ibitmap.free(inum)
        self.inodes[inum].free()

    def dataAlloc(self):
        return self.dbitmap.alloc()

    def dataFree(self, bnum):
        self.dbitmap.free(bnum)
        self.data[bnum].free()
        
    def getParent(self, name):
        tmp = name.split('/')
        if len(tmp) == 2:
            return '/'
        pname = ''
        for i in range(1, len(tmp)-1):
            pname = pname + '/' + tmp[i]
        return pname

    def deleteFile(self, tfile):
        if printOps:
            print('unlink("%s");' % tfile)

        inum = self.nameToInum[tfile]
        ftype = self.inodes[inum].getType()

        if self.inodes[inum].getRefCnt() == 1:
            # 先释放数据块
            dblock = self.inodes[inum].getAddr()
            if dblock != -1:
                self.dataFree(dblock)
            # 然后释放 inode
            self.inodeFree(inum)
        else:
            self.inodes[inum].decRefCnt()

        # 从父目录中移除
        parent = self.getParent(tfile)
        pinum = self.nameToInum[parent]
        pblock = self.inodes[pinum].getAddr()
        # 修复的 bug: 如果需要，减少父目录 inode 的引用计数 (感谢 Srinivasan Thirunarayanan)
        if ftype == 'd':
            self.inodes[pinum].decRefCnt()
        self.data[pblock].delDirEntry(tfile)

        # 最后从文件列表中移除
        self.files.remove(tfile)
        return 0

    def createLink(self, target, newfile, parent):
        # 查找父目录信息
        parentInum = self.nameToInum[parent]

        # 父目录中是否有空间?
        pblock = self.inodes[parentInum].getAddr()
        if self.data[pblock].getFreeEntries() <= 0:
            dprint('*** createLink 失败：父目录没有空间 ***')
            return -1

        if self.data[pblock].dirEntryExists(newfile):
            dprint('*** createLink 失败：名字不唯一 ***')
            return -1

        # 查找目标的 inode
        tinum = self.nameToInum[target]
        self.inodes[tinum].incRefCnt()

        # 不增加父目录的引用计数 - 仅限目录
        # self.inodes[parentInum].incRefCnt()

        # 现在添加到目录中
        tmp = newfile.split('/')
        ename = tmp[len(tmp)-1]
        self.data[pblock].addDirEntry(ename, tinum)
        return tinum

    def createFile(self, parent, newfile, ftype):
        # 查找父目录信息
        parentInum = self.nameToInum[parent]

        # 父目录中是否有空间?
        pblock = self.inodes[parentInum].getAddr()
        if self.data[pblock].getFreeEntries() <= 0:
            dprint('*** createFile 失败：父目录没有空间 ***')
            return -1

        # 确保文件名唯一
        block = self.inodes[parentInum].getAddr()
        if self.data[block].dirEntryExists(newfile):
            dprint('*** createFile 失败：名字不唯一 ***')
            return -1
        
        # 查找空闲 inode
        inum = self.inodeAlloc()
        if inum == -1:
            dprint('*** createFile 失败：没有空闲的 inode ***')
            return -1
        
        # 如果是目录，则需要分配目录块来存储基本信息（., ..）
        fblock = -1
        if ftype == 'd':
            refCnt = 2
            fblock = self.dataAlloc()
            if fblock == -1:
                dprint('*** createFile 失败：没有空闲的数据块 ***')
                self.inodeFree(inum)
                return -1
            else:
                self.data[fblock].setType('d')
                self.data[fblock].addDirEntry('.',  inum)
                self.data[fblock].addDirEntry('..', parentInum)
        else:
            refCnt = 1
            
        # 现在可以初始化 inode
        self.inodes[inum].setAll(ftype, fblock, refCnt)

        # 如果是目录，增加父目录的引用计数
        if ftype == 'd':
            self.inodes[parentInum].incRefCnt()

        # 将文件添加到父目录的目录中
        self.data[pblock].addDirEntry(newfile, inum)
        return inum

    def writeFile(self, tfile, data):
        inum = self.nameToInum[tfile]
        curSize = self.inodes[inum].getSize()
        dprint('writeFile: inum:%d cursize:%d refcnt:%d' % (inum, curSize, self.inodes[inum].getRefCnt()))
        if curSize == 1:
            dprint('*** writeFile 失败：文件已满 ***')
            return -1
        fblock = self.dataAlloc()
        if fblock == -1:
            dprint('*** writeFile 失败：没有空闲的数据块 ***')
            return -1
        else:
            self.data[fblock].setType('f')
            self.data[fblock].addData(data)
        self.inodes[inum].setAddr(fblock)
        if printOps:
            print('fd=open("%s", O_WRONLY|O_APPEND); write(fd, buf, BLOCKSIZE); close(fd);' % tfile)
        return 0
            
    def doDelete(self):
        dprint('doDelete')
        if len(self.files) == 0:
            return -1
        dfile = self.files[int(random.random() * len(self.files))]
        dprint('尝试删除(%s)' % dfile)
        return self.deleteFile(dfile)
    def doLink(self):
            dprint('执行链接')
            if len(self.files) == 0:
                return -1
            parent = self.dirs[int(random.random() * len(self.dirs))]
            nfile = self.makeName()

            # 随机选择目标文件
            target = self.files[int(random.random() * len(self.files))]
            # 必须是文件，而不是目录（在这里始终为真）

            # 获取新文件的完整路径
            if parent == '/':
                fullName = parent + nfile
            else:
                fullName = parent + '/' + nfile

            dprint('尝试创建链接(%s %s %s)' % (target, nfile, parent))
            inum = self.createLink(target, nfile, parent)
            if inum >= 0:
                self.files.append(fullName)
                self.nameToInum[fullName] = inum
                if printOps:
                    print('link("%s", "%s");' % (target, fullName))
                return 0
            return -1

    def doCreate(self, ftype):
            dprint('执行创建')
            parent = self.dirs[int(random.random() * len(self.dirs))]
            nfile = self.makeName()
            if ftype == 'd':
                tlist = self.dirs
            else:
                tlist = self.files

            if parent == '/':
                fullName = parent + nfile
            else:
                fullName = parent + '/' + nfile

            dprint('尝试创建文件(%s %s %s)' % (parent, nfile, ftype))
            inum = self.createFile(parent, nfile, ftype)
            if inum >= 0:
                tlist.append(fullName)
                self.nameToInum[fullName] = inum
                if parent == '/':
                    parent = ''
                if ftype == 'd':
                    if printOps:
                        print('mkdir("%s/%s");' % (parent, nfile))
                else:
                    if printOps:
                        print('creat("%s/%s");' % (parent, nfile))
                return 0
            return -1

    def doAppend(self):
            dprint('执行追加')
            if len(self.files) == 0:
                return -1
            afile = self.files[int(random.random() * len(self.files))]
            dprint('尝试写入文件(%s)' % afile)
            data = chr(ord('a') + int(random.random() * 26))
            rc = self.writeFile(afile, data)
            return rc

    def run(self, numRequests):
            self.percentMkdir  = 0.40
            self.percentWrite  = 0.40
            self.percentDelete = 0.20
            self.numRequests   = 20

            print('初始状态')
            print('')
            self.dump()
            print('')

            for i in range(numRequests):
                if printOps == False:
                    print('哪个操作发生了？')
                rc = -1
                while rc == -1:
                    r = random.random()
                    if r < 0.3:
                        rc = self.doAppend()
                        dprint('执行追加 rc:%d' % rc)
                    elif r < 0.5:
                        rc = self.doDelete()
                        dprint('执行删除 rc:%d' % rc)
                    elif r < 0.7:
                        rc = self.doLink()
                        dprint('执行链接 rc:%d' % rc)
                    else:
                        if random.random() < 0.75:
                            rc = self.doCreate('f')
                            dprint('执行创建(f) rc:%d' % rc)
                        else:
                            rc = self.doCreate('d')
                            dprint('执行创建(d) rc:%d' % rc)
                    if self.ibitmap.numFree() == 0:
                        print('文件系统没有空闲的 inode；是否通过命令行参数重新运行？')
                        exit(1)
                    if self.dbitmap.numFree() == 0:
                        print('文件系统没有空闲的数据块；是否通过命令行参数重新运行？')
                        exit(1)
                if printState == True:
                    print('')
                    self.dump()
                    print('')
                else:
                    print('')
                    print('  文件系统状态（inode 位图、inode、数据位图、数据）？')
                    print('')

            if printFinal:
                print('')
                print('文件和目录的总结::')
                print('')
                print('  文件:      ', self.files)
                print('  目录:      ', self.dirs)
                print('')

#
# 主程序
#
parser = OptionParser()

parser.add_option('-s', '--seed',        default=0,     help='随机种子',                      action='store', type='int', dest='seed')
parser.add_option('-i', '--numInodes',   default=8,     help='文件系统中的 inode 数量',      action='store', type='int', dest='numInodes') 
parser.add_option('-d', '--numData',     default=8,     help='文件系统中的数据块数量', action='store', type='int', dest='numData') 
parser.add_option('-n', '--numRequests', default=10,    help='模拟的请求次数',       action='store', type='int', dest='numRequests')
parser.add_option('-r', '--reverse',     default=False, help='打印操作而不是状态', action='store_true',        dest='reverse')
parser.add_option('-p', '--printFinal',  default=False, help='打印最终的文件/目录集',    action='store_true',        dest='printFinal')
parser.add_option('-c', '--compute',     default=False, help='计算答案',               action='store_true',        dest='solve')

(options, args) = parser.parse_args()

print('ARG seed',        options.seed)
print('ARG numInodes',   options.numInodes)
print('ARG numData',     options.numData)
print('ARG numRequests', options.numRequests)
print('ARG reverse',     options.reverse)
print('ARG printFinal',  options.printFinal)
print('')

random_seed(options.seed)

if options.reverse:
    printState = False
    printOps   = True
else:
    printState = True
    printOps   = False

if options.solve:
    printOps   = True
    printState = True

printFinal = options.printFinal

#
# 必须生成有效的文件系统随机请求！
#

f = fs(options.numInodes, options.numData)

#
# 操作：mkdir rmdir : create delete : append write
#

f.run(options.numRequests)

