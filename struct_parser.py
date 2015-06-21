import os
import re
import pprint
from pdb import set_trace
from pycparser import parse_file, c_parser, c_generator
from pycparser.c_ast import (Typedef, TypeDecl, Typename, Struct, Enum, Constant, 
        ID, NamedInitializer, Decl, UnaryOp, Union, IdentifierType, Enum, PtrDecl, ArrayDecl)
from collections import namedtuple, OrderedDict
import enumeration

pp = pprint.PrettyPrinter(indent=4)

class arch_types_enum_t(enumeration.Enum):
    M32 = 0
    M64 = 1

class endian_types_enum_t(enumeration.Enum):
    LittleEndian=0
    BigEndian=1

class type_t(enumeration.Enum):
    basic = 0
    array = 1
    pointer = 2
    typedef = 4
    enum = 5
    struct = 6
    union = 7

inst_info_t = namedtuple("inst_info_t", ["name", "qualifier", "type", "values"])
value_info_t = namedtuple("value_info_t", ["qualifier", "value"])
type_info_t = namedtuple("type_info_t", ["type_id", "name", "size", "align", "info"])
array_info_t = namedtuple("array_into_t", ["array_count", "array_type"]);
ptr_info_t  = namedtuple("ptr_info_t", ["actual_type"])
typedef_info_t = namedtuple("typedef_info_t", ["actual_type"])
enum_info_t   = namedtuple("enum_info_t", ["enum_dict"])
struct_info_t = namedtuple("struct_info_t", ["fields"])
union_info_t  = namedtuple("union_info_t", ["fields"])

struct_field_into_t = namedtuple("struct_field_into_t", ["var_name", "size", "byte_offset", "type"]);

def form_type_info(type_info_type, name, size, align=None, info=None, ):
    if align != None and align > 8:
        set_trace()
        pass
    return type_info_t(type_info_type, name, size, 
            size if align==None else align, 
            info)
    
