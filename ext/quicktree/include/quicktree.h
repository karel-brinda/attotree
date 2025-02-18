#ifndef QUICKTREE_H
#define QUICKTREE_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdio.h>

/* Declaration of the quicktree function implemented in your C code */
void quicktree(FILE *input);

/* Declaration of the wrapper function */
void run_quicktree(const char *input_filename);

#ifdef __cplusplus
}
#endif

#endif // QUICKTREE_H

