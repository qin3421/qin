#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>
#define BUFFER_SIZE 1024  // 定义缓冲区大小

int main() {
    int pipe_fd[2];  // 用于存储管道的文件描述符
    pid_t pid;
    char buffer[BUFFER_SIZE];

    // 创建管道
    if (pipe(pipe_fd) == -1) {
        perror("pipe failed");
        exit(1);
    }

    // 创建子进程
    pid = fork();
    if (pid < 0) {
        // fork失败，退出
        perror("fork failed");
        exit(1);
    }

    if (pid == 0) {

        // 子进程：从管道中读取数据
        close(pipe_fd[1]);  // 关闭写端

        // 从管道读取数据
        int n = read(pipe_fd[0], buffer, BUFFER_SIZE);
        if (n == -1) {
            perror("read failed");
            exit(1);
        }

        printf("Child process received: %s\n", buffer);
        close(pipe_fd[0]);  // 关闭读端
    } else {
        // 父进程：向管道写入数据
        close(pipe_fd[0]);  // 关闭读端

        // 写数据到管道
        const char *message = "Hello I'm parent!";
        if (write(pipe_fd[1], message, strlen(message) + 1) == -1) {
            perror("write failed");
            exit(1);
        }

        printf("Parent process sent: %s\n", message);
        close(pipe_fd[1]);  // 关闭写端
	wait(NULL);
    }

    return 0;
}

