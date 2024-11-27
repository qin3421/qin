#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <string.h>
#include <sys/wait.h>
#define SHM_SIZE 1024  // 定义共享内存大小

int main(int argc, char *argv[])
{
    key_t key;
    int shm_id;
    char *shm_ptr;

    // 1. 生成一个唯一的key
    key = ftok("shmfile", 65);  // 使用文件路径生成key，确保唯一性

    // 2. 创建共享内存段
    shm_id = shmget(key, SHM_SIZE, 0666 | IPC_CREAT);
    if (shm_id == -1) {
        perror("shmget failed");
        return 1;
    }

    // 3. 将共享内存段附加到进程的地址空间
    shm_ptr = (char*) shmat(shm_id, NULL, 0);
    if (shm_ptr == (char*) -1) {
        perror("shmat failed");
        return 1;
    }

    int rc = fork();
    if (rc < 0) {
        // fork failed; exit
        fprintf(stderr, "fork failed\n");
        exit(1);
    } else if (rc == 0) {
        // 子进程：向共享内存写入数据
        printf("Enter data to write into shared memory in child process(pid:%d) : ", getpid());
        fgets(shm_ptr, SHM_SIZE, stdin);
        shmdt(shm_ptr);  // 分离共享内存
    } else {
        // 父进程：读取共享内存中的数据
        
	wait(NULL);    
	printf("Data read from shared memory in parent process(pid:%d): %s\n",getpid(), shm_ptr);
        shmdt(shm_ptr);  // 分离共享内存

        // 删除共享内存段
        shmctl(shm_id, IPC_RMID, NULL);
    }

    return 0;
}

