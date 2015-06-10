import os
import re
from pdb import set_trace
from pycparser import parse_file, c_parser, c_generator
from pycparser.c_ast import (Typedef, TypeDecl, Typename, Struct, 
    Union, IdentifierType, Enum, PtrDecl)
from collections import namedtuple
from enum import Enum

class arch_types_enum_t(Enum):
    M32 = 0
    M64 = 1

class endian_types_enum_t(Enum):
    LittleEndian=0
    BigEndian=0

class type_t(Enum):
    default = 0
    pointer = 1
    typedec = 2
    typedef = 3
    enum = 4
    struct = 5
    union = 6

type_info_t = namedtuple("type_info_t", ["type_id", "name", "size", "info", "field_name"])
ptr_info_t  = namedtuple("ptr_info_t", ["actual_type"])
typedec_info_t = namedtuple("typedec_info_t", ["actual_type"])
typedef_info_t = namedtuple("typedef_info_t", ["actual_type"])
enum_info_t   = namedtuple("enum_info_t", ["enum_dict"])
struct_info_t = namedtuple("struct_info_t", ["fields"])
union_info_t  = namedtuple("union_info_t", ["fields"])


def form_type_info(type_info_type, name, size, info=None, field_name=None):
    return type_info_t(type_info_type, name, size, info, field_name)
    

class struct_parser_t:
    parser_types = {}
    def __init__(self, c_file, arch=arch_types_enum_t.M32,
            endian=endian_types_enum_t.LittleEndian):
        self.c_file = c_file
        self.arch   = arch
        self.endian = endian
        self.__update_basic_types__()
        self.ast = parse_file(c_file, use_cpp=True)
        for ext in self.ast.ext:
            t_obj = self.get_type_info(ext)
            self.parser_types[t_obj.name] = t_obj;

    def __update_basic_types__(self):
        is_64bit = True if self.arch==arch_types_enum_t.M64 else False
        self.parser_types["__ptr__"] = form_type_info(type_t.default, "__ptr__", 8 if is_64bit else 4)
        self.parser_types["void"] = form_type_info(type_t.default, "void", 0)
        self.parser_types["char"] = form_type_info(type_t.default, "char", 1)
        self.parser_types["signed char"] = form_type_info(type_t.default, "signed char", 1)
        self.parser_types["unsigned char"] = form_type_info(type_t.default, "unsigned char", 1)
        self.parser_types["short"] = form_type_info(type_t.default, "short", 2)
        self.parser_types["signed short"] = form_type_info(type_t.default, "signed short", 2)
        self.parser_types["unsigned short"] = form_type_info(type_t.default, "unsigned short", 2)
        self.parser_types["short int"] = form_type_info(type_t.default, "short", 2)
        self.parser_types["signed short int"] = form_type_info(type_t.default, "signed short", 2)
        self.parser_types["unsigned short int"] = form_type_info(type_t.default, "unsigned short", 2)
        self.parser_types["int"] = form_type_info(type_t.default, "int", 4)
        self.parser_types["signed int"] = form_type_info(type_t.default, "signed int", 4)
        self.parser_types["unsigned int"] = form_type_info(type_t.default, "unsigned int", 4)
        self.parser_types["long"] = form_type_info(type_t.default, "long", 8 if is_64bit else 4)
        self.parser_types["signed long"] = form_type_info(type_t.default, "signed long", 8 if is_64bit else 4)
        self.parser_types["unsigned long"] = form_type_info(type_t.default, "unsigned long", 8 if is_64bit else 4)
        self.parser_types["long long"] = form_type_info(type_t.default, "long long", 8)
        self.parser_types["signed long long"] = form_type_info(type_t.default, "signed long long", 8)
        self.parser_types["unsigned long long"] = form_type_info(type_t.default, "unsigned long long", 8)
        self.parser_types["float"] = form_type_info(type_t.default, "float", 4)
        self.parser_types["double"] = form_type_info(type_t.default, "double", 8)
        self.parser_types["long double"] = form_type_info(type_t.default, "long double", 10)
        

    def get_type_info(self, ext):
        type_id = None
        name = None
        size = None
        info = None
        field_name = None
        if type(ext)==Typedef:
            t_obj = self.get_type_info(ext.type)
            type_id = type_t.typedef
            name = ext.name
            try:
                info = typedef_info_t(t_obj)
            except:
                set_trace()
            size = t_obj.size
            return form_type_info(type_id, name, size, info)
        elif type(ext)==TypeDecl:
            if self.isKnownType(ext.declname):
                t_obj = self.parser_types[ext.declname]
            else:
                t_obj = self.get_type_info(ext.type)
            type_id = type_t.typedec
            name    = ext.declname
            try:
                info    = typedec_info_t(t_obj)
                size    = t_obj.size
            except:
                set_trace()
                pass
            return form_type_info(type_id, name, size, info)
        elif type(ext)==IdentifierType:
            type_name = " ".join(ext.names)
            if self.isKnownType(type_name):
                t_obj = self.parser_types[type_name];
                return t_obj;
            else:
                set_trace();
                assert 0, "Unknown type"
        elif type(ext)==PtrDecl:
            t_obj = self.get_type_info(ext.type);
            type_id = type_t.pointer;
            name = t_obj.name;
            size = 8 if self.arch==arch_types_enum_t.M64 else 4;
            info = ptr_info_t(t_obj);
            return form_type_info(type_id, name, size, info);
    def isKnownType(self, type_name):
        if type_name in self.parser_types.keys():
            return True
        else:
            return False



















