
typedef unsigned long long uint64;
typedef unsigned int uint32;
typedef void * test_id_t;
typedef struct test_data_struct test_data_struct;
typedef unsigned short test_type;

typedef enum {
    SUCCESS,
    FAILURE,
} test_enum_t;

typedef struct test_complex_struct {
    uint32 a;
    uint64 b;
    test_type c;
} test_complex_struct;
