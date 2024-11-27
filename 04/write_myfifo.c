#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

int main() {
    const char *fifo_path = "./mypipe"; // 命名管道的路径
    int fd;

    // 打开管道以写入
    fd = open(fifo_path, O_WRONLY);
    if (fd == -1) {
        perror("Failed to open pipe");
        exit(EXIT_FAILURE);
    }

    // 要写入管道的消息
    const char *message = "Hello from writer!";
    if (write(fd, message, strlen(message) + 1) == -1) {
        perror("Failed to write to pipe");
        close(fd);
        exit(EXIT_FAILURE);
    }

    // 关闭管道
    close(fd);
    printf("Data written to the pipe: %s\n", message);

    return 0;
}

