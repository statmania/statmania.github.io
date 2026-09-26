#include <stdio.h>
#include <stdbool.h>

int main(){
  if (20 > 10){
    printf("20 is greater than 10.\n");
  }

  // Test variables

  int x = 50;
  int y = 30;

  if (x > y){
    printf("x is greater than y\n");
  }

  // Using boolean variables

  bool isxGreater = x > y; //must use <stdbool.h> header
  if (isxGreater){
    printf("x is greater than y\n");
  }

  // ELSE
  // Lets change the value of x to make it smaller

  x -= 30;
  bool isGreater = x > y;

  if (isGreater){
    printf("x is greater than y\n");
  } else {
    printf("x is less than y\n");
  }

  int passMark = 60;
  int obtainedMark = 70;
  bool isPassed = obtainedMark >= passMark;

  if (isPassed){
    printf("Passed!\n");
  } else {
    printf("Failed!\n");
  }

  // ELSE IF

  int grade = 72;

  if (grade >= 80) {
    printf("The grade is A+\n");
  } else if (grade >= 70){
    printf("The grade is A\n");
  }

  //Another Example

  int temp = 43;

  if (temp < -10){
    printf("The weather is extremely cold\n");
  } else if (temp <= 10) {
    printf("The weather is cold\n");
  } else if (temp <= 30) {
    printf("The weather is not that cold\n");
  }
  else {
    printf("Extremely Hot!\n");
  }

  // Short hand

  (temp < 0) ? printf("The temperature is below freezing level.\n") : printf("The temperature is above freezing level.\n");

  // Let's reassign x and y. Already declared.

  x = 50;
  y = 40;

  if (x > 25) {
    printf("x is greater than 25. \n");

    //Nested
    if (y > 20) {
      printf("y is greater than 20.\n");
    }
  }

  // Real-world Nested if example

  int isMember = 1;
  double purchaseAmount = 1250.00;

  //Check if premium member
  if (isMember == 1){
    printf("Membership verified!\n");

    // Check amount of purchase with a nested if
    if (purchaseAmount > 1000.0){
      printf("You're eligible for a 20%% discount!\n");
    } else {
      printf("You're eligible for a 10%% discount.\n");
    }
  } else {
    // Not a member
    printf("Standard customer: No discount at this time. \n");
  }


  // ATM Pin and amount check

  int pin = 5103;
  int balance = 50000;

  if (pin == 5103) {
    printf("Thank you! You're logged in!\n");

    // Nested if to verify balance
    if (balance >= 40000) {
      printf("And you have sufficient balance.\n");
    } else {
      printf("Sorry! Your balance is too low!\n");
    }
  } else {
    printf("Your PIN is not correct \n");
  }

  // Logical operators with conditions

  // Redo the previous one with && (both conditions must be true)

  if (pin == 5103 && balance >= 40000) {
    printf("You're ready to withdraw money!\n");
  }

  // OR (||)
  // Use isMember and purchaseAmount variables from before

  if (isMember == 1 || purchaseAmount >=1000);
  printf("You are eligible for a discount. \n");

  // NOT (!)
  if (isMember != 1 || purchaseAmount < 1000);
  printf("You are not eligible for a discount. \n");

  // Using bool again
  int departmentalCustomer = 0;

  if (departmentalCustomer || (isMember == 1 && purchaseAmount >=1000)){
      printf("You are eligible for a discount. \n");
  } else {
    printf("Standard customer: No discount at this time. \n");
  }

  // Find odd/even numbers

  int selectedNumber = 10;
  if (selectedNumber %2 == 0){
    printf("The number %d is even.\n", selectedNumber);
  } else {
    printf("It's an odd number.\n");
  }

  return 0;
}
