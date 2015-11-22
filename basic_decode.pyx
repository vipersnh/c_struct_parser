from libc.stdio cimport printf
import pdb
import re;
import platform
import sys
import math
from target_defs import endian_types_enum_t
from target_defs import arch_types_enum_t

isHostLittleEndian = 1 if sys.byteorder=='little' else 0
hostWordSize    = int(re.findall("[0-9]+", platform.architecture()[0])[0]);

class basic_decode_t:
    f_dict = dict()
    host_endianness = None
    host_wordSize   = None
    target_endianness = None
    target_wordSize   = None

    def __init__(self, endian=endian_types_enum_t.LittleEndian, arch_type=arch_types_enum_t.M32, 
            enumSize=4):
        self.target_endianness = endian
        self.target_wordSize = 4 if arch_type==arch_types_enum_t.M32 else 8
        self.target_enumSize = 4

        self.f_dict["__ptr__"]       = self.decode_as_unsigned_int if self.target_wordSize==4 else self.decode_as_unsigned_long_long
        self.f_dict["enum"]          = self.decode_as_unsigned_int if self.target_enumSize==4 else self.decode_as_unsigned_char
        self.f_dict["char"]          = self.decode_as_signed_char
        self.f_dict["signed char"]   = self.decode_as_signed_char
        self.f_dict["unsigned char"] = self.decode_as_unsigned_char
        self.f_dict["short"]         = self.decode_as_signed_short
        self.f_dict["signed short"]  = self.decode_as_signed_short
        self.f_dict["unsigned short"]= self.decode_as_unsigned_short
        self.f_dict["short int"]     = self.decode_as_signed_short
        self.f_dict["signed short int"]= self.decode_as_signed_short
        self.f_dict["unsigned short int"]= self.decode_as_unsigned_short
        self.f_dict["int"]               = self.decode_as_signed_int
        self.f_dict["signed int"]        = self.decode_as_signed_int
        self.f_dict["unsigned int"]      = self.decode_as_unsigned_int
        self.f_dict["long"]              = self.decode_as_signed_int if self.target_wordSize==4 else self.decode_as_signed_long_long
        self.f_dict["signed long"]       = self.decode_as_signed_int if self.target_wordSize==4 else self.decode_as_signed_long_long
        self.f_dict["unsigned long"]     = self.decode_as_unsigned_int if self.target_wordSize==4 else self.decode_as_unsigned_long_long
        self.f_dict["long int"]          = self.decode_as_signed_int if self.target_wordSize==4 else self.decode_as_signed_long_long
        self.f_dict["signed long int"]   = self.decode_as_signed_int if self.target_wordSize==4 else self.decode_as_signed_long_long
        self.f_dict["unsigned long int"] = self.decode_as_unsigned_int if self.target_wordSize==4 else self.decode_as_unsigned_long_long
        self.f_dict["long long"]         = self.decode_as_signed_long_long
        self.f_dict["signed long long"]  = self.decode_as_signed_long_long
        self.f_dict["unsigned long long"]= self.decode_as_unsigned_long_long
        self.f_dict["float"]             = self.decode_as_float
        self.f_dict["double"]            = self.decode_as_double
        self.f_dict["long double"]       = self.decode_as_long_double
        
    def decode_as_signed_char(self, unsigned char *data_ptr):
        return (<signed char *>data_ptr)[0]

    def decode_as_unsigned_char(self, unsigned char *data_ptr):
        return (<unsigned char *>data_ptr)[0]
    
    def decode_as_signed_short(self, unsigned char *data_ptr):
        return (<signed short *>data_ptr)[0]

    def decode_as_unsigned_short(self, unsigned char *data_ptr):
        return (<unsigned short *>data_ptr)[0]

    def decode_as_signed_int(self, unsigned char *data_ptr):
        return (<signed int *>data_ptr)[0]

    def decode_as_unsigned_int(self, unsigned char *data_ptr):
        return (<unsigned int *>data_ptr)[0]

    def decode_as_signed_long_long(self, unsigned char *data_ptr):
        return (<signed long long *>data_ptr)[0]

    def decode_as_unsigned_long_long(self, unsigned char *data_ptr):
        return (<unsigned long long *>data_ptr)[0]

    def decode_as_float(self, unsigned char *data_ptr):
        return (<float *>data_ptr)[0]
    
    def decode_as_double(self, unsigned char *data_ptr):
        return (<double *>data_ptr)[0]

    def decode_as_long_double(self, unsigned char *data_ptr):
        return (<long double *>data_ptr)[0]


def decode_as_nbytes_number(unsigned char *data_ptr, unsigned char nbytes, unsigned char isSigned,
                             unsigned char targetWordSize, 
                             unsigned char isTargetLittleEndian):
#    printf("data_ptr            = %p \n", data_ptr)
#    printf("nbytes              = %u \n", nbytes)
#    printf("isSigned            = %u \n", isSigned)
#    printf("targetWordSize      = %u \n", targetWordSize)
#    printf("isTargetLittleEndian   = %u \n", isTargetLittleEndian)
    if nbytes==1:
        if isSigned:
            return (<signed char *>data_ptr)[0]
        else:
            return (<unsigned char *>data_ptr)[0]
    else: 
        if isTargetLittleEndian:
            if nbytes==2:
                if isHostLittleEndian:
                    if isSigned:
                        return (<signed short*>data_ptr)[0]
                    else:
                        return (<unsigned short *>data_ptr)[0]
                else:
                    pass
            elif nbytes==4:
                if isHostLittleEndian:
                    if isSigned:
                        return (<int*>data_ptr)[0]
                    else:
                        return (<unsigned int *>data_ptr)[0]
                else:
                    pass
            elif nbytes==8:
                if isHostLittleEndian:
                    if isSigned:
                        return (<signed long long *>data_ptr)[0];
                    else:
                        return (<unsigned long long *>data_ptr)[0];
                else:
                    pass
            else:
                assert 0, "Unknown nbytes"
        else:
            if nbytes==2:
                if isHostLittleEndian:
                    pass
                else:
                    pass
            elif nbytes==4:
                if isHostLittleEndian:
                    pass
                else:
                    pass
            elif nbytes==8:
                if isHostLittleEndian:
                    pass
                else:
                    pass
            else:
                assert 0, "Unknown nbytes"
    return None

cdef decode_as_float(unsigned char *data_ptr, unsigned char targetWordSize, 
        unsigned char isTargetLittleEndian):
    pass
    return

if __name__ == '__main__':
    import os
    pass


