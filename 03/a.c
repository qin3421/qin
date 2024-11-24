#include <stdio.h>
#include <stdlib.h>


int add(int a, int b) {
    return a + b;
}

int main(int argc, char *argv[]) {

    if (argc != 3) {
        printf("Usage: %s <num1> <num2>\n", argv[0]);
        return 1;
    }
	
    int x = atoi(argv[1]);
    int y = atoi(argv[2]);
    
    int result = add(x, y);
    printf(" %d + %d =  %d\n", x, y, result);

    return 0;
}

