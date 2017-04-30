#-*- coding: utf-8 -*-
import os
import sys
import timeit
import hashlib
import shutil
import random

myVersion = '-V0.627_170501a- Time:'
LIMITED_SIZE = 65536

def main(folderlist):
    isMoveFile = False
    isDebugMode = False
    error_msg = []

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
    dict = {}  
    aResult = {}  
  
    for folder in folders:
        if os.path.exists(folder):
            for (path, dir, files) in os.walk(folder):
                for filename in files:
                    tf = os.path.join(path, filename)
                    if isDebugMode: print tf
                    try:
                        dict[tf] = os.path.getsize(tf);
                        #if isDebugMode: print ("%s/%s " % (path, filename))
                        if isDebugMode: print ("%s : %d" % (tf, dict[tf]))
                        if aResult.get(dict[tf]) == None:
                            aResult[dict[tf]] = 1
                        else:
                            aResult[dict[tf]] += 1
                    except:
                        error_msg.append('Fail to get size of ' + tf)
                        print error_msg[-1]
 
        else:
            print "Error:",folder," is not exist"           

    print "\n* Start find same size files"   
    bigdupfile = {}
    smalldupfile = {}
          
    for key,value in dict.iteritems():  
        if aResult[value] != None and aResult[value] >= 2:
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

    result = {}
    print "\n* Start get same files < ",LIMITED_SIZE, len(smalldupfile)
    filecount = 1
    for key,aValue in smalldupfile.iteritems():
        print '.',len(aValue),
        myHash = {}
        for f in aValue:
            fileHash = getMyHash(f)
            if myHash.get(fileHash) != None:
               myHash[fileHash].append(f)
            else:
               myHash[fileHash] = [f]  
        
        tmpResult = list(filter(lambda x: len(x) >= 2, myHash.values()))
        value = []
        for files in tmpResult:
             value += files 

        print '_',len(value),
        if len(value) > 0:
            removedFile = []
            while True:
                result[filecount] = []
                size = len(value)        
                #if isDebugMode: print '\nb', value[0]
                print '/',    
                for f in range(1, size):
                    if dofilecmp(value[0], value[f]) == True:                
                        if isDebugMode : print '\n',value[0], ' = ', value[f], '\n'
                        result[filecount].append(value[f])
                        removedFile.append(value[f])
                result[filecount].append(value[0])
                removedFile.append(value[0])
                value = list(set(value) - set(removedFile))
                filecount += 1
                if len(value) == 0:
                    break
        print '%', 

    
    nextFileCount = filecount + 10;
    filecount = len(bigdupfile)
    print "\n* Start get same files >= ",LIMITED_SIZE, filecount
    
    for key,value in bigdupfile.iteritems():
        print '.',len(value),
        myHash = {}
        for f in value:
            fileHash = getMyHash(f)
            if myHash.get(fileHash) != None:
               myHash[fileHash].append(f)
            else:
               myHash[fileHash] = [f]  
        
        tmpResult = list(filter(lambda x: len(x) >= 3, myHash.values()))
        aDupfile = []
        for files in tmpResult:
            aDupfile += files 
       
        filecount = len(aDupfile)
        print '_',filecount,
        if filecount >= 1:
            for file in aDupfile:  
                print filecount,
                fileHash = getHashValue(file)
                if result.get(fileHash) != None:
                   result[fileHash].append(file)
                else:
                   result[fileHash] = [file]
                if isDebugMode : print '>',
            print '%', 

        tmpOnlyTwoFiles = list(filter(lambda x: len(x) == 2, myHash.values()))
        filecount = len(tmpOnlyTwoFiles)
        print '__',filecount,
        if filecount >= 1:
            for files in tmpOnlyTwoFiles:  
                result[nextFileCount] = []
                if dofilecmp2(files[0], files[1]):
                    result[nextFileCount].append(files[0])
                    result[nextFileCount].append(files[1])
                    nextFileCount += 1
                if isDebugMode : print '>',
            print '%', 


    if len(result) > 1:
        results = list(filter(lambda x: len(x) >= 2, result.values()))
        print "\n* Start find same files", len(results)    
        
        if len(results) >= 1:
            if not os.path.exists('dupfiles'):
                os.makedirs('dupfiles')
        
            resultfile = open('result.html','w')
            resultfile.write('<html><body>')
        
            for files in results:
                tfiles = files[1:]
                print files[0]
                resultfile.write('[ <a href=\"' + files[0] + '\">' + files[0] + '</a> ]<br><ul>')
                for file in tfiles:
                    #print file
                    afilename = os.path.basename(file)
                    afilepath = os.path.join('dupfiles', afilename)
        
                    if not os.path.exists(afilepath):
                        if isMoveFile:
                            shutil.move(file, afilepath)
                        print file,' -> ',afilepath
                        if isMoveFile:
                            resultfile.write('<li><a href=\"' + afilepath + '\">' + afilepath + '</a></li><br>')
                        else:
                            resultfile.write('<li><a href=\"' + file + '\">' + file + '</a></li><br>')
                    else:
                        afilepath = os.path.join('dupfiles', 'a' + str(random.randrange(100,999)) + '_' + afilename)
                        if isMoveFile: 
                            shutil.move(file, afilepath)
                        print file,' ->> ',afilepath
                        if isMoveFile:
                            resultfile.write('<li><a href=\"' + afilepath + '\"> ->' +  afilepath + '</a><li><br>')
                        else:
                            resultfile.write('<li><a href=\"' + file + '\"> ->' + file + '</a></li><br>')
                print "-" * 20
                resultfile.write('</ul>')
            resultfile.write('<br>' + myVersion + '<br>')
            resultfile.write('</body></html>')
            resultfile.close()
        else:
            print "\n* There is no duplicated file" 
    else:
        print "\n* There is no duplicated file" 

    if len(error_msg) > 0:
        for em in error_msg:
            print em

