#include <stdlib.h>

int64_t fact(int64_t n) {
    int result = 1, i = 1;
    for (;i<=n;i++) {
        result *= i;
    }
    return result;
}

int64_t fact2(int64_t n) {
    int64_t result = 1, i = 1;
    for (;i<=n;i++) {
        result *= i;
    }
    return result;
}