// client.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#define PORT 8080  // 服务器的端口号

int main() {
    int sock = 0;
    struct sockaddr_in server_address;
    char message[1024];
    char buffer[1024] = {0};

    // 创建客户端套接字
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("Socket creation failed");
        exit(EXIT_FAILURE);
    }

    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(PORT);

    // 将服务器地址转换成二进制格式
    if (inet_pton(AF_INET, "127.0.0.1", &server_address.sin_addr) <= 0) {
        perror("Invalid address");
        exit(EXIT_FAILURE);
    }

    // 连接服务器
    if (connect(sock, (struct sockaddr *)&server_address, sizeof(server_address)) < 0) {
        perror("Connection failed");
        exit(EXIT_FAILURE);
    }

    // 提示用户输入消息
    printf("Enter message to send to server: ");
    fgets(message, sizeof(message), stdin);  // 从标准输入读取消息

    // 去掉换行符（如果存在）
    message[strcspn(message, "\n")] = 0;

    // 发送消息到服务器
    send(sock, message, strlen(message), 0);

    // 接收服务器的响应
    read(sock, buffer, sizeof(buffer));
    printf("Server response: %s\n", buffer);

    // 关闭套接字
    close(sock);
    return 0;
}

