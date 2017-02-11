#!/usr/bin/env python
# coding: utf-8

DESCRIPTION=""

import numpy as np
import argparse

try:
   import cPickle as pickle
except:
   import pickle

@profile
def main(args):
    pass



parser = argparse.ArgumentParser(description=DESCRIPTION)


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
