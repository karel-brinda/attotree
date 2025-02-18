#include <stdio.h>
#include <stdlib.h>
#include "quicktree.h"  // This now declares both quicktree() and run_quicktree()

void run_quicktree(const char *input_filename) {
    FILE *input = fopen(input_filename, "r");
    if (!input) {
        fprintf(stderr, "Could not open file %s for reading\n", input_filename);
        exit(1);
    }
    quicktree(input);  // Now declared in quicktree.h
}
