from pdb import set_trace
import sys
from os.path import dirname, abspath
path = dirname(abspath(__file__))
sys.path.append(path+"/../..")
import basic_decode
from struct_parser import struct_parser_t, endian_types_enum_t, arch_types_enum_t
import argparse
import pprint
prettyPrint = pprint.PrettyPrinter()
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('header_file', nargs=1)
arg_parser.add_argument('trace_file', nargs=1)
parse_res = arg_parser.parse_args()
header_file = parse_res.header_file[0]
trace_file  = parse_res.trace_file[0]
if __name__=="__main__":
    parser = struct_parser_t(header_file)
    trace_bytes_index = 0
    trace_bytes = open(trace_file, "rb").read()
    print("1. Reading trace_preamble from trace file.\n");
    [trace_preamble, trace_bytes] = parser.unpack_as_type(trace_bytes, "trace_preamble_struct_t")
    endian = endian_types_enum_t.LittleEndian if trace_preamble.value[0].value else endian_types_enum_t.BigEndian
    arch   = arch_types_enum_t.M32 if trace_preamble.value[1].value == 4 else arch_types_enum_t.M64
    parser.set_arch_n_endianness(arch, endian)
    print(parser.pretty_print(trace_preamble))
    print("2. Reading trace_struct1 from trace_file.\n");
    [trace_struct1, trace_bytes] = parser.unpack_as_type(trace_bytes, "trace_struct1_t")
    print(parser.pretty_print(trace_struct1))
    print("3. Reading trace_struct2 from trace_file.\n");
    [trace_struct2, trace_bytes] = parser.unpack_as_type(trace_bytes, "trace_struct2_t")
    print(parser.pretty_print(trace_struct2))
    print("4. Reading trace_struct3 from trace_file.\n");
    [trace_struct3, trace_bytes] = parser.unpack_as_type(trace_bytes, "trace_struct3_t")
    print(parser.pretty_print(trace_struct3))
    print("5. Reading trace_struct4 from trace_file.\n");
    [trace_struct4, trace_bytes] = parser.unpack_as_type(trace_bytes, "trace_struct4_t")
    print(parser.pretty_print(trace_struct4))
    print("6. Done\n");
