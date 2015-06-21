from libc.stdio cimport printf
import pdb
import re;
import platform
import sys
import math

isHostLittleEndian = 1 if sys.byteorder=='little' else 0
hostWordSize    = int(re.findall("[0-9]+", platform.architecture()[0])[0]);

def decode_as_nbytes_number(unsigned char *data_ptr, unsigned char nbytes, unsigned char isSigned,
                             unsigned char targetWordSize, 
                             unsigned char isTargetLittleEndian):
    printf("data_ptr            = %p \n", data_ptr)
    printf("nbytes              = %u \n", nbytes)
    printf("isSigned            = %u \n", isSigned)
    printf("targetWordSize      = %u \n", targetWordSize)
    printf("isTargetLittleEndian   = %u \n", isTargetLittleEndian)
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


