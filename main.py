import os
import argparse
from struct_parser import struct_parser_t

parser = argparse.ArgumentParser()
parser.add_argument('fnames', nargs="+")
parse_res = parser.parse_args()
fnames = parse_res.fnames;

if __name__=="__main__":
    parser = struct_parser_t(fnames[0]);


