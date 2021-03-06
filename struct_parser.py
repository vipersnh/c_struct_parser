import os
import re
import pprint
from pdb import set_trace
from pycparser import parse_file, c_parser, c_generator
from pycparser.c_ast import (Typedef, TypeDecl, Typename, Struct, Enum, Constant, 
        ID, NamedInitializer, Decl, UnaryOp, Union, IdentifierType, Enum, PtrDecl, ArrayDecl)
from collections import namedtuple, OrderedDict
import enumeration
from basic_decode import *
from target_defs import *
from dict_struct  import dict_struct_t

pp = pprint.PrettyPrinter(indent=4)

class type_t(enumeration.Enum):
    basic = 0
    array = 1
    pointer = 2
    typedef = 4
    enum = 5
    struct = 6
    union = 7

class signed_t(enumeration.Enum):
    signed = 0
    unsigned = 1

inst_info_t = namedtuple("inst_info_t", ["name", "qualifier", "type", "values"])
value_info_t = namedtuple("value_info_t", ["qualifier", "value"])
type_info_t = namedtuple("type_info_t", ["type_id", "name", "size", "sign", "align", "info"])
array_info_t = namedtuple("array_info_t", ["array_count", "array_type"]);
ptr_info_t  = namedtuple("ptr_info_t", ["actual_type"])
typedef_info_t = namedtuple("typedef_info_t", ["actual_type"])
enum_info_t   = namedtuple("enum_info_t", ["enum_dict"])
struct_info_t = namedtuple("struct_info_t", ["fields"])
union_info_t  = namedtuple("union_info_t", ["fields"])

struct_field_into_t = namedtuple("struct_field_into_t", ["var_name", "size", "byte_offset", "type"]);

unpack_info_t = namedtuple("unpack_info_t", ["var_name", "size", "type_name", "value"]);

def form_type_info(type_info_type, name, size, sign=None, align=None, info=None):
    try:
        if align != None and align > 8:
            set_trace()
            pass
    except:
        set_trace(); pass
    return type_info_t(type_info_type, name, size, sign,
            size if align==None else align, 
            info)
    
