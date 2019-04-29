#! /usr/local/Cellar/python/3.7.0/bin/python3

import os
import argparse


## You can comment out these two lines after you run it once
from pip._internal import main as pipmain
pipmain(['install','pydicom'])


import pydicom





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Modify Series Description and Number',usage='updateSeriesBatch.py /path/to/[scanner] -ext "dcm" -v')
    parser.add_argument('root_dir',help='Path to top folder in containing folder')
    parser.add_argument('-ext',default=None, type=str, help='Dicom is recognized by this extension: STR')
    parser.add_argument('-sw', default=None, type=str, help='Dicom is recognized by starting with: STR')
    parser.add_argument('-v','--verbose', action='store_true', help='Give option to show BASIC status updates')
    parser.add_argument('-d', '--verbose_detailed', action='store_true', help='Give option to show ALL status updates')
    parser.add_argument('-ip', '--inplace', action='store_true', help='Default is to to COPY, not replace. Give to make changes inplace.')
    args = parser.parse_args()

    if args.ext is not None:
        if not args.ext.startswith('.'):
            args.ext = '.{0}'.format(args.ext)

    args.root_dir = os.path.abspath(args.root_dir)
    if not os.path.realpath('.').startswith(os.path.realpath(args.root_dir)):
        outputpath = os.path.join('./',os.path.basename(args.root_dir))
        exists = os.path.isdir(outputpath)
        if exists:
            answer = input('WARNING directory exists and files may be overwritten. Do you wish to continue? (y/n)')
            if answer.lower().startswith("y"):
                print("Overwriting files")
            else:
                print("Script stopped")
                exit()
        new_se_num = 9000
        for dirpath,dirnames,filenames in os.walk(args.root_dir):
            new_se_num += 1
            if args.verbose:
                print('Working in: {0}'.format(dirpath))
            for file in filenames:
                fpath = os.path.abspath(os.path.join(dirpath,file))
                swbool = True
                extbool = True

                if args.sw is not None:
                    if not os.path.basename(fpath).startswith(args.sw):
                        swbool = False

                if args.ext is not None:
                    if not os.path.basename(fpath).endswith(args.ext):
                        extbool = False

                if swbool and extbool:
                    dcm = pydicom.dcmread(fpath)
                    orig_se_desc = dcm.SeriesDescription
                    orig_se_num = dcm.SeriesNumber
                    se_desc = os.path.basename(os.path.dirname(fpath))
                    dcm.SeriesDescription = se_desc
                    dcm.SeriesNumber = new_se_num
                    if args.inplace:
                        dcm.save_as(fpath)
                        if args.verbose:
                            print('{0}\n    SeriesDescription {1} --> {2}'.format(fpath, orig_se_desc, se_desc))
                            print(     '    SeriesNumber {0} --> {1}'.format(orig_se_num, new_se_num))
                    else:
                        structure = os.path.join(outputpath, os.path.relpath(dirpath, args.root_dir))
                        if not os.path.isdir(structure):
                            os.makedirs(structure)
                        npath = os.path.join(structure,os.path.basename(fpath))
                        dcm.save_as(npath)
                        if args.verbose and args.verbose_detailed:
                            print('{0} --> {1}\n    SeriesDescription {2} --> {3}'.format(fpath,npath,orig_se_desc, se_desc))
                            print(             '    SeriesNumber {0} --> {1}'.format(orig_se_num, new_se_num))
        if not args.inplace:
            print('Results Saved: {0}'.format(os.path.abspath(outputpath)))
    else:
        print('Error: Working directory cannot be a subdirectory of root_dir')
