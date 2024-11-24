#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
int main() {
    int x = 100;

    // 打印父进程中的变量 x 的值
    printf("Parent process: x = %d(pid:%d)\n", x, getpid());

    // 调用 fork() 创建子进程
    int pid = fork();

    if (pid < 0) {
        // fork() 失败
        fprintf(stderr, "fork failed\n");
        exit(1);
    } else if (pid == 0) {
        // 子进程
        printf("Child process: x = %d(pid:%d)\n", x, getpid());
	
	//code
	
	
    } else {
        // 父进程
	wait(NULL);
        printf("Parent process: x = %d(pid:%d)\n", x, getpid());

	//code
	


    }
    
    
    printf("End x = %d(pid:%d)\n", x, getpid());

    return 0;
}

