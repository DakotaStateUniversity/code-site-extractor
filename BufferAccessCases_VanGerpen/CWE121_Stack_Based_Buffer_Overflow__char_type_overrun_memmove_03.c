// =========VANGERPEN TEST CASE 01===========
//TOTAL SITES: 17

//All comments by me will be denoted with the "//" comment



/* TEMPLATE GENERATED TESTCASE FILE
Filename: CWE121_Stack_Based_Buffer_Overflow__char_type_overrun_memmove_03.c
Label Definition File: CWE121_Stack_Based_Buffer_Overflow.label.xml
Template File: point-flaw-03.tmpl.c
*/
/*
 * @description
 * CWE: 121 Stack Based Buffer Overflow
 * Sinks: type_overrun_memmove
 *    GoodSink: Perform the memmove() and prevent overwriting part of the structure
 *    BadSink : Overwrite part of the structure by incorrectly using the sizeof(struct) in memmove()
 * Flow Variant: 03 Control flow: if(5==5) and if(5!=5)
 *
 * */

#include "std_testcase.h"
#ifndef _WIN32
#include <wchar.h>
#endif

/* SRC_STR is 20 char long, including the null terminator */
#define SRC_STR "0123456789abcde0123"

typedef struct _charVoid
{
    char charFirst[16];
    void * voidSecond;
    void * voidThird;
} charVoid;

#ifndef OMITBAD

void CWE121_Stack_Based_Buffer_Overflow__char_type_overrun_memmove_03_bad()
{
    if(5==5)
    {
        {
            charVoid structCharVoid;
//INSURE buffer access inside "if" body of function
            structCharVoid.voidSecond = (void *)SRC_STR;
            /* Print the initial block pointed to by structCharVoid.voidSecond */
//INSURE buffer access inside "if" body of function   
            printLine((char *)structCharVoid.voidSecond);
            /* FLAW: Use the sizeof(structCharVoid) which will overwrite the pointer voidSecond */
            memmove(structCharVoid.charFirst, SRC_STR, sizeof(structCharVoid));
//INSURE buffer access inside "if" body of function
            structCharVoid.charFirst[(sizeof(structCharVoid.charFirst)/sizeof(char))-1] = '\0'; /* null terminate the string */
//INSURE buffer access inside "if" body of function    
            printLine((char *)structCharVoid.charFirst);
//INSURE buffer access inside "if" body of function    
            printLine((char *)structCharVoid.voidSecond);
        }
    }
}

#endif /* OMITBAD */

#ifndef OMITGOOD

/* good1() uses if(5!=5) instead of if(5==5) */
static void good1()
{
    if(5!=5)
    {
        /* INCIDENTAL: CWE 561 Dead Code, the code below will never run */
        printLine("Benign, fixed string");
    }
    else
    {
        {
            charVoid structCharVoid;
//INSURE buffer access inside "else" body of function   
            structCharVoid.voidSecond = (void *)SRC_STR;
            /* Print the initial block pointed to by structCharVoid.voidSecond */
//INSURE buffer access inside "else" body of function 
            printLine((char *)structCharVoid.voidSecond);
            /* FIX: Use sizeof(structCharVoid.charFirst) to avoid overwriting the pointer voidSecond */
            memmove(structCharVoid.charFirst, SRC_STR, sizeof(structCharVoid.charFirst));
//INSURE buffer access inside "else" body of function             
            structCharVoid.charFirst[(sizeof(structCharVoid.charFirst)/sizeof(char))-1] = '\0'; /* null terminate the string */
//INSURE buffer access inside "else" body of function             
            printLine((char *)structCharVoid.charFirst);
//INSURE buffer access inside "else" body of function             
            printLine((char *)structCharVoid.voidSecond);
        }
    }
}

/* good2() reverses the bodies in the if statement */
static void good2()
{
    if(5==5)
    {
        {
            charVoid structCharVoid;
//INSURE buffer access inside "if" body of function 
            structCharVoid.voidSecond = (void *)SRC_STR;
            /* Print the initial block pointed to by structCharVoid.voidSecond */
//INSURE buffer access inside "if" body of function 
            printLine((char *)structCharVoid.voidSecond);
            /* FIX: Use sizeof(structCharVoid.charFirst) to avoid overwriting the pointer voidSecond */
            memmove(structCharVoid.charFirst, SRC_STR, sizeof(structCharVoid.charFirst));
//INSURE buffer access inside "if" body of function 
            structCharVoid.charFirst[(sizeof(structCharVoid.charFirst)/sizeof(char))-1] = '\0'; /* null terminate the string */
//INSURE buffer access inside "if" body of function 
            printLine((char *)structCharVoid.charFirst);
//INSURE buffer access inside "if" body of function 
            printLine((char *)structCharVoid.voidSecond);
        }
    }
}

void CWE121_Stack_Based_Buffer_Overflow__char_type_overrun_memmove_03_good()
{
    good1();
    good2();
}

#endif /* OMITGOOD */

/* Below is the main(). It is only used when building this testcase on
   its own for testing or for building a binary to use in testing binary
   analysis tools. It is not used when compiling all the testcases as one
   application, which is how source code analysis tools are tested. */

#ifdef INCLUDEMAIN

int main(int argc, char * argv[])
{
    /* seed randomness */
    srand( (unsigned)time(NULL) );
#ifndef OMITGOOD
    printLine("Calling good()...");
//INSURE Function call
    CWE121_Stack_Based_Buffer_Overflow__char_type_overrun_memmove_03_good();
    printLine("Finished good()");
#endif /* OMITGOOD */
#ifndef OMITBAD
    printLine("Calling bad()...");
//INSURE function call
    CWE121_Stack_Based_Buffer_Overflow__char_type_overrun_memmove_03_bad();
    printLine("Finished bad()");
#endif /* OMITBAD */
    return 0;
}

#endif
