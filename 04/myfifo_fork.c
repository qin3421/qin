#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <sys/stat.h>  // 包含 mkfifo 函数的声明
#include <sys/types.h>
#include <sys/wait.h>

#define FIFO_PATH "./mypipe" // 命名管道的路径

int main() {
    // 创建命名管道（FIFO），如果已存在则不创建
    if (mkfifo(FIFO_PATH, 0666) == -1) {
        perror("mkfifo failed");
        exit(EXIT_FAILURE);
    }

    pid_t pid = fork(); // 创建子进程
    if (pid < 0) {
        perror("fork failed");
        exit(EXIT_FAILURE);
    }

    if (pid == 0) {
        // 子进程：从管道读取数据
        int fd = open(FIFO_PATH, O_RDONLY); // 以只读模式打开管道
        if (fd == -1) {
            perror("Child: open failed");
            exit(EXIT_FAILURE);
        }

        char buffer[256];
        ssize_t bytes_read = read(fd, buffer, sizeof(buffer) - 1); // 从管道读取数据
        if (bytes_read == -1) {
            perror("Child: read failed");
            close(fd);
            exit(EXIT_FAILURE);
        }

        buffer[bytes_read] = '\0'; // 添加字符串结束符
        printf("Child process received: %s\n", buffer);

        close(fd); // 关闭管道
        exit(EXIT_SUCCESS);
    } else {
        // 父进程：向管道写入数据
        int fd = open(FIFO_PATH, O_WRONLY); // 以写模式打开管道
        if (fd == -1) {
            perror("Parent: open failed");
            exit(EXIT_FAILURE);
        }

        const char *message = "Hello from parent!";
        if (write(fd, message, strlen(message) + 1) == -1) { // 写入数据到管道
            perror("Parent: write failed");
            close(fd);
            exit(EXIT_FAILURE);
        }

        printf("Parent process sent: %s\n", message);

        close(fd); // 关闭管道
        wait(NULL); // 等待子进程结束

        // 删除命名管道
        unlink(FIFO_PATH);

        exit(EXIT_SUCCESS);
    }
}

