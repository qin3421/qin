#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>

sem_t semaphore;

void* thread_func(void* arg) {
    sem_wait(&semaphore);  // P操作
    printf("线程 %ld 进入临界区\n", (long)arg);
    sleep(1);  // 模拟临界区工作
    printf("线程 %ld 离开临界区\n", (long)arg);
    sem_post(&semaphore);  // V操作
    return NULL;
}

int main() {
    pthread_t threads[5];
    
    // 初始化信号量，初始值为2（表示有两个资源可以同时访问）
    sem_init(&semaphore, 0, 2);
    
    // 创建5个线程
    for (long i = 0; i < 5; i++) {
        pthread_create(&threads[i], NULL, thread_func, (void*)i);
    }
    
    // 等待所有线程完成
    for (int i = 0; i < 5; i++) {
        pthread_join(threads[i], NULL);
    }
    
    // 销毁信号量
    sem_destroy(&semaphore);
    
    return 0;
}
