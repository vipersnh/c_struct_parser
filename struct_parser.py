import os;
import re;
from pdb import set_trace;
from pycparser import parse_file, c_parser, c_generator
from pycparser.c_ast import (Typedef, TypeDecl, Typename, Struct, 
    Union, IdentifierType, Enum, PtrDecl)
from collections import namedtuple
from enum import Enum

class arch_types_enum_t(Enum):
    M32=0;
    M64=1;

class endian_types_enum_t(Enum):
    LittleEndian=0;
    BigEndian=0;

class type_t(Enum):
    default=0;
    typedef=1;
    enum=2;
    struct=3;
    union=4;

type_info_t = namedtuple("type_info_t", ["type", "name", "size", "info", "field_name"]);
ptr_info_t  = namedtuple("ptr_info_t", ["actual_type"]);
typedef_info_t = namedtuple("typedef_info_t", ["actual_type"]);
enum_info_t   = namedtuple("enum_info_t", ["enum_dict"]);
struct_info_t = namedtuple("struct_info_t", ["fields"]);
union_info_t  = namedtuple("union_info_t", ["fields"]);


def form_type_info(type_info_type, name, size, info=None, field_name=None):
    return type_info_t(type_info_type, name, size, info, field_name);
    

class struct_parser_t:
    basic_types = {};
    parsed_types = {};
    def __init__(self, c_file, arch=arch_types_enum_t.M32,
            endian=endian_types_enum_t.LittleEndian):
        self.c_file = c_file;
        self.arch   = arch;
        self.endian = endian;
        self.__update_basic_types__();
        self.ast = parse_file(c_file, use_cpp=True);
        for ext in self.ast.ext:
            [name, obj] = self.get_type_info(ext);
            self.parsed_types[name] = obj;

    def __update_basic_types__(self):
        is_64bit = True if self.arch==arch_types_enum_t.M64 else False;
        self.basic_types["__ptr__"] = form_type_info(type_t.default, "__ptr__", 8 if is_64bit else 4);
        self.basic_types["char"] = form_type_info(type_t.default, "char", 1);
        self.basic_types["signed char"] = form_type_info(type_t.default, "signed char", 1);
        self.basic_types["unsigned char"] = form_type_info(type_t.default, "unsigned char", 1);
        self.basic_types["short"] = form_type_info(type_t.default, "short", 2);
        self.basic_types["signed short"] = form_type_info(type_t.default, "signed short", 2);
        self.basic_types["unsigned short"] = form_type_info(type_t.default, "unsigned short", 2);
        self.basic_types["short int"] = form_type_info(type_t.default, "short", 2);
        self.basic_types["signed short int"] = form_type_info(type_t.default, "signed short", 2);
        self.basic_types["unsigned short int"] = form_type_info(type_t.default, "unsigned short", 2);
        self.basic_types["int"] = form_type_info(type_t.default, "int", 4);
        self.basic_types["signed int"] = form_type_info(type_t.default, "signed int", 4);
        self.basic_types["unsigned int"] = form_type_info(type_t.default, "unsigned int", 4);
        self.basic_types["long"] = form_type_info(type_t.default, "long", 8 if is_64bit else 4);
        self.basic_types["signed long"] = form_type_info(type_t.default, "signed long", 8 if is_64bit else 4);
        self.basic_types["unsigned long"] = form_type_info(type_t.default, "unsigned long", 8 if is_64bit else 4);
        self.basic_types["long long"] = form_type_info(type_t.default, "long long", 8);
        self.basic_types["signed long long"] = form_type_info(type_t.default, "signed long long", 8);
        self.basic_types["unsigned long long"] = form_type_info(type_t.default, "unsigned long long", 8);
        self.basic_types["float"] = form_type_info(type_t.default, "float", 4);
        self.basic_types["double"] = form_type_info(type_t.default, "double", 8);
        self.basic_types["long double"] = form_type_info(type_t.default, "long double", 10);
        

    def get_type_info(self, ext):
        typ = None;
        name = None;
        size = None;
        info = None;
        field_name = None;
        if type(ext)==Typedef:
            act_name = " ".join(ext.type.type.names);
            typ = type_t.typedef;
            name = ext.name;
            info = typedef_info_t(act_name);
            if act_name in self.basic_types.keys():
                bt = self.basic_types[act_name];
                size = bt.size;
            elif act_name in self.parsed_types.keys():
                pt = self.parsed_types[act_name];
                size = pt.size;
            else:
                set_trace();
                assert 0, "Invalid situation";
            return [name, form_type_info(typ, name, size, info)]; 
        elif type(ext)==TypeDecl:
            set_trace();
            pass;




















