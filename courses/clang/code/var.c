#include <stdio.h>

int main(){
  printf("Hello \n");
  int myNum = 15;
  float myFloat = 4.32;
  char myChar = 'D'; // "D" or "Dhaka" give warnings
  /*var.c:7: warning: assignment makes integer from pointer without a cast
   * var.c:7: warning: cast between pointer and integer of different size
   */
  // give errors printf(myNum);
  printf("%d \n", myNum);
  printf("%f \n", myFloat);
  printf("%c \n", myChar);

  // Combining text and variable
  printf("The chosen number is %d", myNum);
  // Text, letter, and number
  printf("The number is %d and the letter is %c \n", myNum, myChar);
  //   print without storing
  printf("The assigned number is %d \n", 15);
  printf("The character is %c \n", 'C');
  // Change variable
  myNum = 20; //new value
  printf("The new value is %d \n", myNum);
  // New name to old var
  int neovar = myNum;
  printf("The new variable is %d, copied from the older one \n", neovar);

  // Declare with no assignment
  int barevar;
  barevar = myNum;
  printf("This varibale (barevar) has a value now and %d is the value \n", myNum);

  // Add variables
  int x = 10;
  int y = 20;
  int sum = x + y;
  printf("The sum is %d \n", sum);

  //Update variable
  int z = 5;
  z = z + 20;
  printf("The new value is %d \n", z);
  return 0;
}