def dofilecmp(f1, f2):
    bufsize = LIMITED_SIZE
    with open(f1, 'rb') as fp1, open(f2, 'rb') as fp2:
        b1 = fp1.read(bufsize)
        b2 = fp2.read(bufsize)
        if b1 != b2:
            return False
        return True


def dofilecmp2(f1, f2):
    bufsize = LIMITED_SIZE
    with open(f1, 'rb') as fp1, open(f2, 'rb') as fp2:
        while True:
            b1 = fp1.read(bufsize)
            b2 = fp2.read(bufsize)
            if b1 != b2:
                return False
            if not b1:
                return True
    
  
def getHashValue(filepath):
    chunksize = LIMITED_SIZE
    hash = hashlib.md5()

    with open(filepath, 'rb') as afile:
        buf = afile.read(chunksize)
        while len(buf) > 0:
            buf = afile.read(chunksize)
            hash.update(buf)

    retHash = hash.hexdigest()
    #print retHash 
    return retHash


def getMyHash(filepath):
    chunksize = 1024

    with open(filepath, 'rb') as afile:
        buf = afile.read(chunksize)

    buf = buf + '0.62700000000000000000000000000000000000000000000000000000000'
    return buf[0:1024]


def printHelp():
    print "\n[Help]"
    print "Usage : pyrmdup [option] FolderName" 
    print "option:"
    print " -d : print log"
    print " -m : move all duplicated files to dupfiles folder"
    print " -h : show help message"
    print "\nThis program DO NOT GUARANTEE YOUR DATA and any problem!\n" 
    

if __name__ == '__main__':
    start_time = timeit.default_timer()
 
    if (len(sys.argv) < 2) or ('-h' in sys.argv[1:]):
        printHelp()
    else:
        main(sys.argv[1:])

    print '\n', myVersion, timeit.default_timer()-start_time