class struct_parser_t:
    parser_types = OrderedDict()
    inst_vars  = OrderedDict()
    parser_ctypes_spec = OrderedDict()
    def __init__(self, c_file, arch=arch_types_enum_t.M32,
            endian=endian_types_enum_t.LittleEndian):
        self.c_file = c_file
        self.arch   = arch
        self.is_64bit = self.arch==arch_types_enum_t.M64
        self.is_32bit = self.arch==arch_types_enum_t.M32
        self.word_size = 4 if self.arch==arch_types_enum_t.M32 else 8
        self.max_align = self.word_size
        self.isTargetBigEndian = True if endian==endian_types_enum_t.BigEndian else False
        self.__update_basic_types__()
        self.ast = parse_file(c_file, use_cpp=True)
        for ext in self.ast.ext:
            if type(ext)==Decl and ext.name:
                inst_obj = self.get_instance_info(ext)
                if inst_obj:
                    self.inst_vars[inst_obj.name] = inst_obj
            else:
                t_obj = self.get_type_info(ext)
                self.parser_types[t_obj.name] = t_obj
    
    def isWordAligned(self, num):
        return num % self.word

    def set_endianness(self, endian):
        self.isTargetBigEndian = True if endian==endian_types_enum_t.BigEndian else False

    def wordBytesLeft(self, offset):
        offset = offset % self.word
        return self.word - offset

    def __update_basic_types__(self):
        is_64bit = True if self.arch==arch_types_enum_t.M64 else False
        self.parser_types["__ptr__"] = form_type_info(type_t.basic, "__ptr__", 8 if is_64bit else 4)
        self.parser_types["enum"] = form_type_info(type_t.basic, "enum", 4) # Check this later
        self.parser_types["void"] = form_type_info(type_t.basic, "void", 0)
        self.parser_types["char"] = form_type_info(type_t.basic, "char", 1)
        self.parser_types["signed char"] = form_type_info(type_t.basic, "signed char", 1)
        self.parser_types["unsigned char"] = form_type_info(type_t.basic, "unsigned char", 1)
        self.parser_types["short"] = form_type_info(type_t.basic, "short", 2)
        self.parser_types["signed short"] = form_type_info(type_t.basic, "signed short", 2)
        self.parser_types["unsigned short"] = form_type_info(type_t.basic, "unsigned short", 2)
        self.parser_types["short int"] = form_type_info(type_t.basic, "short", 2)
        self.parser_types["signed short int"] = form_type_info(type_t.basic, "signed short", 2)
        self.parser_types["unsigned short int"] = form_type_info(type_t.basic, "unsigned short", 2)
        self.parser_types["int"] = form_type_info(type_t.basic, "int", 4)
        self.parser_types["signed int"] = form_type_info(type_t.basic, "signed int", 4)
        self.parser_types["unsigned int"] = form_type_info(type_t.basic, "unsigned int", 4)
        self.parser_types["long"] = form_type_info(type_t.basic, "long", 8 if is_64bit else 4)
        self.parser_types["signed long"] = form_type_info(type_t.basic, "signed long", 8 if is_64bit else 4)
        self.parser_types["unsigned long"] = form_type_info(type_t.basic, "unsigned long", 8 if is_64bit else 4)
        self.parser_types["long long"] = form_type_info(type_t.basic, "long long", 8)
        self.parser_types["signed long long"] = form_type_info(type_t.basic, "signed long long", 8)
        self.parser_types["unsigned long long"] = form_type_info(type_t.basic, "unsigned long long", 8)
        self.parser_types["float"] = form_type_info(type_t.basic, "float", 4)
        self.parser_types["double"] = form_type_info(type_t.basic, "double", 8, align=4)
        self.parser_types["long double"] = form_type_info(type_t.basic, "long double", 12, align=4)
        

    def get_type_info(self, ext):
        name = None
        size = None
        info = None
        field_name = None
        if type(ext)==Typedef:
            t_obj = self.get_type_info(ext.type)
            name = ext.name
            try:
                info = typedef_info_t(t_obj)
            except:
                set_trace()
            size = t_obj.size
            align = t_obj.align

            return form_type_info(type_t.typedef, name, size, align, info)
        elif type(ext)==Enum:
            enumList = ext.values.enumerators
            enum_dict = OrderedDict()
            enum_val  = 0;
            for item in enumList:
                if item.value:
                    if type(item.value)==UnaryOp:
                        op = item.value.op
                        enum_val = int(op+item.value.expr.value, 0)
                    elif type(item.value)==Constant:
                        enum_val = int(item.value.value, 0)
                enum_dict[item.name] = enum_val
                enum_val += 1
            return form_type_info(type_t.enum, ext.name, self.parser_types["enum"].size,
                    None, enum_info_t(enum_dict))
        elif type(ext)==IdentifierType:
            type_name = " ".join(ext.names)
            if self.isKnownType(type_name):
                return self.parser_types[type_name]
            else:
                set_trace()
                assert 0, "Unknown type"
        elif type(ext)==Struct:
            if ext.decls:
                fields = []
                offset = 0
                total_size = 0
                max_align = 0
                for decl in ext.decls:
                    t_obj = self.get_type_info(decl.type)
                    t_obj = self.finalizeType(t_obj)
                    while t_obj.size:
                        if t_obj.align > max_align:
                            max_align = t_obj.align
                        if ((offset % t_obj.align) == 0) or ((offset % self.max_align) == 0):
                            byte_offset = offset
                            break
                        else:
                            offset += 1 # Increment by byte wise
                    try:
                        offset += t_obj.size
                    except:
                        set_trace()
                        pass
                    field = struct_field_into_t(decl.name, t_obj.size, byte_offset, t_obj)
                    fields.append(field)
                
                if offset % max_align==0:
                    total_size = offset
                else:
                    rem_bytes = self.max_align - (offset % self.max_align)
                    total_size = offset + rem_bytes
                return form_type_info(type_t.struct, ext.name, total_size, max_align, 
                        struct_info_t(fields))
            elif self.isKnownType(ext.name):
                return self.parser_types[ext.name]
            else:
                # Create empty structure info parsed_types and return it;
                return form_type_info(type_t.struct,
                    ext.name, None, None)
        elif type(ext)==Union:
            if ext.decls:
                fields = []
                offset = 0
                total_size = 0
                max_align = 0
                max_size = 0
                for decl in ext.decls:
                    t_obj = self.get_type_info(decl.type)
                    t_obj = self.finalizeType(t_obj)
                    if t_obj.align > max_align:
                        max_align = t_obj.align
                    if t_obj.size > max_size:
                        max_size = t_obj.size
                    field = struct_field_into_t(decl.name, t_obj.size, 0, t_obj)
                    fields.append(field)
                offset += max_size
                if offset % max_align==0:
                    total_size = offset
                else:
                    rem_bytes = self.max_align - (offset % self.max_align)
                    total_size = offset + rem_bytes
                return form_type_info(type_t.union, ext.name, total_size, max_align,
                        union_info_t(fields))
            elif self.isKnownType(ext.name):
                return self.parser_types[ext.name]
            else:
                # Create empty union info parsed_types and return it;
                return form_type_info(type_t.union,
                    ext.name, None, None)
        elif type(ext)==TypeDecl:
            return self.updateParserTypes(self.get_type_info(ext.type))
        elif type(ext)==Decl:
            return self.updateParserTypes(self.get_type_info(ext.type))
        elif type(ext)==PtrDecl:
            t_obj = self.get_type_info(ext.type)
            name = t_obj.name
            size = 8 if self.arch==arch_types_enum_t.M64 else 4
            info = ptr_info_t(t_obj)
            return form_type_info(type_t.pointer, name, size, None, info)
        elif type(ext)==ArrayDecl:
            array_count = 0;
            if ext.dim:
                array_count = int(ext.dim.value, 0)
            array_type = self.get_type_info(ext.type)
            size = array_type.size
            align = array_type.align
            try:
                size *= array_count
            except:
                set_trace()
                pass
            return form_type_info(type_t.array, "", size, align, array_info_t(array_count, array_type))
        else:
            set_trace();
            assert 0, "Code this condition"

    def isKnownType(self, type_name):
        if type_name in self.parser_types.keys():
            if self.parser_types[type_name]:
                return True
            else:
                return False
        else:
            return False

    def updateParserTypes(self, t_obj):
        if t_obj.name:
            self.parser_types[t_obj.name] = t_obj
        return t_obj

    def finalizeType(self, t_obj):
        if t_obj.size:
            return t_obj
        else:
            try:
                if t_obj.type_id==type_t.typedef:
                    sub_t_obj = t_obj.info.actual_type
                    return self.finalizeType(sub_t_obj)
                elif t_obj.type_id==type_t.struct:
                    return self.parser_types[t_obj.name]
                elif t_obj.type_id==type_t.array:
                    return t_obj;
                else:
                    set_trace()
                    assert 0, "What is this"
            except:
                set_trace()
                pass
    
    def get_instance_info(self, ext):
        qualifier = None
        type_obj = None
        declname = ext.name
        try:
            t_obj = self.get_actual_type(" ".join(ext.type.type.names))
        except:
            return None
        if ext.quals:
            qualifier = ext.quals[0]
        if t_obj.type_id==type_t.struct:
            if ext.init:
                sub_insts = OrderedDict()
                for idx, init in enumerate(ext.init.exprs):
                    [name, sub_inst] = self.get_init_value(init)
                    if name:
                        sub_insts[name] = sub_inst
                    else:
                        sub_insts[idx] = sub_inst
                values = []
                for idx, field in enumerate(t_obj.info.fields):
                    if field.var_name in sub_insts.keys():
                        # Named initialization
                        sub_inst = sub_insts[field.var_name]
                        values.append(inst_info_t(field.var_name, sub_inst.qualifier,
                            field.type, sub_inst.value))
                    elif idx in sub_insts.keys():
                        # Indexed initialization
                        sub_inst = sub_insts[idx]
                        values.append(inst_info_t(field.var_name, sub_inst.qualifier,
                            field.type, sub_inst.value))
                    else:
                        set_trace()
                        values.append(inst_info_t(field.var_name, None, field.type, 
                            None))
                return inst_info_t(declname, qualifier, t_obj, values)
        elif t_obj.type_id==type_t.basic:
            if ext.init:
                init = ext.init.exprs[0]
                assert len(ext.init.exprs)==1, "What to do"
                [name, sub_init] = self.get_init_value(init)
            else:
                # Uninitialized declaration
                return inst_info_t(declname, qualifier, t_obj, None)

    def get_init_value(self, init):
        name = None
        if type(init)==NamedInitializer:
            [_, value] = self.get_init_value(init.expr)
            name = init.name[0].name
            return [name, value]
        elif type(init)==Constant:
            type_name = init.type
            if self.parser_types[type_name].type_id==type_t.basic:
                value = init.value
                return [name, value_info_t(None, value)]
            else:
                set_trace()
                pass
        elif type(init)==UnaryOp:
            value = self.evaluate_expr(init)
            return [name, value_info_t(None, value)]

    def evaluate_expr(self, expr):
        if expr.op=='sizeof':
            var_name = self.get_var_name(expr)
            type_name = self.get_type_name(expr)
            if var_name in self.inst_vars.keys():
                return self.inst_vars[var_name].type.size
            elif type_name in self.parser_types.keys():
                return self.finalizeType(self.parser_types[type_name]).size
            else:
                set_trace()
                pass
        else:
            set_trace()
            pass

    def get_var_name(self, expr):
        return expr.expr.name

    def get_type_name(self, expr):
        if type(expr)==UnaryOp:
            return self.get_type_name(expr.expr)
        elif type(expr)==ID:
            return None;
        elif type(expr)==Typename:
            return self.get_type_name(expr.type)
        elif type(expr)==TypeDecl:
            return self.get_type_name(expr.type)
        elif type(expr)==IdentifierType:
            return " ".join(expr.names)
        else:
            set_trace()
            pass
    def get_actual_type(self, type_name):
        t_obj = self.parser_types[type_name];
        while t_obj.type_id==type_t.typedef:
            t_obj = t_obj.info.actual_type
        return t_obj

    def get_basic_value(self, byte_array, byte_offset, basic_type_name):
        pass

    def unpack_as_type(self, byte_array, type_name):
        t_obj = self.get_actual_type(type_name)
        assert t_obj.size != None and t_obj.size >= 0, "Error in typename"
        assert len(byte_array) >= t_obj.size, "Input size is less than type size"
        if t_obj.type_id==type_t.struct:
            pass;
        else:
            set_trace()
            pass

    def sizeof(self, type_name):
        return self.parser_types[type_name].size







