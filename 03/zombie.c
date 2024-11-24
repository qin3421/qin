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
	sleep(5);
        printf("Child process (PID: %d) is terminating...\n", getpid());
exit(0);
    } else {
        // 父进程
  	while(1){
		printf("I'm parent:%d, my child pid:%d\n", getpid(), pid);
		sleep(1);
	}
             exit(0);
    }
}

