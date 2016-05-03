//INSURE 9 sites found
/* TEMPLATE GENERATED TESTCASE FILE
Filename: CWE124_Buffer_Underwrite__char_declare_memmove_01.c
Label Definition File: CWE124_Buffer_Underwrite.stack.label.xml
Template File: sources-sink-01.tmpl.c
*/
/*
 * @description
 * CWE: 124 Buffer Underwrite
 * BadSource:  Set data pointer to before the allocated memory buffer
 * GoodSource: Set data pointer to the allocated memory buffer
 * Sink: memmove
 *    BadSink : Copy string to data using memmove
 * Flow Variant: 01 Baseline
 *
 * */

#include "std_testcase.h"

#include <wchar.h>

#ifndef OMITBAD

void CWE124_Buffer_Underwrite__char_declare_memmove_01_bad()
{
    char * data;
    char dataBuffer[100];
    memset(dataBuffer, 'A', 100-1);
//INSURE Array access inside function
    dataBuffer[100-1] = '\0';
    /* FLAW: Set data pointer to before the allocated memory buffer */
    data = dataBuffer - 8;
    {
        char source[100];
        memset(source, 'C', 100-1); /* fill with 'C's */
//INSURE Array access inside function
        source[100-1] = '\0'; /* null terminate */
        /* POTENTIAL FLAW: Possibly copying data to memory before the destination buffer */
        memmove(data, source, 100*sizeof(char));
        /* Ensure the destination buffer is null terminated */
//INSURE Array access inside function
        data[100-1] = '\0';
        printLine(data);
    }
}

#endif /* OMITBAD */

#ifndef OMITGOOD

/* goodG2B uses the GoodSource with the BadSink */
static void goodG2B()
{
    char * data;
    char dataBuffer[100];
    memset(dataBuffer, 'A', 100-1);
//INSURE Array access inside function
    dataBuffer[100-1] = '\0';
    /* FIX: Set data pointer to the allocated memory buffer */
    data = dataBuffer;
    {
        char source[100];
        memset(source, 'C', 100-1); /* fill with 'C's */
//INSURE Array access inside function
        source[100-1] = '\0'; /* null terminate */
        /* POTENTIAL FLAW: Possibly copying data to memory before the destination buffer */
        memmove(data, source, 100*sizeof(char));
        /* Ensure the destination buffer is null terminated */
//INSURE Array access inside function
        data[100-1] = '\0';
        printLine(data);
    }
}

void CWE124_Buffer_Underwrite__char_declare_memmove_01_good()
{
//INSURE Function call
    goodG2B();
}

#endif /* OMITGOOD */

/* Below is the main(). It is only used when building this testcase on
 * its own for testing or for building a binary to use in testing binary
 * analysis tools. It is not used when compiling all the testcases as one
 * application, which is how source code analysis tools are tested.
 */

#ifdef INCLUDEMAIN

int main(int argc, char * argv[])
{
    /* seed randomness */
    srand( (unsigned)time(NULL) );
#ifndef OMITGOOD
    printLine("Calling good()...");
//INSURE Function call
    CWE124_Buffer_Underwrite__char_declare_memmove_01_good();
    printLine("Finished good()");
#endif /* OMITGOOD */
#ifndef OMITBAD
    printLine("Calling bad()...");
//INSURE Function call
    CWE124_Buffer_Underwrite__char_declare_memmove_01_bad();
    printLine("Finished bad()");
#endif /* OMITBAD */
    return 0;
}

#endif
