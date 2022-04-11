/* Encoding and Decoding program
 * Created by: Austin Basset
 * Class: Seng 265
 * Year: 2019
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

/* 
 * void encode(char encodeMessage)
 *
 * Takes in a String as a parameter
 * Then encodes the string with a char and number
 * The char represents the letter 
 * The number represents the number of times the letter was repeated.
 * 
*/

void encode(char encodeMessage[])
{

    // Char variables
    char encodedMessage[22] = "";           // String for encoded message.
    char currentCharacter, characterHolder; // Character place holders.

    // Integer variables
    int numberOfCharacters = 1; // Character repeated tracker.
    int characterIndex = 0;     // Location in the string.
    int printEncode;    // Integer for print encoded message.

    // Set currentCharacter and characterHolder to first character in encodeMessage string.
    currentCharacter = encodeMessage[0];
    characterHolder = currentCharacter;

    while (currentCharacter != '\0')
    {
        // Char buffer for concatinating the strings.
        char messageBuffer[20] = "";

        // If to check that each letter is capitalized and if each letter is either A, C, G, or T.
        if (!isupper(currentCharacter) || (currentCharacter != 'A' && currentCharacter != 'C' && currentCharacter != 'G' && currentCharacter != 'T') || isdigit(currentCharacter))
        {
            // Checking if the white space is at the end of string, if so ignore it.
            if (encodeMessage[characterIndex + 1] == '\0' && isspace(currentCharacter))
            {

                break;

            }
            else
            {

                printf("Error:String could not be encoded\n");
                exit(5);


            } //if else

        } //if

        // Set currentCharacter to the next character in the string.
        characterIndex++;
        currentCharacter = encodeMessage[characterIndex];

        // Check if characterHolder is different from currentCharacter.
        if (characterHolder != currentCharacter)
        {
            // If so, add the character and the number of times it was repeated to an encodedMessage string.
            sprintf(messageBuffer, "%c%i", characterHolder, numberOfCharacters);
            strcat(encodedMessage, messageBuffer);

            // Set characterHolder to the new character and reset the numberOfCharacter counter.
            characterHolder = currentCharacter;
            numberOfCharacters = 1;

        }
        else
        {
            // Otherwise increment numberOfCharacters by 1.
            numberOfCharacters++;

        } //if else
    } //while

    // Print out the Encoded Message.
    printf("Encoded Message: ");
    for (printEncode = 0; printEncode < 22; printEncode++)
    {
        // Checking it at end of message, then break the for loop
        if(encodedMessage[printEncode] == '\0' || isspace(encodedMessage[printEncode])){
            
            break;
        
        }

        printf("%c", encodedMessage[printEncode]);

    } //for
    printf("\n");

    exit(0);
} //encode



/* 
 * void decode(char decodeMessage)
 *
 * Takes in a String as a parameter
 * Then decodes the string from a character number pair to a sequence string
 * Of the character repeating the number of times.
 * The number represents the number of times the letter was repeated.
 * 
*/

