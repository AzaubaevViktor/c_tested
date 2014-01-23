#include <stdlib.h>

char *cutStr(char *str, int n) {
    int i = 0;
    char *result = calloc(n,sizeof(char));
    for (i=0; i<n; i++) {
        result[i] = str[n-1-i];
    }
    return result;
}