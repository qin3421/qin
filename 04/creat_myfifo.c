#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
int main() {
    const char *fifo_path = "./mypipe";

    // 创建有名管道
    if (mkfifo(fifo_path, 0666) == -1) {
        perror("mkfifo failed");
        exit(EXIT_FAILURE);
    }
    printf("Named pipe created at %s\n", fifo_path);
    return 0;
}
