#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>  // For random number
#include <time.h>
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

  // PIN INPUT. For now, commented to allow other code to run smoothly

/*  int PIN;

  do {
    printf("Enter PIN (hint 2471?)\n");
  scanf("%d", &PIN);
  } while (PIN != 2471);
  printf("Correct PIN!\n");
*/
  // More examples
  // a program that only prints even numbers between 0 and 10 (inclusive):

  int num = 0;
  while (num <= 10) {
    printf("%d\n", num);
    num += 2;
  }

  // Reverse digits
  // The Algorithm
  // Start with 0 and assign it to a variable x (say)
  // multiply x with 10 and add to it the remainder when x /10.
  // SO at first we get 0*10 + 12345/10 = 5
  // So we have 5. Now divide x by 10. this gives us 1234 (because C ignores .5 for integer division)
  //So we keep getting 4,3,2,1

  int numbers = 12345;
  int revNumber = 0;
  while (numbers) {
    revNumber = revNumber * 10 + numbers % 10;
    numbers /= 10;
  }
  printf("%d\n", revNumber);

  // Let's now generate a random number from 1 to 6 (a die throw). Let's keep tossing until it's a 6.

  srand(time(NULL));

  int dice = 0;
  int throw = 0;

  while (dice != 6) {
    dice = (rand() % 6) + 1;
    throw++;
    printf("Step %d: rolled %d\n", throw, dice);
  }

  printf("We have 6, in %d steps.\n", throw);


  // Sum Until Sentinel
  // A sensor is sending temperature readings. The program reads integers from the user one at a time. When the user enters -999 (the "sentinel" value, meaning "no more data"), the program stops and prints the total sum and the count of readings. The -999 itself should NOT be counted.

  float temp;
  float sum = 0;
  while (temp != -999) {
    printf("Enter the temperature.\n");
    scanf("%f", &temp);
    sum = sum + temp;
  }
  printf("Sum of temperature is %f", sum + 999);

  return 0;
}



