#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>

#define BUFFER_SIZE 5  // 缓冲区大小

// 缓冲区
int buffer[BUFFER_SIZE];
int in = 0;  // 生产者放入数据的位置
int out = 0; // 消费者取出数据的位置

// 定义信号量
sem_t empty;  // 空槽信号量，表示缓冲区的空位置
sem_t full;   // 满槽信号量，表示缓冲区的满位置
pthread_mutex_t mutex; // 互斥锁，保护缓冲区的访问

// 生产者线程函数（学生需要完成）
void *producer(void *arg) {
    int item;
    while (1) {
        item = rand() % 100;  // 生成一个随机数据
        sem_wait(&empty);  // P操作，等待空槽信号量
        pthread_mutex_lock(&mutex);  // 进入临界区

        // 完成生产过程，将数据放入缓冲区
        buffer[in] = item;
        printf("Produced: %d at index %d\n", item, in);
        in = (in + 1) % BUFFER_SIZE;

        pthread_mutex_unlock(&mutex);  // 离开临界区
        sem_post(&full);  // V操作，释放满槽信号量

        sleep(1);  // 模拟生产的时间
    }
    return NULL;
}

// 消费者线程函数（学生需要完成）
void *consumer(void *arg) {
    int item;
    while (1) {
        sem_wait(&full);  // P操作，等待满槽信号量
        pthread_mutex_lock(&mutex);  // 进入临界区

        // 完成消费过程，从缓冲区取出数据
        item = buffer[out];
        printf("Consumed: %d from index %d\n", item, out);
        out = (out + 1) % BUFFER_SIZE;

        pthread_mutex_unlock(&mutex);  // 离开临界区
        sem_post(&empty);  // V操作，释放空槽信号量

        sleep(1);  // 模拟消费的时间
    }
    return NULL;
}

int main() {
    pthread_t producer_thread, consumer_thread;

    // 初始化信号量和互斥锁
    sem_init(&empty, 0, BUFFER_SIZE);  // 初始时缓冲区全为空
    sem_init(&full, 0, 0);             // 初始时缓冲区没有满槽
    pthread_mutex_init(&mutex, NULL);  // 初始化互斥锁

    // 创建生产者和消费者线程
    pthread_create(&producer_thread, NULL, producer, NULL);
    pthread_create(&consumer_thread, NULL, consumer, NULL);

    // 等待线程结束
    pthread_join(producer_thread, NULL);
    pthread_join(consumer_thread, NULL);

    // 销毁信号量和互斥锁
    sem_destroy(&empty);
    sem_destroy(&full);
    pthread_mutex_destroy(&mutex);

    return 0;
}

