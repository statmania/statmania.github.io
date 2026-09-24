#include <stdio.h>

int main(){
  // Basic operations
  int x = 35;
  int y = 20;
  int sum = x + y;
  int diff = x - y;
  int prod = x * y;
  float div = (float) x / y;

  printf("The sum is %d\n", sum);
  printf("The division is %f\n", div);

    // Modulus
  printf("The modulus is %d\n", x % y);
  // Increment
  printf("The incremented value is %d\n", ++x);
  // Decrement
  printf("The decremented value is %d\n", x--);
  //or write, actually ++x and x++ server different purposes.
  printf("The decremented value is %d\n", --x);

  // Example
  // Counting Students

  int numStd = 20;
  // 1 new
  numStd++;
  //another comes
  numStd++;
  printf("Now there are %d students.\n", numStd);
  //one goes
  numStd--;
  printf("Now there are %d students.\n", numStd);

  //Assignment operators
  // = is already familiar to us

  //+=
  int p = 4;
  p = p + 4;
  printf("New value is %d \n", p);
  // can also b written as
  p += 3;
  p -= 3;
  printf("New value is back to %d \n", p);

  p *= 3;
  printf("New value is after multiplications is %d \n", p);

  //Division
  p /= 4;
  printf("New value is after division is %d \n", p);

  //Modulus
  p %= 5;
  printf("Modulus is %d \n", p);

  //Comparison

  // we use x and y assigned before.

  printf("%d\n", x > y); //1 if true
  printf("%d\n", x != y);
  printf("%d\n", x == y);
  printf("%d\n", x < y);
  printf("%d\n", x <= y);
  printf("%d\n", x >= y);

  // Real-world example

  int score = 60;
  printf("Has the students passed? Answer is %d\n", score >= 60);
  return 0;
}
