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

  //All data types

  int intg = 200;
  double db = 4.45;

  short int tiny = 5; // range -32,768 to 32,767
  unsigned int numb = 30;

  long int big = 3462746;
  long long int large = 4348758542365;
  unsigned long long int giant = 3462893462346823764;
  long double euler = 2.7182818285;

  printf("Ordinary integer %d\n", intg);
  printf("Double %lf\n", db);
  printf("Small value %hd\n", tiny);
  printf("A count %u, usually used for counting\n", numb);
  printf("A Big boss %ld\n", big);
  printf("A larger one %lld\n", large);
  printf("A gigantic one now %llu\n", giant);
  printf("Finally, a precise one %Lf\n", euler);

  // Check their sizes
  printf("The sizes are \n");
  printf("%zu, %zu, %zu, %zu, %zu, %zu, %zu, %zu\n", sizeof(intg), sizeof(db), sizeof(tiny), sizeof(numb), sizeof(big), sizeof(large), sizeof(giant), sizeof(euler));

  // Data Tape Conversion

  // The problem

  int x = 20;
  int y = 3;
  int div = x / y;
  printf("%d\n", div); // 6 but it should be 6.66...

  // Implicit conversion
  // automatically by the compiler

  float fl = 9;
  printf("%f\n", fl); //converted to 9.00000
  int z = 8.80;
  printf("%d \n", z); // converted to 8 from 8.80

  // Even this is a problem
  float dv = x / y;
  printf("%f\n", dv); //yet gives 6.00000

  // Explicit conversion

  float correctdv = (float) x / y;
  printf("%f\n", correctdv); // Now 6.666667
  printf("%.2f\n", correctdv); // with specific precision

  // Example

  int numSick = 20;
  int totPeople = 200;
  float ratio1 = numSick / totPeople;
  float ratio2 = (float) numSick / totPeople;
  printf("%f, %f\n", ratio1, ratio2);

  // Constants, unchangeable
  const int BIRTH_YEAR = 2001; // skipping int is not right
  const birth_month = 12;
  const DAY = 7; //better to write in uppercase

  printf("Born in %d.\n", BIRTH_YEAR);
  return 0;
}
