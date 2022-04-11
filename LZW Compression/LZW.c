#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DICTSIZE 4096
#define ENTRYSIZE 32

unsigned char dict[DICTSIZE][ENTRYSIZE];

// Global variables
int entryCounter = 256; // Integer variable tracking how many entries are currently in the dictionary
int valueOfStringIndex = 0; // Integer variable for tracking the index where the string was found in the dictionary
int offset = 0; // Integer variable for off setting search loop through the dictionary

// Prototypes
void encode(FILE *inputFile, FILE *outputFile);
void decode(FILE *inputFile, FILE *outputFile);
void initalizeDict();
int read12(FILE *infil);
int write12(FILE *outfil, int int12);
void flush12(FILE *outfil);
void strip_lzw_ext(char *fname);

int main(int argc, char *argv[]){

    // Variables
    char *firstInput = argv[1];     // Variable for first input argument
    char *secondInput = argv[2];    // Variable for second input argument
    char outputFileName[80];        // String variable for creating output file name

    FILE *fileInOperator;  // Variable for input file operations
    FILE *fileOutOperator = NULL; // Variable for output file operations

    // Setting output file name to same as input name.
    strcpy(outputFileName, firstInput);
    
    // Check if a file and encode or decode character were provided.
    if(argc < 2){
        printf("Error: No input file specified!");
        exit(1);

    }//if

    // If second argument is NULL print error, also if second argument is not e or d print error
    if (secondInput == NULL){
        printf("Invalid Usage, expected: LZW{input_file} [e|d]\n");
        exit(4);
    }
    else if (strcmp(secondInput, "e") != 0 && strcmp(secondInput, "d") != 0){
        printf("Invalid Usage, expected: LZW{input_file} [e|d]\n");
        exit(4);
    } //if

    // Open input file in read binary mode
    fileInOperator = fopen(firstInput, "rb");

    // If fileInOperator has a NULL value print error message
    if (fileInOperator == NULL)
    {
        printf("Read error: file not found or cannot be read\n");
        exit(2);
    }
    
    // Fill the first 0-255 elements of dict with ascii values
    initalizeDict();
   
    // Check value of secondInput and either encode or decode
    if (strcmp(secondInput, "e") == 0){
        
        // Adding .LZW to output file
        strcat(outputFileName, ".LZW");

        // Open output file in write binary mode
        fileOutOperator = fopen(outputFileName, "wb");

        // Encode file
        encode(fileInOperator, fileOutOperator);

    }else{

        // Stripping file extension .LZW
        strip_lzw_ext(outputFileName);

        // Open output file in write binary mode
        fileOutOperator = fopen(outputFileName, "wb");

        // Decode file
        decode(fileInOperator, fileOutOperator);

    }//if else

    // Close both files
    fclose(fileInOperator);
    fclose(fileOutOperator);

    // Exit code 0 means encoding or decoding was sucessful
    exit(0);

} //main

/*
 *  void encode(FILE *inputFile, FILE *outputFile);
 *  
 *  Encode takes two parameters one is an input file the other is an output file
 *  encode then reads one character at a time and checks if the character exists in the dictionary.
 *  If the character is not in the dictionary add it at a open index.
 *  If the character is in the dictionary set a string variable to be equal to character
 *  and grab a new character and append them and recheck.
 * 
 *  The output is a binary file type.
 * 
 */

