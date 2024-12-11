#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

int main() {
    int fd;
    char write_buf[] = "Hello, Linux file system!";
    char read_buf[128];  // 用于读取文件内容
    ssize_t bytes_written, bytes_read;

    // 打开或创建文件
    fd = open("example.txt", O_CREAT | O_WRONLY, 0644);
    if (fd == -1) {
        perror("Failed to open file");
        return 1;
    }

    // 写入文件
    bytes_written = write(fd, write_buf, strlen(write_buf));
    if (bytes_written == -1) {
        perror("Failed to write to file");
        close(fd);
        return 1;
    }
    printf("Wrote %ld bytes to file.\n", bytes_written);

    // 关闭文件
    close(fd);

    // 重新打开文件以读取
    fd = open("example.txt", O_RDONLY);
    if (fd == -1) {
        perror("Failed to open file for reading");
        return 1;
    }

    // 读取文件
    bytes_read = read(fd, read_buf, sizeof(read_buf) - 1);
    if (bytes_read == -1) {
        perror("Failed to read file");
        close(fd);
        return 1;
    }

    // 确保读取的内容以 '\0' 结尾
    read_buf[bytes_read] = '\0';
    printf("Read %ld bytes from file: %s\n", bytes_read, read_buf);

    // 关闭文件
    close(fd);
    return 0;
}

