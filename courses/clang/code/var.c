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
  // Multiple variables
  int a = 2, b = 6;
  // Sum
  printf("The sum is %d \n", a + b);

  // Assign the same value to multiple variables
  int p, q, r;
  p = q = r = 30;
  printf("The variables have the same value, and that's %d \n", p);
  // Sum them
  printf("Their sum is %d \n", p + q +r);

  //Identifier
  // Good
  int age = 30;
  printf("My age is %d \n", age);
  // Fine, but not recognizabe
  int x2 = 40;

  // A personal profile
  int id = 16;
  int weight = 76;
  int bp = 121;
  float fee = 1000.20;
  char grade = 'B';

  printf("The student having the id %d\n has weight %d, \n BP %d, \n fee %f, \n and \n grade %c \n", id, weight, bp, fee, grade);

  // Calculate area
  int length = 40;
  float width = 20;
  float area;
  area = length*width;
  printf("The area is %f\n", area);

  // Assign multiple characters together

  char d = 65, e = 'F'; //65 for A
  printf("The assigned values are %c and %c \n", d, e);


  // Storing multiple character

  char myText = 'Hello';
  printf("The character is %c \n", myText); // last character (o) is returned.


  return 0;
}
