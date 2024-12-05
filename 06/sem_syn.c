#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>

sem_t semaphore;

void* worker(void* arg) {
    sem_wait(&semaphore); // 等待信号量
    printf("进入临界区：%s\n", (char*)arg);
    // 临界区代码
    sem_post(&semaphore); // 释放信号量
    return NULL;
}

int main() {
    pthread_t t1, t2;
    sem_init(&semaphore, 0, 1); // 初始化信号量，值为1

    pthread_create(&t1, NULL, worker, "线程1");
    pthread_create(&t2, NULL, worker, "线程2");

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    sem_destroy(&semaphore); // 销毁信号量
    return 0;
}
