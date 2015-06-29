#include <stdio.h>
#include <stdlib.h>
#include "struct_header.h"

#define TRACE_FILE "./trace.bin"
#define TRACE_CONTENTS_FILE "./trace_contents.txt"

#define True 0x01
#define False 0x00

trace_preamble_struct_t trace_preamble = {
    .isLittleEndian = 0,
    .wordsize       = 0,
};

trace_struct1_t trace_struct1 = {
    .field1_struct1 = 0xAB,
    .field2_struct1 = 0xABCD,
    .field3_struct1 = 0xABCDEFAD,
    .field4_struct1 = 0xABCDEFADABCDEFAD,
};

trace_struct2_t trace_struct2 = {
    .field1_struct2 = &trace_struct1,
    .field2_struct2 = 0xCD,
    .field3_struct2 = 0xCDEF,
    .field4_struct2 = 0xCDEF,
};

trace_struct3_t trace_struct3 = {
    .field1_struct3 = &trace_struct1,
    .field2_struct3 = &trace_struct2,
};

trace_struct4_t trace_struct4 = {
    .field1_struct4 = &trace_struct1,
    .field2_struct4 = &trace_struct2,
    .field3_struct4 = &trace_struct3,
};

void populate_endian_n_wordsize(trace_preamble_struct_t * preamble) 
{
    char endian[2] = {0, 1};
    uint16_t value = *(uint16_t *)endian;
    preamble->wordsize = sizeof(long);
    if (value == 0x01) {
        preamble->isLittleEndian = False;
    } else if (value == 0x0100) {
        preamble->isLittleEndian = True;
    } else {
        printf("Undefined condition, exiting !!\n");
        exit(-1);
    }
    return;
}

void print_struct_trace_preamble_struct(FILE * info_file, trace_preamble_struct_t * ptr)
{
    fprintf(info_file, "Struct trace_preamble_struct_t =>\n");
    fprintf(info_file, "    isLittleEndian => %u\n",    ptr->isLittleEndian);
    fprintf(info_file, "    wordsize       => %u\n",    ptr->wordsize);
}

void print_struct_trace_struct1(FILE * info_file, trace_struct1_t * ptr)
{
    fprintf(info_file, "Struct trace_struct1_t =>\n");
    fprintf(info_file, "    field1_struct1 => %u\n",    ptr->field1_struct1);
    fprintf(info_file, "    field2_struct1 => %u\n",    ptr->field2_struct1);
    fprintf(info_file, "    field3_struct1 => %u\n",    ptr->field3_struct1);
    fprintf(info_file, "    field4_struct1 => %lu\n",   ptr->field4_struct1);
}

void print_struct_trace_struct2(FILE * info_file, trace_struct2_t * ptr)
{
    fprintf(info_file, "Struct trace_struct2_t =>\n");
    fprintf(info_file, "    field1_struct2 => %p\n",    ptr->field1_struct2);
    fprintf(info_file, "    field2_struct2 => %u\n",    ptr->field2_struct2);
    fprintf(info_file, "    field3_struct2 => %u\n",    ptr->field3_struct2);
    fprintf(info_file, "    field4_struct2 => %u\n",   ptr->field4_struct2);
}

void print_struct_trace_struct3(FILE * info_file, trace_struct3_t * ptr)
{
    fprintf(info_file, "Struct trace_struct3_t =>\n");
    fprintf(info_file, "    field1_struct3 => %p\n",    ptr->field1_struct3);
    fprintf(info_file, "    field2_struct3 => %p\n",    ptr->field2_struct3);
}

void print_struct_trace_struct4(FILE * info_file, trace_struct4_t * ptr)
{
    fprintf(info_file, "Struct trace_struct4_t =>\n");
    fprintf(info_file, "    field1_struct4 => %p\n",    ptr->field1_struct4);
    fprintf(info_file, "    field2_struct4 => %p\n",    ptr->field2_struct4);
    fprintf(info_file, "    field3_struct4 => %p\n",    ptr->field3_struct4);
}




int main(void) 
{
    FILE *trace_file, *trace_info_file;
    trace_file      = fopen(TRACE_FILE, "wb");
    trace_info_file = fopen(TRACE_CONTENTS_FILE, "w");
    populate_endian_n_wordsize(&trace_preamble);
    printf("1. Writing trace_preamble to trace file.\n");
    fwrite(&trace_preamble, sizeof(trace_preamble), 1, trace_file);
    print_struct_trace_preamble_struct(trace_info_file, &trace_preamble);
    printf("2. Writing trace_struct1 to trace_file.\n");
    fwrite(&trace_struct1, sizeof(trace_struct1), 1, trace_file);
    print_struct_trace_struct1(trace_info_file, &trace_struct1);
    printf("3. Writing trace_struct2 to trace_file.\n");
    fwrite(&trace_struct2, sizeof(trace_struct2), 1, trace_file);
    print_struct_trace_struct2(trace_info_file, &trace_struct2);
    printf("4. Writing trace_struct3 to trace_file.\n");
    fwrite(&trace_struct3, sizeof(trace_struct3), 1, trace_file);
    print_struct_trace_struct3(trace_info_file, &trace_struct3);
    printf("5. Writing trace_struct4 to trace_file.\n");
    fwrite(&trace_struct4, sizeof(trace_struct4), 1, trace_file);
    print_struct_trace_struct4(trace_info_file, &trace_struct4);
    printf("6. Done\n");
    fclose(trace_file);
    fclose(trace_info_file);
    return 0;
}