void decode(char decodeMessage[])
{

    // Char variables.
    char decodedMessage[255] = "";             // String for the fully decoded message.
    char currentCharacter, numberToCharacter; // Char holders for current letter and number to be converted to a integer variable type.

    // Integer variables.
    int numberOfRepitions;  // Number of times to repeat the letter.
    int numberIndex = 1;    // Index to find the numbers.
    int characterIndex = 0; // Index to find the letters.
    int printDecode;    // Integer for printint decoded message.
    int repitionLoop;   // Integer for repition of character loop.

    // Set currentCharacter to first Letter of the String.
    currentCharacter = decodeMessage[characterIndex];

    while (currentCharacter != '\0')
    {

        char decodeBuffer[50] = ""; // String for concatinating the message together.

        // Get the number from the string and convert it to a integer.
        numberToCharacter = decodeMessage[numberIndex];
        numberOfRepitions = atoi(&numberToCharacter);

        // If to check that each letter is capitalized and if each letter is either A, C, G, or T.
        if (!isupper(currentCharacter) || (currentCharacter != 'A' && currentCharacter != 'C' && currentCharacter != 'G' && currentCharacter != 'T') || !isdigit(numberToCharacter))
        {
            // Checking if the white space is at the end of string, if so ignore it.
            if (decodeMessage[characterIndex + 1] == '\0' && isspace(currentCharacter))
            {

                break;

            }
            else
            {

                printf("Error:String could not be decoded\n");
                exit(5);

            } //if else
        }     //if

        // Add the currentCharacter to decodeBuffer numberOfRepition times.
        for (repitionLoop = 0; repitionLoop < numberOfRepitions; repitionLoop++)
        {

            decodeBuffer[repitionLoop] = currentCharacter;

        } //for

        // Concatinate the stings together.
        strcat(decodedMessage, decodeBuffer);

        // Increment both Indexs to find the next character number pair.
        characterIndex = characterIndex + 2;
        numberIndex = numberIndex + 2;
        currentCharacter = decodeMessage[characterIndex];

    } //while

    // Print out the decoded message.
    printf("Decoded Message: ");
    for (printDecode = 0; printDecode < 180; printDecode++)
    {
        // Checking it at end of message, then break the for loop
        if(decodedMessage[printDecode] == '\0' || isspace(decodedMessage[printDecode])){
            break;
        }//if

        printf("%c", decodedMessage[printDecode]);

    } //for
    printf("\n");

    exit(0);
} //decode



int main(int args, char *inputData[])
{
    // Char variables.
    char *fileName = inputData[1];          // File name variable from command line.
    char *encodeOrDecode = inputData[2];    // Decision maker variable for encoding or decoding.
    char fileMessage[41];                   // String for text from file that was input.
    char fileExtensionVerifier[5] = ".txt"; // Variable for verifying file extension.
    char *isValidFile;                      // Place holder for checking if file inputted is vaild.

    int messageLoop;    // Integer used in for loop.

    // Check if fileName is of type .txt.
    isValidFile = strstr(fileName, fileExtensionVerifier);

    // File pointer.
    FILE *fileOperator;

    // If file input was invalid print error and exit program.
    if (isValidFile == NULL)
    {

        printf("Error: No input file specified!\n");
        exit(1);

    } //if(isValidFile)

    // Checking if encodeOrDecode was not provided an argument or if they weren't of the type e, d, [e] or [d].
    if (encodeOrDecode == NULL)
    {

        printf("Invaild Usage,expected:RLE{filename}[e|d]\n");
        exit(4);

    }
    else if ((strcmp(encodeOrDecode, "e") != 0 && strcmp(encodeOrDecode, "d") != 0) && (strcmp(encodeOrDecode, "[e]") != 0 && strcmp(encodeOrDecode, "[d]") != 0))
    {

        printf("Invaild Usage,expected:RLE{filename}[e|d]\n");
        exit(4);

    } //if else

    // Open inputted file and read it.
    fileOperator = fopen(fileName, "r");

    // Check if fileOperator was able to open file.
    if (fileOperator == NULL)
    {

        printf("Read error: file not found or cannot be read\n");
        exit(2);

    } //if(fileOperator == NULL)

    // Put contents of file into a string array.
    fgets(fileMessage, 41, fileOperator);

    // Close inputted file.
    fclose(fileOperator);
    
    // Checking the location of whitespace.
    for(messageLoop = 0; messageLoop < 41; messageLoop++){
        
        // Checking if the white space is at the end of string, if so ignore it.
        if (fileMessage[messageLoop + 1] == '\0' && isspace(fileMessage[messageLoop]))
        {

            break;

        }
        else if(isspace(fileMessage[messageLoop]))
        {

            printf("Error:Invalid format\n");
            exit(3);

        } //if else

    }//for

    // Check weither to encode fileMessage or decode fileMessage.
    if (strcmp(encodeOrDecode, "e") == 0)
    {

        encode(fileMessage);

    }
    else
    {

        decode(fileMessage);

    } //if else

    return 0;
} //main