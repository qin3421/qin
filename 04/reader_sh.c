#include <stdio.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <string.h>

#define SHM_SIZE 1024  // 定义共享内存大小

int main() {
    key_t key;
    int shm_id;
    char *shm_ptr;

    // 1. 生成一个唯一的key（与写入进程相同）
    key = ftok("shmfile", 65);

    // 2. 获取现有的共享内存段
    shm_id = shmget(key, SHM_SIZE, 0666);
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

    // 4. 读取共享内存中的数据
    printf("Data read from shared memory: %s\n", shm_ptr);

    // 5. 分离共享内存段
    shmdt(shm_ptr);

    // 6. 删除共享内存段
    shmctl(shm_id, IPC_RMID, NULL);

    return 0;
}