void encode(FILE *inputFile, FILE *outputFile){

    // Variables
    unsigned char string[ENTRYSIZE];    // Array for holding char of strings
    int currentChar;   // Variable for holding current character of file
    int searchingBook;  // Index used for searching the dict
    int stringLength = 0;   // Current string length
    int stringAndCharacterLength = 0;   // Length of concatenated sting
    
    // While there is still more to be read
    while ((currentChar = getc(inputFile)) != -1){

        // Variables
        unsigned char stringAndCharacter[ENTRYSIZE];    // Bufffer for holding string concat
        int forLoopCounter; // Variable for looping counter
        int stringAndCharacterInDict = 0;   // Flag for if concatenated string is in dict or not; FALSE = 0, TRUE = 1
    
        // Setting stringAndCharacter equal to string
        for(forLoopCounter = 0; forLoopCounter < stringLength; forLoopCounter++){
            
            stringAndCharacter[forLoopCounter] = string[forLoopCounter];
            
        }//for
        
        // Setting stringAndCharacterLength equal to stringLength
        stringAndCharacterLength = stringLength;
       
        // Add currentChar to stringAndCharacter
        stringAndCharacter[stringAndCharacterLength] = currentChar;
        
        // Increment stringAndCharacterLength by 1
        stringAndCharacterLength++;

        //  Search dictionary to see if stringAndCharacter has already been added
        //  An offset is used to reduce the amount of iterations
        for(searchingBook = 0 + offset; searchingBook < entryCounter; searchingBook++){

            // If lengths are not the same go to next iteration
            if(dict[searchingBook][0] != stringAndCharacterLength || dict[searchingBook][1] != stringAndCharacter[0]){

                continue;

            }//if 

            // Set the flag to TRUE
            stringAndCharacterInDict = 1;

            // Loop through the word held at searchBook index and compare each character
            for(forLoopCounter = 2; forLoopCounter <= dict[searchingBook][0]; forLoopCounter++){
                   
                // If any character is not equal set stringAndCharacterInDict to zero and break out of loop
                if(dict[searchingBook][forLoopCounter] != stringAndCharacter[forLoopCounter - 1]){

                    // Set the flag to FALSE
                    stringAndCharacterInDict = 0; 

                    // Break out of this inner for loop as dictionary string at this index is not the same to stringAndCharacter string
                    break;

                }//if

            }//for

            // If stringAndCharacterInDict is equal to 1, set valueOfStringIndex to searchBook value, then break out of loop
            if(stringAndCharacterInDict == 1){
                
                // If seachingBook is less than 256 set offset to 256, otherwise set it to searchingBook value
                if(searchingBook < 256){

                    offset = 256;

                }else{

                    offset = searchingBook;

                }//if else
                
                // Setting valueOfStringIndex to searchingBook value
                valueOfStringIndex = searchingBook;

                // Break out of this outer for loop as string has been found
                break;

            }//if

        }//for
       
        // If stringAndCharacterInDict equals 1, concatenate stringAndCharacter to string
        if(stringAndCharacterInDict == 1){
            
            // Add currentChar to the end of string
            string[stringLength] = currentChar;
            
            // Increment stringLength by 1
            stringLength++;
            
        }else{

            // Write string's index value to file
            write12(outputFile, valueOfStringIndex);
        
            // Put the stringAndCharacter length into dict
            dict[entryCounter][0] = stringAndCharacterLength; 

            // Add stringAndCharacter to dict
            for(forLoopCounter = 1; forLoopCounter <= stringAndCharacterLength; forLoopCounter++){

                dict[entryCounter][forLoopCounter] = stringAndCharacter[forLoopCounter - 1];
    
            }//for
            
            // Increment entryCounter to next free slot
            entryCounter++;

            // Reset entryCounter when dictionary becomes full
            if(entryCounter >= DICTSIZE){

                entryCounter = 256;

            }//if
        
            // Set string to currentChar value
            string[0] = currentChar;

            // Set valueOfStringIndex to currentChar integer value
            valueOfStringIndex = currentChar;

            // Reset stringLength to 1
            stringLength = 1;

            // Setting offset to 256, since next iteration the string + character will have a length greater than one
            // Thus skipping the ascii values from 0 - 255
            offset = 256;

        }//if else 
        
    }//while

    // Flush the write function to output any numbers currently waiting
    write12(outputFile, valueOfStringIndex);
    flush12(outputFile);

} //encode

/* void decode(FILE *inputFile, FILE *outputFile)
 *
 *  inputFile is a FILE pointer to input file
 *  outputFile is a FILE pointer to output file
 * 
 *  Decode takes a file input, read12(inputFile) reads a binary value from the inputFile and returns as a integer store in readIndex variable
 *  readIndex is used to check if the string currently exists in the dictionary
 *  if so output the string at that locaton and then add the first letter of the dictionary string to the string variable, then place it in dictionary
 *  otherwise add the string variable's first character to the end of it, then add to the string variable to the dictionary
 *  then set string to the dictionary string at readIndex.
 * 
 * 
 */

