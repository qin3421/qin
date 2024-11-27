#include <stdio.h>
#include <sys/ipc.h>

int main() {
    key_t key;
    
    // 使用 ftok 函数生成 key
    key = ftok("shmfile", 65);
    if (key == -1) {
        perror("ftok failed");
        return 1;
    }

    printf("Generated key: %d\n", key);
    return 0;
}

