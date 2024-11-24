#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main() {
    pid_t pid = fork(); // 创建一个子进程

    if (pid < 0) {
        perror("fork failed");
        exit(1);
    } else if (pid == 0) {
        // 子进程
	while(1){
		printf("I'm child:%d, my parent pid:%d\n", getpid(),getppid());
		sleep(1);
	}
        exit(0);
    } else {
        // 父进程
	sleep(5);
        printf("Parent process (PID: %d) is terminating...\n", getpid());
        exit(0); // 父进程提前终止
    }
}

