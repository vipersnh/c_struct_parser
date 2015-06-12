
typedef unsigned char uint8;
typedef unsigned long long uint64;
typedef unsigned int uint32;
typedef void * test_id_t;
typedef struct test_data_struct test_data_struct;
typedef unsigned short test_type;

typedef enum {
    SUCCESS = 5,
    FAILURE,
} test_enum_t;

//typedef struct {
//    char a;
//    unsigned long long b;
//    char c;
//    long double d;
//    char e;
//} test_struct_t;

typedef struct test_complex_struct {
    uint32 a;
    uint64 b[3];
    uint8 c[5][3];
    test_type * d;
    test_type * e[3];
    test_type f[0];
    test_type g[];
} test_complex_struct;


