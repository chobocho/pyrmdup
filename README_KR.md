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

def main():
    print "Hello!"

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
        main()
```

### 2.3 실행 시간을 확인하기 위한 코드를 추가 

```
#-*- coding: utf-8 -*-
import sys
import timeit

myVersion = '-V0.627_170423c- Time:'

def main():
    print "Hello!"

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
