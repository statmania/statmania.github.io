#include <stdio.h>
#include <stdbool.h> // For boolean operators

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
  //or write, actually ++x and x++ serve different purposes.
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

  //Logical

  int isSignedin = 1;
  int isAdmin = 0;

  printf("Normal user: %d\n", isSignedin && !isAdmin);
  printf("Access granted: %d\n", isSignedin || isAdmin);
  printf("Logged out: %d\n", !isSignedin);

  // Order of Operations
  /*
   () - Parentheses
   *, /, % - Multiplication, Division, Modulus
   + , - - Addition, Subtraction
   >, <, >=, <= - Comparison
   ==, != - Equality
   && - Logical AND
   || - Logical OR
   = - Assignment
   */

  int res1 = 15 - 5 + 8; // 18
  int res2 = 15 - (5 + 8); // 2
  printf("The results are %d and %d, respectively.\n", res1, res2);

  // Boolean operators
  // Needs #include <stdbool.h>

  // Declare boolean
  bool isStatistician = true;
  bool isGoodwithComp = true;

  printf("A statistician: %d\n", isStatistician);
  printf("Good with computer: %d\n", isGoodwithComp);

  // COmpare with bool

  printf("Is 10.9 greater than 10.10: %d\n", 10.9 > 10.10);
  printf("100 equals 100.1: %d\n", 100 == 100.1);

  // Storing result of comparison

  bool isGreater = res1 > res2;
  printf("Stored result is: %d\n", isGreater);

  int liftCapacity = 450; //kg
  int currentWeight = 451;
  printf("Overloaded: %d\n", liftCapacity < currentWeight);

  // Using if with bool

  if (currentWeight <= liftCapacity){
    printf("It's safe to go.\n");
  } else {
    printf("Somebody has to get down.\n");
  }

  return 0;
}
