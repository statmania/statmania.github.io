#include <stdio.h>

int main(){
  //Int
  int area = 24;
  float height = 2.3;
  char jar = 'A';

  float volume = area * height;
  printf("The volume of the jar %c is %f\n", jar, volume);

  // ASCII for char
  char a = 65, b = 67;
  printf("The ASCII char is %c\n", a);

  //  Storing more than a character
  char c = 'Language';
  printf("The text is %c\n", c); //just e

  //Need string to store multiple characters (%s)
  char fullchar[] = "Language";
  printf("Now we should ge the whole %s\n", fullchar);


  // Double allows more precision than float (7 vs 15 digits)

  float len = 19.101255564;
  float wid = 2.672;
  float area1 = len * wid;
  double area2 = len * wid;
  printf("The area in float is %f and in double is %lf\n", area1, area2); // Still same output, more on this later

  // Scientific numbers
  float sciN = 10e2;
  double sciN2 = 34E3;
  printf("%f, %lf\n", sciN, sciN2);

  // Set Decimal precision

  float num1 = 4.5;
  double num2 = 5.6;
  printf("%f \n", num1);
  printf("%lf\n", num2);

  //Specify number of digits after decimal
  printf("The whole number is %f\n", num2);
  printf("The number up to first digit after decimal is %.1lf\n", num2);

  // Operator Size
  printf("The size of the area int is %zu\n", sizeof(area));
  printf("The size of the jar char is %zu\n", sizeof(jar));
  printf("The size of the float is %zu\n", sizeof(num1));
  printf("The size of the double is %zu\n", sizeof(num2));

  // Example of different data type
  int count = 20;
  float totweight = 65.23;
  float avgweight = totweight / count;
  printf("The avaerage weight is %f\n", avgweight);
  return 0;
}
