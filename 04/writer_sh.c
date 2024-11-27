#include <stdio.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <string.h>

#define SHM_SIZE 1024  // 定义共享内存大小

int main() {
    key_t key;
    int shm_id;
    char *shm_ptr;

    // 1. 生成一个唯一的key
    key = ftok("shmfile", 65);  // 使用文件路径生成key，确保唯一性

    // 2. 创建共享内存段
    shm_id = shmget(key, SHM_SIZE, 0666|IPC_CREAT);
    if (shm_id == -1) {
        perror("shmget failed");
        return 1;
    }

    // 3. 将共享内存段附加到进程的地址空间
    shm_ptr = (char*) shmat(shm_id, NULL, 0);
    if (shm_ptr == (char *) -1) {
        perror("shmat failed");
        return 1;
    }

    // 4. 向共享内存写入数据
    printf("Enter data to write into shared memory: ");
    fgets(shm_ptr, SHM_SIZE, stdin);

    // 5. 分离共享内存段
    shmdt(shm_ptr);

    return 0;
}
