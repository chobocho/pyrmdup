#-*- coding: utf-8 -*-
import os
import sys
import timeit
import hashlib
import shutil
import random

myVersion = '-V0.627_170423a- Time:'
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
        print "Show file list"       

    folders = folderlist

    print '* Folders :'
    for f in folders:
        print f

    print "* Start read files"
    dict = {}  
    dupfile = []
    smalldupfile = {}
    result = {}  
  
    for folder in folders:
        if os.path.exists(folder):
            for (path, dir, files) in os.walk(folder):
                for filename in files:
                    tf = os.path.join(path, filename)
                    if isDebugMode: print tf
                    dict[tf] = os.path.getsize(tf);
                    #if isDebugMode: print ("%s/%s " % (path, filename))
                    if isDebugMode: print ("%s : %d" % (tf, dict[tf]))
                    if result.get(dict[tf]) == None:
                        result[dict[tf]] = 1
                    else:
                        result[dict[tf]] += 1 
        else:
            print "Error:",folder," is not exist"           

    print "\n* Start find same size files"             
    for key,value in dict.iteritems():  
        if result[value] != None and result[value] >= 2:
            #if isDebugMode: print key
            if value < LIMITED_SIZE:
                if isDebugMode: print '> ', key, value
                if smalldupfile.get(value) != None:
                    smalldupfile[value].append(key)
                else:
                    smalldupfile[value] = [key]
            else:
                dupfile.append(key)


    filecount = len(dupfile)
    print "\n* Start get hash of same files >= ",LIMITED_SIZE, filecount
    result = {}
    for file in dupfile:  
        print filecount,
        fileHash = getHashValue(file)
        if result.get(fileHash) != None:
           result[fileHash].append(file)
        else:
           result[fileHash] = [file]
        filecount -= 1
        print '>',


    print "\n* Start get same files < ",LIMITED_SIZE, len(result)
    filecount = 1
    for key,value in smalldupfile.iteritems():
        print '.',
        removedFile = []
        while True:
            result[filecount] = []
            size = len(value)        
            #if isDebugMode: print '\nb', value[0]
            print '/',    
            for f in range(1, size):
                if dofilecmp(value[0], value[f]) == True:                
                    print '\n',value[0], ' = ', value[f], '\n'
                    result[filecount].append(value[f])
                    removedFile.append(value[f])
            result[filecount].append(value[0])
            removedFile.append(value[0])
            value = list(set(value) - set(removedFile))
            filecount += 1
            if len(value) == 0:
                break
        print '%',    

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
        
        resultfile.write('</body></html>')
        resultfile.close()
    else:
        print "\n* There is no duplicated file" 
     
def dofilecmp(f1, f2):
    bufsize = LIMITED_SIZE
    with open(f1, 'rb') as fp1, open(f2, 'rb') as fp2:
        b1 = fp1.read(bufsize)
        b2 = fp2.read(bufsize)
        if b1 != b2:
            return False
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

