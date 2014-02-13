#include <stdlib.h>
#include <inttypes.h>
#include <string.h>

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

int32_t two_arg(int16_t lal, char *bla) {
    return (int32_t) lal + *(bla + 1);
}

char *lolstr(int num, char *s) {
    char *_s = calloc(num,sizeof(char));
    int64_t i = 0, _i = 0;

    for (i=0; i<num; (i+=2, _i++)) {
        _s[_i] = s[i];
    }
    return _s;
}