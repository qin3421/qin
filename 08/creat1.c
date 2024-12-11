#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

int main() {
    int fd;

    // 创建文件 testfile2.txt，权限为 rw-r--r--
    fd = creat("testfile2.txt", 0644);
    if (fd == -1) {
        perror("File creation failed");
        return 1;
    }
    printf("File created successfully with file descriptor: %d\n", fd);

    // 关闭文件
    close(fd);
    return 0;
}

