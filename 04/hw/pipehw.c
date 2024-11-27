#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>


int main() {
    pid_t pid;



    // 创建子进程
    pid = fork();
    if (pid < 0) {
        // fork失败，退出
        perror("fork failed");
        exit(1);
    }

    if (pid == 0) {

        // 子进程

	printf("hello ");

    } else {
        // 父进程
	
	printf("world!\n");	

    }

    return 0;
}

