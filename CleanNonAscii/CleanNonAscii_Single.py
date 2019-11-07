#
# CleanNonAscii.py
#
# Help to clean non ascii character
#
# 2019-11-06 @Michell =      First version
#

import sys
from os import path
from os import walk
from time import time as time
import shutil
import traceback

exclude_dir = ['Build']
proc_file_ext = ['.asi', '.asl', '.inf', '.c', '.h']
proc_file_list = []

def exceptreport(e):
    error_class = e.__class__.__name__
    detail = e.args[0]
    cl, exc, tb = sys.exc_info()
    lastCallStack = traceback.extract_tb(tb)[-1]
    fileName = lastCallStack[0]
    lineNum = lastCallStack[1]
    funcName = lastCallStack[2]
    errMsg = 'File \"{}\", line {}, in {}( ): [{}] {}'.format(fileName, lineNum, funcName, error_class, detail)
    print(errMsg)


def getprintname(fullpath):
    if len(fullpath) >= 128:
        p = fullpath[:-64] + '...\\' + path.basename(fullpath)
    else:
        p = fullpath
    return p


def processfile(filename):
    sf = []
    af = []
    IsChange = False
    pn = getprintname(filename)
    print('\r{:128s}'.format(pn), end='', flush=True)
    with open(filename, 'rb') as f:
        try:
            for i, s in enumerate(f):
                # skip unicode BOM
                if (s[0:2] == b'\xff\xfe') or\
                    (s[0:2] == b'\xfe\xff') or\
                    (s[0:3] == b'\xef\xbb\xbf') or\
                    (s[0:4] == b'\x00\x00\xfe\xff') or\
                    (s[0:4] == b'\x00\x00\xff\xfe'):
                    return
                sf.append(s)
                for c in s:
                    if (c == 0) or (c >= 0x9) and (c <= 0x0D):
                        af.append(c.to_bytes(1, byteorder="little"))
                    elif (c > 0x7F) or (c < 0x20):
                        print()
                        print('\r{:128s} LINE:{:d}'.format(pn, i+1), end='')
                        IsChange = True
                        af.append(b' ')
                    else:
                        af.append(c.to_bytes(1, byteorder="little"))
        except Exception as e:
                exceptreport(e)
                return
    if IsChange:
        print()
        shutil.copy2(filename, filename + '_bak')

        with open(filename, 'wb') as f:
            f.write(b''.join(af))


if __name__== "__main__":
    try:
        # test parameters vaild
        Tdir = sys.argv[1]
        if path.exists(Tdir) != True:
            Tdir=None
    except Exception as e:
        exceptreport(e)
        Tdir=None

    start_time = time()
    print('Collecting files...')
    if Tdir != None:
        for root, dirs, files in walk(Tdir):
            dirs[:] = [d for d in dirs if d not in exclude_dir]
            for file in files:
                if (path.splitext(file)[-1]) in proc_file_ext:
                    absname = path.join(root, file)
                    proc_file_list.append(absname)

    print('Starting to process files...')
    if len(proc_file_list) > 0:
        for file in proc_file_list:
            processfile(file)

    end_time = time()
    print()
    print('Finished in {:.3f} s'.format(end_time - start_time))
