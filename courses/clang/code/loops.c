#include <stdio.h>
#include <stdbool.h>
int main(){
  int i = 0;

  while (i < 5) {
    printf("The value is %d\n", i);
    i++;
  }

  // Countdown example

  int count = 3;
  while (count > 0){
    printf("%d\n", count);
    count--;
  }
  printf("Start!\n");

  // If the the condition is initially false, the loop may not start.

  // DO/While Loop; executes at least once even if the condition is false.

  int x = 6;
  do {
    printf("%d\n", i);
    x++;
  } while (x < 5);

  // PIN INPUT

  int PIN;

  do {
    printf("Enter PIN\n");
    scanf("%d", &PIN);
  } while (PIN != 2471);
  printf("Correct PIN!\n");
  return 0;
}