class struct_parser_t:
    trace_bytes = None
    trace_byte_idx = 0
    basic_decode = None
    parser_types = OrderedDict()
    parser_undefined_types = OrderedDict()
    inst_vars  = OrderedDict()
    parser_ctypes_spec = OrderedDict()
    def __init__(self, c_file, arch=arch_types_enum_t.M32,
            endian=endian_types_enum_t.LittleEndian):
        self.c_file = c_file
        self.target_arch = arch
        self.target_endian = endian
        self.target_is_64bit = arch==arch_types_enum_t.M64
        self.target_is_32bit = arch==arch_types_enum_t.M32
        self.target_word_size = 4 if arch==arch_types_enum_t.M32 else 8
        self.target_max_align = self.target_word_size
        self.isTargetLittleEndian = True if endian==endian_types_enum_t.LittleEndian else False
        self.ast = parse_file(c_file, use_cpp=True)
        self.basic_decoder = basic_decode_t(endian, arch)
        self.update_defs()
  
    def set_trace_bytes(self, trace_bytes, trace_byte_idx):
        self.trace_bytes    = trace_bytes
        self.trace_byte_idx = trace_byte_idx

    def update_defs(self):
        self.__update_basic_types__()
        for ext in self.ast.ext:
            if type(ext)==Decl and ext.name:
                inst_obj = self.get_instance_info(ext)
                if inst_obj:
                    self.inst_vars[inst_obj.name] = inst_obj
            else:
                t_obj = self.get_type_info(ext)
                self.parser_types[t_obj.name] = t_obj
        self.basic_decoder = basic_decode_t(self.target_endian, self.target_arch)
        self.update_empty_defs()

    def update_empty_defs(self):
        for t_name in self.parser_types.keys():
            t_obj = self.parser_types[t_name]
            if t_obj.size==None:
                rmKey = False
                if t_obj.type_id==type_t.typedef:
                    defined_type = t_obj.info.actual_type.name
                    act_t_obj = self.parser_types[defined_type]
                    if act_t_obj.size==None:
                        # Remove key from dict and put in undefined 
                        rmKey = True
                    else:
                        self.parser_types[t_name] = type_info_t(t_obj.type_id, 
                            t_obj.name, act_t_obj.size, act_t_obj.sign, act_t_obj.align,
                            typedef_info_t(act_t_obj))
                else:
                    rmKey = True
                
                if rmKey:
                    self.parser_types.pop(t_name, None)
                    self.parser_undefined_types[t_name] = t_obj

    def isWordAligned(self, num):
        return num % self.word

    def set_arch_n_endianness(self, arch, endian):
        self.target_arch = arch
        self.target_endian = endian
        self.target_is_64bit = arch==arch_types_enum_t.M64
        self.target_is_32bit = arch==arch_types_enum_t.M32
        self.isTargetLittleEndian = True if endian==endian_types_enum_t.LittleEndian else False
        self.update_defs();

    def wordBytesLeft(self, offset):
        offset = offset % self.word
        return self.word - offset

    def __update_basic_types__(self):
        self.parser_types["__ptr__"]                = form_type_info(type_t.basic, "__ptr__", 8 if self.target_is_64bit else 4)
        self.parser_types["enum"]                   = form_type_info(type_t.basic, "enum", 4) # Check this later
        self.parser_types["void"]                   = form_type_info(type_t.basic, "void", 0)
        self.parser_types["char"]                   = form_type_info(type_t.basic, "char", 1, signed_t.signed)
        self.parser_types["signed char"]            = form_type_info(type_t.basic, "signed char", 1, signed_t.signed)
        self.parser_types["unsigned char"]          = form_type_info(type_t.basic, "unsigned char", 1, signed_t.unsigned)
        self.parser_types["short"]                  = form_type_info(type_t.basic, "short", 2, signed_t.signed)
        self.parser_types["signed short"]           = form_type_info(type_t.basic, "signed short", 2, signed_t.signed)
        self.parser_types["unsigned short"]         = form_type_info(type_t.basic, "unsigned short", 2, signed_t.unsigned)
        self.parser_types["short int"]              = form_type_info(type_t.basic, "short", 2, signed_t.signed)
        self.parser_types["signed short int"]       = form_type_info(type_t.basic, "signed short", 2, signed_t.signed)
        self.parser_types["unsigned short int"]     = form_type_info(type_t.basic, "unsigned short", 2, signed_t.unsigned)
        self.parser_types["int"]                    = form_type_info(type_t.basic, "int", 4, signed_t.signed)
        self.parser_types["signed int"]             = form_type_info(type_t.basic, "signed int", 4, signed_t.signed)
        self.parser_types["unsigned int"]           = form_type_info(type_t.basic, "unsigned int", 4, signed_t.unsigned)
        self.parser_types["long"]                   = form_type_info(type_t.basic, "long", 8 if self.target_is_64bit else 4, signed_t.signed)
        self.parser_types["signed long"]            = form_type_info(type_t.basic, "signed long", 8 if self.target_is_64bit else 4, signed_t.signed)
        self.parser_types["unsigned long"]          = form_type_info(type_t.basic, "unsigned long", 8 if self.target_is_64bit else 4, signed_t.unsigned)
        self.parser_types["long int"]               = form_type_info(type_t.basic, "long", 8 if self.target_is_64bit else 4, signed_t.signed)
        self.parser_types["signed long int"]        = form_type_info(type_t.basic, "signed long", 8 if self.target_is_64bit else 4, signed_t.signed)
        self.parser_types["unsigned long int"]      = form_type_info(type_t.basic, "unsigned long", 8 if self.target_is_64bit else 4, signed_t.unsigned)
        self.parser_types["long long"]              = form_type_info(type_t.basic, "long long", 8, signed_t.signed)
        self.parser_types["signed long long"]       = form_type_info(type_t.basic, "signed long long", 8, signed_t.signed)
        self.parser_types["unsigned long long"]     = form_type_info(type_t.basic, "unsigned long long", 8, signed_t.unsigned)
        self.parser_types["float"]                  = form_type_info(type_t.basic, "float", 4, signed_t.signed)
        self.parser_types["double"]                 = form_type_info(type_t.basic, "double", 8, signed_t.signed, align=4)
        self.parser_types["long double"]            = form_type_info(type_t.basic, "long double", 12, signed_t.signed, align=4)
        

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

            return form_type_info(type_t.typedef, name, size, t_obj.sign, align, info)
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
                enum_dict[enum_val] = item.name
                enum_val += 1
            return form_type_info(type_t.enum, ext.name, self.parser_types["enum"].size,
                    None, None, enum_info_t(enum_dict))
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
                target_max_align = 0
                for decl in ext.decls:
                    t_obj = self.get_type_info(decl.type)
                    t_obj = self.finalizeType(t_obj)
                    while t_obj.size:
                        if t_obj.align > target_max_align:
                            target_max_align = t_obj.align
                        if ((offset % t_obj.align) == 0) or ((offset % self.target_max_align) == 0):
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
                
                if offset % target_max_align==0:
                    total_size = offset
                else:
                    rem_bytes = self.target_max_align - (offset % self.target_max_align)
                    total_size = offset + rem_bytes
                return form_type_info(type_t.struct, ext.name, total_size, None, target_max_align, 
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
                target_max_align = 0
                max_size = 0
                for decl in ext.decls:
                    t_obj = self.get_type_info(decl.type)
                    t_obj = self.finalizeType(t_obj)
                    if t_obj.align > target_max_align:
                        target_max_align = t_obj.align
                    if t_obj.size > max_size:
                        max_size = t_obj.size
                    field = struct_field_into_t(decl.name, t_obj.size, 0, t_obj)
                    fields.append(field)
                offset += max_size
                if offset % target_max_align==0:
                    total_size = offset
                else:
                    rem_bytes = self.target_max_align - (offset % self.target_max_align)
                    total_size = offset + rem_bytes
                return form_type_info(type_t.union, ext.name, total_size, None, 
                        target_max_align, union_info_t(fields))
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
            size = 8 if self.target_is_64bit else 4
            info = ptr_info_t(t_obj)
            return form_type_info(type_t.pointer, name, size, None, None, info)
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
            return form_type_info(type_t.array, "", size, None, align, array_info_t(array_count, array_type))
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
            [orig_t_obj, t_obj] = self.get_actual_type(" ".join(ext.type.type.names))
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
                return inst_info_t(declname, qualifier, orig_t_obj, values)
        elif t_obj.type_id==type_t.basic:
            if ext.init:
                init = ext.init.exprs[0]
                assert len(ext.init.exprs)==1, "What to do"
                [name, sub_init] = self.get_init_value(init)
            else:
                # Uninitialized declaration
                return inst_info_t(declname, qualifier, orig_t_obj, None)

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
    def get_actual_type(self, type_name=None, t_obj=None):
        if t_obj==None:
            orig_t_obj = t_obj = self.parser_types[type_name]
        else:
            orig_t_obj = t_obj
        while t_obj.type_id==type_t.typedef:
            try:
                t_obj = t_obj.info.actual_type
            except:
                set_trace()
                pass
        return [orig_t_obj, t_obj]

    def get_basic_value(self, t_obj, n_elem=1):
        if n_elem==1:
            value = self.basic_decoder.f_dict[t_obj.name](self.trace_bytes[self.trace_byte_idx:])
            self.trace_byte_idx += t_obj.size
        else:
            value = []
            for idx in range(n_elem):
                try:
                    value.append(self.basic_decoder.f_dict[t_obj.name](self.trace_bytes[self.trace_byte_idx:]))
                    self.trace_byte_idx += t_obj.size
                except:
                    set_trace()
        return unpack_info_t(None, t_obj.size, t_obj.name, value)

#    def get_basic_value(self, byte_array, t_obj, n_elem=1):
#        if t_obj.name in ["char", "signed char"] :
#            if n_elem > 1:
#                value = byte_array[0:t_obj.size*n_elem].split(
#                            b'\x00')[0].split(b'\x00')[0].decode()
#            else:
#                value = byte_array[0:t_obj.size*n_elem]
#        elif t_obj.name in ["void", "float", "double", "long double"]:
#            set_trace(); pass
#        else:
#            isSigned = True if t_obj.sign==signed_t.signed else False
#            if n_elem==1:
#                value = decode_as_nbytes_number(byte_array, t_obj.size, isSigned,
#                             self.target_word_size, self.isTargetLittleEndian)
#            else:
#                value = []
#                for idx in range(n_elem):
#                    value.append(decode_as_nbytes_number(byte_array, t_obj.size, isSigned,
#                             self.target_word_size, self.isTargetLittleEndian))
#        return [unpack_info_t(None, t_obj.size*n_elem, t_obj.name, value), byte_array[t_obj.size*n_elem:]]

    def unpack_as_type(self, type_name=None, t_obj = None, count=1):
        if count > 1:
            [_, t_obj] = self.get_actual_type(type_name, t_obj)
            array_t_obj = array_info_t(count, t_obj)
            return self.unpack_as_type(type_name, form_type_info(type_t.array, "", count*t_obj.size,
                        info=array_t_obj))
    
        [orig_t_obj, t_obj] = self.get_actual_type(type_name, t_obj)
#        print("Tname={0}, Tid={1}, typename={2},".format(t_obj.name, t_obj.type_id, type_name))
        assert t_obj.size != None and t_obj.size >= 0, "Error in typename"
        if t_obj.type_id==type_t.struct:
            value = [];
            trace_byte_idx_old = self.trace_byte_idx
            for field in t_obj.info.fields:
                self.trace_byte_idx = trace_byte_idx_old + field.byte_offset
                unpack_info = self.unpack_as_type(None, field.type)
                value.append(unpack_info_t(field.var_name, unpack_info.size, unpack_info.type_name, 
                    unpack_info.value))
            self.trace_byte_idx = trace_byte_idx_old + t_obj.size
            return unpack_info_t(None, t_obj.size, type_name, value)
        elif t_obj.type_id==type_t.basic:
            return self.get_basic_value(t_obj)
        elif t_obj.type_id==type_t.pointer:
            t_obj = self.parser_types["__ptr__"];
            unpack_info = self.get_basic_value(t_obj)
            return unpack_info_t(None, unpack_info.size, unpack_info.type_name, unpack_info.value)
        elif t_obj.type_id==type_t.enum:
            t_obj_enum = self.parser_types["int"] # Decode as normal int value 
            unpack_info = self.get_basic_value(t_obj_enum)
            return unpack_info_t(None, unpack_info.size, t_obj.name, t_obj.info[0][unpack_info.value])
        elif t_obj.type_id==type_t.array:
            [_, act_t_obj] = self.get_actual_type(t_obj=t_obj.info.array_type)
            if act_t_obj.type_id==type_t.basic:
                return self.get_basic_value(act_t_obj, t_obj.info.array_count)
            else:
                value = []
                for idx in range(t_obj.info.array_count):
                    unpack_info = self.unpack_as_type(t_obj=act_t_obj)
                    value.append(unpack_info)
                return unpack_info_t(None, t_obj.size, t_obj.name, value)
        else:
            set_trace()
            pass


    def sizeof(self, type_name):
        return self.parser_types[type_name].size


    def pretty_print(self, unpack_info, ts=0):
        op_ts = " "*ts if ts else ""
        try:
            [orig_t_obj, t_obj] = self.get_actual_type(unpack_info.type_name);
        except:
            set_trace()
            [orig_t_obj, t_obj] = self.get_actual_type(unpack_info.type_name);
            pass
        op = op_ts;
        if t_obj.type_id==type_t.struct:
            op += unpack_info.type_name + " " + (unpack_info.var_name if unpack_info.var_name else "") + " = {\n"
            for value in unpack_info.value:
                op += self.pretty_print(value, ts+4)
            op += op_ts + "}; \n"
            return op
        elif t_obj.type_id==type_t.basic:
            op += unpack_info.type_name + " " + unpack_info.var_name + " = " + hex(unpack_info.value) + "\n";
            return op

    def unpack_info_to_struct(self, unpack_info):
        struct = dict_struct_t();
        if type(unpack_info.value)==list:
            if type(unpack_info.value[0])==int:
                return unpack_info.value
            else:
                for value in unpack_info.value:
                    if value.var_name:
                        struct.__setattr__(value.var_name, self.unpack_info_to_struct(value))
                    else:
                        struct.__setattr__("_unknown_", self.unpack_info_to_struct(value))
        else:
            return unpack_info.value
        return struct