void decode(FILE *inputFile, FILE *outputFile){

    // Variables
    unsigned char string[255];  // Character array for storing the string

    int readIndex = read12(inputFile);  // Integer from file
    int stringLength = 0;   // Length of string
    int i;  // For loop counter
    int dictStringLength;   // Length of string in dictionary

    // Grab the length of string stored at readIndex location
    dictStringLength = dict[readIndex][0];

    // Set string length equal to dictStringLength
    stringLength = dictStringLength;

    // Loop through output string at readIndex location
    for(i = 1; i <= dictStringLength; i++){

        fputc(dict[readIndex][i], outputFile);

        // Set string as the readIndex string in the dictionary
        string[i - 1] = dict[readIndex][i];

    }//for

    // While not at the end of file continue reading the inputFile
    while((readIndex = read12(inputFile)) != EOF){
        
        // Variable
        char temp[2];  // Character array for holding the temporary string

        // Break out of while if readIndex returns the padding index
        if(readIndex == 4095){
            break;
        }//if

        // Grab the length of the string at readIndex location
        dictStringLength = dict[readIndex][0];
        
        // If readIndex is less the entryCounter, then string is in dict
        if(readIndex < entryCounter){

            // Output string at readIndex location
            for(i = 1; i <= dictStringLength; i++){

                fputc(dict[readIndex][i], outputFile);

            }//for
           
            // Add the first letter of the dictionary string to string   
            string[stringLength] = dict[readIndex][1];

            // Increment stringLength by 1
            stringLength++;

            // Add string's length at a open location called entryCounter
            dict[entryCounter][0] = stringLength;
           
            // Add the string to entryCounter location
            for(i = 1; i <= stringLength; i++){

                dict[entryCounter][i] = string[i - 1];
                
            }//for

        }else{
            // Else string was not in dictionary

            // Add the first character of string to temp
            temp[0] = string[0];

            // Add first string of temp to the end of string
            string[stringLength] = temp[0];

            // Increment string's length by 1
            stringLength++;

            // Add string's length at entryCounter location
            dict[entryCounter][0] = stringLength;

            // Place string at location entryCounter, and then output the string to outputFile
            for(i = 1; i <= stringLength; i++){
               
                dict[entryCounter][i] = string[i - 1];
                fputc(dict[entryCounter][i], outputFile);
                
            }//for
            
            
        }//if else

        // Increment entryCounter by 1
        entryCounter++;

        // If entryCounter is greater than or equal to 4096, then reset entryCounter to 256
        if(entryCounter >= DICTSIZE){

            entryCounter = 256;

        }//if
        
        // Set dictStringLength to the value at readIndex location
        dictStringLength = dict[readIndex][0];

        // Set stringLength equal to dictStringLength
        stringLength = dictStringLength;

        // Set string to the dictionary string stored at readIndex location
        for(i = 1; i <= dictStringLength; i++){

            string[i - 1] = dict[readIndex][i];

        }//for

    }//while

} //decode

/* 
 * void initalizeDict()
 * 
 *  Fills the dictionary with ascii characters from index 0 to 255
 *  And sets the length of each index to 1
 * 
 */

void initalizeDict(){
    // Variables
    int rowIndex;   // For loop counter

    // Loop through dictionary filling each rowIndex location with ascii character and length
    for (rowIndex = 0; rowIndex < entryCounter; rowIndex++){
        
        dict[rowIndex][0] = 1;
        dict[rowIndex][1] = rowIndex;
    }

} //initalizeDict

int write12(FILE *outfil, int int12){

   static int number1 = -1, number2 = -1;
   unsigned char hi8, lo4hi4, lo8;
   unsigned long bignum;

   if (number1 == -1) /* no numbers waiting             */
   {
      number1 = int12; /* save the number for next time  */
      return (0);      /* actually wrote 0 bytes         */
   }

   if (int12 == -1)     /* flush the last number and put  */
      number2 = 0x0FFF; /* padding at end                 */
   else
      number2 = int12;

   bignum = number1 * 0x1000; /* move number1 12 bits left      */
   bignum = bignum + number2; /* put number2 in lower 12 bits   */

   hi8 = (unsigned char)(bignum / 0x10000);               /* bits 16-23 */
   lo4hi4 = (unsigned char)((bignum % 0x10000) / 0x0100); /* bits  8-15 */
   lo8 = (unsigned char)(bignum % 0x0100);                /* bits  0-7  */

   fwrite(&hi8, 1, 1, outfil); /* write the bytes one at a time  */
   fwrite(&lo4hi4, 1, 1, outfil);
   fwrite(&lo8, 1, 1, outfil);

   number1 = -1; /* no bytes waiting any more      */
   number2 = -1;

   return (3); /* wrote 3 bytes                  */
}

int read12(FILE *infil){

   static int number1 = -1, number2 = -1;
   unsigned char hi8, lo4hi4, lo8;
   int retval;

   if (number2 != -1)   /* there is a stored number from   */
   {                    /* last call to read12() so just   */
      retval = number2; /* return the number without doing */
      number2 = -1;     /* any reading                     */
   }
   else /* if there is no number stored    */
   {
      if (fread(&hi8, 1, 1, infil) != 1) /* read three bytes (2 12 bit nums)*/
         return (-1);
      if (fread(&lo4hi4, 1, 1, infil) != 1)
         return (-1);
      if (fread(&lo8, 1, 1, infil) != 1)
         return (-1);

      number1 = hi8 * 0x10;                /* move hi8 4 bits left            */
      number1 = number1 + (lo4hi4 / 0x10); /* add hi 4 bits of middle byte    */

      number2 = (lo4hi4 % 0x10) * 0x0100; /* move lo 4 bits of middle byte   */
                                          /* 8 bits to the left              */
      number2 = number2 + lo8;            /* add lo byte                     */

      retval = number1;
   }

   return (retval);
}


void flush12(FILE *outfil){

   write12(outfil, -1); /* -1 tells write12() to write    */

} /* the number in waiting          */

void strip_lzw_ext(char *fname){
   char *end = fname + strlen(fname);

   while (end > fname && *end != '.' && *end != '\\' && *end != '/')
   {
      --end;
   }
   if ((end > fname && *end == '.') &&
       (*(end - 1) != '\\' && *(end - 1) != '/'))
   {
      *end = '\0';
   }
}// strip_lzw_ext