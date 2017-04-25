# pyrmdup
중복파일을 제거하는 파이썬 스크립트  

## 1. 기본 아이디어  
> 검색할 폴더안의 파일들을 크기순으로 정렬 하여, 같은 크기가 2개 이상인 파일들을 그룹으로 묶기  
> 같은 크기의 파일 그룹에 속한 파일들을 각각 1024바이트 씩 읽어서 같은 값인 파일들만 남기기  
> 같은 그룹에 속한 파일들을 1:1로 비교  


## 2. 구현  
### 2.1 pyrmdup.py 생성  
```
#-*- coding: utf-8 -*-

def main():
    print "Hello!"

if __name__ == '__main__':
   main()
```

### 2.2 옵션기능을 추가
>-m : 발견된 중복 파일을 dupfiles 폴더로 옮김  
>-d : 자세한 로그를 출력하기  
>-h : 도움말을 보여줌   

```
#-*- coding: utf-8 -*-
import sys

def main(folderlist):
    isMoveFile = False
    isDebugMode = False

    #Check option
    if '-m' in folderlist:
        isMoveFile = True
        folderlist.remove('-m')
        print "* Remove duplicated files"

    if '-d' in folderlist:
        isDebugMode = True
        folderlist.remove('-d')
        print "* Show file list"  

def printHelp():
    print "\n[Help]"
    print "Usage : pyrmdup [option] FolderName" 
    print "option:"
    print " -d : print log"
    print " -m : move all duplicated files to dupfiles folder"
    print " -h : show help message"

if __name__ == '__main__':
    if (len(sys.argv) < 2) or ('-h' in sys.argv[1:]):
        printHelp()
    else:
        main(sys.argv[1:])
```

### 2.3 실행 시간을 확인하기 위한 코드를 추가 

```
#-*- coding: utf-8 -*-
import sys
import timeit

myVersion = '-V0.627_170423c- Time:'

def main(folderlist):
    isMoveFile = False
    isDebugMode = False

    #Check option
    if '-m' in folderlist:
        isMoveFile = True
        folderlist.remove('-m')
        print "* Remove duplicated files"

    if '-d' in folderlist:
        isDebugMode = True
        folderlist.remove('-d')
        print "* Show file list" 

def printHelp():
    print "\n[Help]"
    print "Usage : pyrmdup [option] FolderName" 
    print "option:"
    print " -d : print log"
    print " -m : move all duplicated files to dupfiles folder"
    print " -h : show help message"

if __name__ == '__main__':
    start_time = timeit.default_timer()
 
    if (len(sys.argv) < 2) or ('-h' in sys.argv[1:]):
        printHelp()
    else:
        main(sys.argv[1:])

    print '\n', myVersion, timeit.default_timer()-start_time
```


### 2.4 입력된 폴더의 모든 파일을 출력

```
#-*- coding: utf-8 -*-
import sys
import timeit
import os

myVersion = '-V0.627_170423c- Time:'

def main(folderlist):
    isMoveFile = False
    isDebugMode = False

    #Check option
    if '-m' in folderlist:
        isMoveFile = True
        folderlist.remove('-m')
        print "* Remove duplicated files"

    if '-d' in folderlist:
        isDebugMode = True
        folderlist.remove('-d')
        print "* Show file list" 

    folders = folderlist

    print '* Folders :'
    for f in folders:
        print f

    print "* Start read files"
  
    for folder in folders:
        if os.path.exists(folder):
            for (path, dir, files) in os.walk(folder):
                for filename in files:
                    tf = os.path.join(path, filename)
                    print tf
        else:
            print "Error:",folder," is not exist"       

def printHelp():
    print "\n[Help]"
    print "Usage : pyrmdup [option] FolderName" 
    print "option:"
    print " -d : print log"
    print " -m : move all duplicated files to dupfiles folder"
    print " -h : show help message"

if __name__ == '__main__':
    start_time = timeit.default_timer()
 
    if (len(sys.argv) < 2) or ('-h' in sys.argv[1:]):
        printHelp()
    else:
        main(sys.argv[1:])

    print '\n', myVersion, timeit.default_timer()-start_time

```


### 2.5 입력된 폴더의 모든 파일을 읽어서 같은 크기 끼리 그룹으로 묶음

