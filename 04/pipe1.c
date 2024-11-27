#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>
#define BUFFER_SIZE 20

int main() {
    int pipefd[2];
    pid_t pid;
    char buffer[BUFFER_SIZE];
    int countdown = 5;  // 倒计时的秒数
    // 创建管道
    if (pipe(pipefd) == -1) {
        perror("pipe failed");
        return 1;
    }
    // 创建子进程
    pid = fork();
    if (pid < 0) {
        perror("fork failed");
        return 1;
    }
    if (pid == 0) {  // 子进程
        close(pipefd[1]);  // 关闭写端

        printf("子进程：准备读取数据...\n");

        // 子进程倒计时等待父进程写入数据
        while (countdown > 0) {
            printf("子进程：等待父进程写入数据，剩余 %d 秒...\n", countdown);
            sleep(1);  // 等待1秒，模拟倒计时
            countdown--;
	    }
        // 读取数据，会阻塞直到有数据可读
        read(pipefd[0], buffer, BUFFER_SIZE);
        printf("子进程：读取到数据: %s\n", buffer);
        close(pipefd[0]);

    } else {  // 父进程
        close(pipefd[0]);  // 关闭读端
        sleep(5);  // 模拟父进程的其他操作，子进程会在这期间被阻塞等待
        printf("父进程：准备写入数据...\n");
        write(pipefd[1], "Hello, child!", 14);  // 向管道写入数据
        close(pipefd[1]);
        // 等待子进程结束
        wait(NULL);
    }

    return 0;
}
