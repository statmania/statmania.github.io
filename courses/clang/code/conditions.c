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

  if (temp < - 10){
    printf("The weather is extremely cold\n");
  } else if (temp <= 10) {
    printf("The weather is cold\n");
  } else if (temp <= 30) {
    printf("The weather is not that cold\n");
  }
  else {
    printf("Extremely Hot!\n");
  }


  return 0;
}