```
#-*- coding: utf-8 -*-
import sys
import timeit
import os

myVersion = '-V0.627_170423c- Time:'

def main(folderlist):
    isMoveFile = False
    isDebugMode = False

    #Check option
    if '-m' in folderlist:
        isMoveFile = True
        folderlist.remove('-m')
        print "* Remove duplicated files"

    if '-d' in folderlist:
        isDebugMode = True
        folderlist.remove('-d')
        print "* Show file list" 

    folders = folderlist

    print '* Folders :'
    for f in folders:
        print f

    print "* Start read files"
    dict = {}    #폴더안의 모든 파일을 읽어서, Kye=이름:value=크기 로 저장 
    result = {}  #중복 파일 리스트 개수를 저장하기 위한 변수
  
    for folder in folders:
        if os.path.exists(folder):
            for (path, dir, files) in os.walk(folder):
                for filename in files:
                    tf = os.path.join(path, filename)
                    if isDebugMode: print tf
                    dict[tf] = os.path.getsize(tf);
                    if isDebugMode: print ("%s : %d" % (tf, dict[tf]))

                    if result.get(dict[tf]) == None:
                        result[dict[tf]] = 1
                    else:
                        result[dict[tf]] += 1 
        else:
            print "Error:",folder," is not exist"                

def printHelp():
    print "\n[Help]"
    print "Usage : pyrmdup [option] FolderName" 
    print "option:"
    print " -d : print log"
    print " -m : move all duplicated files to dupfiles folder"
    print " -h : show help message"

if __name__ == '__main__':
    start_time = timeit.default_timer()
 
    if (len(sys.argv) < 2) or ('-h' in sys.argv[1:]):
        printHelp()
    else:
        main(sys.argv[1:])

    print '\n', myVersion, timeit.default_timer()-start_time

```


### 2.6 중복 파일 그룹을 65536보다 큰 파일 그룹과 작은 파일 그룹으로 나눔
```
    # dict : 중복파일 그룹
    # result : 중복 파일 리스트 개수를 저장하기 위한 변수

    print "\n* Start find same size files"   
    bigdupfile = {}
    smalldupfile = {}
          
    for key,value in dict.iteritems():  
        if result[value] != None and result[value] >= 2:
            #if isDebugMode: print key
            if value < LIMITED_SIZE:
                if smalldupfile.get(value) != None:
                    smalldupfile[value].append(key)
                else:
                    smalldupfile[value] = [key]
            else:
                if bigdupfile.get(value) != None:
                    bigdupfile[value].append(key)
                else:
                    bigdupfile[value] = [key]

```
[전체코드]


```
#-*- coding: utf-8 -*-
import sys
import timeit
import os

myVersion = '-V0.627_170424b- Time:'
LIMITED_SIZE = 65536

def main(folderlist):
    isMoveFile = False
    isDebugMode = False

    #Check option
    if '-m' in folderlist:
        isMoveFile = True
        folderlist.remove('-m')
        print "* Remove duplicated files"

    if '-d' in folderlist:
        isDebugMode = True
        folderlist.remove('-d')
        print "* Show file list" 

    folders = folderlist

    print '* Folders :'
    for f in folders:
        print f

    print "* Start read files"
    dict = {}    #폴더안의 모든 파일을 읽어서, Kye=이름:value=크기 로 저장 
    result = {}  #중복 파일 리스트를 저장하기 위한 변수
  
    for folder in folders:
        if os.path.exists(folder):
            for (path, dir, files) in os.walk(folder):
                for filename in files:
                    tf = os.path.join(path, filename)
                    if isDebugMode: print tf
                    dict[tf] = os.path.getsize(tf);
                    if isDebugMode: print ("%s : %d" % (tf, dict[tf]))

                    if result.get(dict[tf]) == None:
                        result[dict[tf]] = 1
                    else:
                        result[dict[tf]] += 1 
        else:
            print "Error:",folder," is not exist"                

    print "\n* Start find same size files"   
    bigdupfile = {}
    smalldupfile = {}
          
    for key,value in dict.iteritems():  
        if result[value] != None and result[value] >= 2:
            #if isDebugMode: print key
            if value < LIMITED_SIZE:
                if smalldupfile.get(value) != None:
                    smalldupfile[value].append(key)
                else:
                    smalldupfile[value] = [key]
            else:
                if bigdupfile.get(value) != None:
                    bigdupfile[value].append(key)
                else:
                    bigdupfile[value] = [key]

def printHelp():
    print "\n[Help]"
    print "Usage : pyrmdup [option] FolderName" 
    print "option:"
    print " -d : print log"
    print " -m : move all duplicated files to dupfiles folder"
    print " -h : show help message"

if __name__ == '__main__':
    start_time = timeit.default_timer()
 
    if (len(sys.argv) < 2) or ('-h' in sys.argv[1:]):
        printHelp()
    else:
        main(sys.argv[1:])

    print '\n', myVersion, timeit.default_timer()-start_time

```

### 2.7 파일 비교를 위한 함수를 추가
```
#파일에서 1024바이트를 읽어서 키값으로 쓴다.
def getMyHash(filepath):
    chunksize = 1024

    with open(filepath, 'rb') as afile:
        buf = afile.read(chunksize)

    buf = buf + '0.62700000000000000000000000000000000000000000000000000000000'
    return buf[0:1024]


#두 개의 파일에서 65536바이트를 읽어서 비교한다.  
def dofilecmp(f1, f2):
    bufsize = LIMITED_SIZE
    with open(f1, 'rb') as fp1, open(f2, 'rb') as fp2:
        b1 = fp1.read(bufsize)
        b2 = fp2.read(bufsize)
        if b1 != b2:
            return False
        
