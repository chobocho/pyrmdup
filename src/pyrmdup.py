#-*- coding: utf-8 -*-
import os
import sys
import timeit
import hashlib
import shutil
import random
import filecmp

myVersion = '-V0.627_170418- Time:'
LIMITED_SIZE = 65536

def main(folderlist):
    isMoveFile = False

    if (folderlist[1] == '-m'):
         folders = folderlist[2:]
         isMoveFile = True
    else:
        folders = folderlist[1:]

    print 'Folders : ', folders, '\n'

    print "Start read files"
    dict = {}    
    for folder in folders:
        if os.path.exists(folder):
            for (path, dir, files) in os.walk(folder):
                for filename in files:
                    tf = os.path.join(path, filename)
                    print tf
                    tfs  = os.path.getsize(tf);
                    #print("%s/%s" % (path, filename))
                    dict[tf] = tfs  
                    #print ("%s : %d" % (tf, dict[tf]))

    print "Start find same size files"
    dupfile = []
    smalldupfile = {}
    result = {}   
    for key,value in dict.iteritems():
        if result.get(value) == None:
            result[value] = 1
        else:
            result[value] += 1 
                   
    for key,value in dict.iteritems():  
        if result[value] != None and result[value] >= 2:
            #print key
            if value < LIMITED_SIZE:
                if smalldupfile.get(value) != None:
                    smalldupfile[value].append(key)
                else:
                    smalldupfile[value] = [key]
            else:
                dupfile.append(key)


    filecount = len(dupfile)
    print "Start get hash of same files >= ",LIMITED_SIZE, filecount
    result = {}
    for file in dupfile:  
        print filecount,
        fileHash = getHashValue(file)
        if result.get(fileHash) != None:
        #if fileHash in result:
           result[fileHash].append(file)
        else:
           result[fileHash] = [file]
        filecount -= 1
        print '>',


    print "\nStart get hash of same files < ",LIMITED_SIZE, len(result)
    filecount = 0
    for key,value in smalldupfile.iteritems():
        filecount += 1
        result[filecount] = []
        removedFile = []
        print '.',
        while True:
            size = len(value)            
            for f in range(1, size):
                if filecmp.cmp(value[0], value[f]):
                     print value[0], ' = ', value[f], '\n'
                     result[filecount].append(value[f])
                     removedFile.append(value[f])
            result[filecount].append(value[0])
            removedFile.append(value[0])
            value = list(set(value) - set(removedFile))
            #print value, len(value), '\n'
            if len(value) == 0:
                break
        print '%',    

    print "\nStart find same files", len(result)    
    results = list(filter(lambda x: len(x) >= 2, result.values()))
    
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
        print "There is no duplicated file" 
     
  
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


if __name__ == '__main__':
    start_time = timeit.default_timer()
 
    if (len(sys.argv) < 2):
        print "Usage : pyrmdup FolderName"
    else:
        main(sys.argv)

    print '\n', myVersion, timeit.default_timer()-start_time

