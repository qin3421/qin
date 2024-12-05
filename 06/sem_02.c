#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

typedef struct {
    unsigned int value;
    pthread_mutex_t mutex;
    pthread_cond_t cond;
} sem_t;

int sem_init(sem_t *sem, int pshared, unsigned int value) {
    if (pshared != 0) {
        return -1;  // 不支持跨进程信号量
    }
    sem->value = value;
    pthread_mutex_init(&sem->mutex, NULL);
    pthread_cond_init(&sem->cond, NULL);
    return 0;
}

int sem_wait(sem_t *sem) {
    pthread_mutex_lock(&sem->mutex);
    while (sem->value == 0) {
        pthread_cond_wait(&sem->cond, &sem->mutex);
    }
    sem->value--;
    pthread_mutex_unlock(&sem->mutex);
    return 0;
}

int sem_post(sem_t *sem) {
    pthread_mutex_lock(&sem->mutex);
    sem->value++;
    if (sem->value > 0) {
        pthread_cond_signal(&sem->cond);
    }
    pthread_mutex_unlock(&sem->mutex);
    return 0;
}

void sem_destroy(sem_t *sem) {
    pthread_mutex_destroy(&sem->mutex);
    pthread_cond_destroy(&sem->cond);
}

void* thread_func(void* arg) {
    sem_t* sem = (sem_t*)arg;
    sem_wait(sem);  // P操作
    printf("Thread %ld entered critical section.\n", pthread_self());
    sleep(1);       // 模拟临界区工作
    printf("Thread %ld leaving critical section.\n", pthread_self());
    sem_post(sem);  // V操作
    return NULL;
}

int main() {
    pthread_t threads[5];
    sem_t sem;
    
    // 初始化信号量，初始值为2
    sem_init(&sem, 0, 2);
    
    // 创建5个线程
    for (int i = 0; i < 5; i++) {
        pthread_create(&threads[i], NULL, thread_func, &sem);
    }
    
    // 等待所有线程完成
    for (int i = 0; i < 5; i++) {
        pthread_join(threads[i], NULL);
    }
    
    // 销毁信号量
    sem_destroy(&sem);
    
    return 0;
}
