#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>

int main() {
    const char *fifo_path = "./mypipe";
    int fd;
    char buffer[128];

    // 打开管道以读取
    fd = open(fifo_path, O_RDONLY);
    if (fd == -1) {
        perror("open failed");
        exit(EXIT_FAILURE);
    }
// 读取数据
    read(fd, buffer, sizeof(buffer));
    close(fd);  // 关闭管道

    printf("Data read from the pipe: %s\n", buffer);
    return 0;
}

