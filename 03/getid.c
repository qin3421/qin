#include <stdio.h>
#include <unistd.h> 

int main() {
    pid_t pid = getpid();   // 获取当前进程的 PID
    pid_t ppid = getppid(); // 获取父进程的 PID

    printf("Current Process ID (PID): %d\n", pid);
    printf("Parent Process ID (PPID): %d\n", ppid);

    return 0;
}

