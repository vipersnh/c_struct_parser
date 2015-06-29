#ifndef _STRUCT_HEADER_H_
#define _STRUCT_HEADER_H_

#include <stdint.h>

typedef struct {
    uint8_t     isLittleEndian;
    uint8_t     wordsize;
} trace_preamble_struct_t;

typedef struct {
    uint8_t     field1_struct1;
    uint16_t    field2_struct1;
    uint32_t    field3_struct1;
    uint64_t    field4_struct1;
} trace_struct1_t;

typedef struct {
    trace_struct1_t   * field1_struct2;
    uint8_t             field2_struct2;
    uint16_t            field3_struct2;
    uint32_t            field4_struct2;
} trace_struct2_t;

typedef struct {
    trace_struct1_t   * field1_struct3;
    trace_struct2_t   * field2_struct3;
} trace_struct3_t;

typedef struct {
    trace_struct1_t   * field1_struct4;
    trace_struct2_t   * field2_struct4;
    trace_struct3_t   * field3_struct4;
} trace_struct4_t;

typedef struct {
    uint32_t        trace_struct_id;
    uint32_t        trace_struct_size;
} trace_header_struct_t;

trace_header_struct_t trace_struct1_header  = {
    .trace_struct_id    = 1,
    .trace_struct_size  = sizeof(trace_struct1_t),
};

trace_header_struct_t trace_struct2_header  = {
    .trace_struct_id    = 2,
    .trace_struct_size  = sizeof(trace_struct2_t),
};

trace_header_struct_t trace_struct3_header  = {
    .trace_struct_id    = 3,
    .trace_struct_size  = sizeof(trace_struct3_t),
};

trace_header_struct_t trace_struct4_header  = {
    .trace_struct_id    = 4,
    .trace_struct_size  = sizeof(trace_struct4_t),
};

#endif
