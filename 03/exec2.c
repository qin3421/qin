#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    pid_t pid = fork();  // 创建一个子进程

    if (pid == -1) {
        // fork 出错
        perror("fork failed");
        return 1;
    }

    if (pid == 0) {
        // 子进程执行
        printf("Child process is executing ls -l\n");
        
        // 使用 execlp 执行 "ls -l" 命令
        execl("/bin/ls", "ls", "-l", NULL);

        // 如果 execlp 执行失败，打印错误信息
        perror("execlp failed");
        return 1;  // 如果 exec 执行失败，返回 1
    } else {
        // 父进程执行
        printf("Parent process is waiting for the child to finish...\n");

        // 等待子进程结束
        wait(NULL);
        printf("Child process finished.\n");
    }

    return 0;
}

