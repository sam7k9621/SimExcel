#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import argparse
import src.ExcelModule as EM
import sys

def main() :
    parser =  argparse.ArgumentParser()
    parser.add_argument("-i", "--inputfile", type=str, required=True)
    try:
        opt = parser.parse_args(sys.argv[1:])
    except:
        raise
    pd.options.display.precision = 2
    pd.set_option('display.precision', 2)
    df = pd.read_csv(opt.inputfile)

    exccmd = EM.ExcelHandler(df)
    exccmd.StartWrapper()
    with open(opt.inputfile, 'w+') as f:
        df.to_csv(f, index=False)
    print( 'Successfully write file : "{}"'.format(opt.inputfile) )

if __name__ == '__main__':
    main()
