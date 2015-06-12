import os
import re
import pprint
from pdb import set_trace
from pycparser import parse_file, c_parser, c_generator
from pycparser.c_ast import (Typedef, TypeDecl, Typename, Struct, Enum,
    Union, IdentifierType, Enum, PtrDecl, ArrayDecl)
from collections import namedtuple, OrderedDict
import enum

pp = pprint.PrettyPrinter(indent=4)

class arch_types_enum_t(enum.Enum):
    M32 = 0
    M64 = 1

class endian_types_enum_t(enum.Enum):
    LittleEndian=0
    BigEndian=0

class type_t(enum.Enum):
    default = 0
    array = 1
    pointer = 2
    typedec = 3
    typedef = 4
    enum = 5
    struct = 6
    union = 7

type_info_t = namedtuple("type_info_t", ["type_id", "name", "size", "align", "info"])
array_info_t = namedtuple("array_into_t", ["array_count", "array_type"]);
ptr_info_t  = namedtuple("ptr_info_t", ["actual_type"])
typedef_info_t = namedtuple("typedef_info_t", ["actual_type"])
enum_info_t   = namedtuple("enum_info_t", ["enum_dict"])
struct_info_t = namedtuple("struct_info_t", ["fields"])
union_info_t  = namedtuple("union_info_t", ["fields"])

field_into_t = namedtuple("field_into_t", ["var_name", "size", "byte_offset", "type"]);

def form_type_info(type_info_type, name, size, align=None, info=None, ):
    return type_info_t(type_info_type, name, size, 
            size if align==None else align, 
            info)
    
class struct_parser_t:
    parser_types = OrderedDict()
    def __init__(self, c_file, arch=arch_types_enum_t.M32,
            endian=endian_types_enum_t.LittleEndian):
        self.c_file = c_file
        self.arch   = arch
        self.is_64bit = self.arch==arch_types_enum_t.M64
        self.is_32bit = self.arch==arch_types_enum_t.M32
        self.word_size = 4 if self.arch==arch_types_enum_t.M32 else 8
        self.max_align = self.word_size
        self.endian = endian
        self.__update_basic_types__()
        self.ast = parse_file(c_file, use_cpp=True)
        for ext in self.ast.ext:
            t_obj = self.get_type_info(ext)
            self.parser_types[t_obj.name] = t_obj
        pp.pprint(self.parser_types)
        set_trace()
    
    def isWordAligned(self, num):
        return num % self.word

    def wordBytesLeft(self, offset):
        offset = offset % self.word
        return self.word - offset

    def __update_basic_types__(self):
        is_64bit = True if self.arch==arch_types_enum_t.M64 else False
        self.parser_types["__ptr__"] = form_type_info(type_t.default, "__ptr__", 8 if is_64bit else 4)
        self.parser_types["enum"] = form_type_info(type_t.default, "enum", 4) # Check this later
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
        self.parser_types["double"] = form_type_info(type_t.default, "double", 8, align=4)
        self.parser_types["long double"] = form_type_info(type_t.default, "long double", 12, align=4)
        

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
            return form_type_info(type_id, name, size, None, info)
        elif type(ext)==TypeDecl:
            if type(ext.type)==Enum:
                enumList = ext.type.values.enumerators
                enum_dict = OrderedDict()
                enum_val  = 0;
                for item in enumList:
                    if item.value:
                        enum_val = int(item.value.value, 0)
                    enum_dict[item.name] = enum_val
                    enum_val += 1
                return form_type_info(type_t.enum, ext.declname, self.parser_types["enum"].size,
                        None, enum_info_t(enum_dict))
            elif type(ext.type)==IdentifierType:
                type_name = " ".join(ext.type.names)
                if self.isKnownType(type_name):
                    return self.parser_types[type_name]
                else:
                    assert 0, "Unknown type"
            elif type(ext.type)==Struct:
                if self.isKnownType(ext.type.name):
                    return self.parser_types[type_name]
                else:
                    type_id = type_t.struct;
                    if ext.type.decls:
                        fields = []
                        offset = 0
                        total_size = 0
                        for decl in ext.type.decls:
                            t_obj = self.get_type_info(decl.type)
                            while t_obj.size:
                                if ((offset % t_obj.align) == 0) or ((offset % self.max_align) == 0):
                                    byte_offset = offset
                                    break
                                else:
                                    offset += 1 # Increment by byte wise
                            offset += t_obj.size
                            field = field_into_t(decl.name, t_obj.size, byte_offset, t_obj)
                            fields.append(field)
                        
                        if offset % self.word_size==0:
                            total_size = offset
                        else:
                            rem_bytes = self.word_size - (offset % self.word_size)
                            total_size = offset + rem_bytes
                        self.parser_types[ext.type.name] = form_type_info(type_t.struct,
                            ext.type.name, total_size, None, struct_info_t(fields))
                    else:
                        # Create empty structure info parsed_types and return it;
                        self.parser_types[ext.type.name] = form_type_info(type_t.struct,
                            ext.type.name, None, None);
                    return self.parser_types[ext.type.name];
            elif self.isKnownType(ext.declname):
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
            return form_type_info(type_id, name, size, None, info)
        elif type(ext)==PtrDecl:
            t_obj = self.get_type_info(ext.type)
            type_id = type_t.pointer
            name = t_obj.name
            size = 8 if self.arch==arch_types_enum_t.M64 else 4
            info = ptr_info_t(t_obj)
            return form_type_info(type_id, name, size, None, info)
        elif type(ext)==ArrayDecl:
            array_count = 0;
            if ext.dim:
                array_count = int(ext.dim.value, 0)
            array_type = self.get_type_info(ext.type)
            size = array_type.size
            size *= array_count
            return form_type_info(type_t.array, "", size, None, array_info_t(array_count, array_type))
        else:
            set_trace();
            assert 0, "Code this condition"

    def isKnownType(self, type_name):
        if type_name in self.parser_types.keys():
            return True
        else:
            return False



















