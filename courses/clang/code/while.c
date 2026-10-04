#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define MAX_ROLLS 100

int main(void) {
  srand(time(NULL));

  int rolls[MAX_ROLLS];

  // Roll exactly MAX_ROLLS times, no stopping condition
  for (int i = 0; i < MAX_ROLLS; i++) {
    rolls[i] = (rand() % 6) + 1;
  }

  // For each face 1..6, print the toss numbers where it appeared
  for (int face = 1; face <= 6; face++) {
    printf("%d appears at toss:", face);
    for (int step = 0; step < MAX_ROLLS; step++) {
      if (rolls[step] == face) {
        printf(" %d", step + 1);
      }
    }
    printf("\n");
  }

  return 0;
}
