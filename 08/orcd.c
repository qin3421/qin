#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>

int main() {
    const char *dir_path = "."; // 当前目录
    DIR *dir;
    struct dirent *entry;

    // 打开目录
    dir = opendir(dir_path);
    if (dir == NULL) {
        perror("Failed to open directory");
        return 1;
    }

    printf("Contents of directory '%s':\n", dir_path);

    // 读取目录内容
    while ((entry = readdir(dir)) != NULL) {
        printf(" - %s\n", entry->d_name);
    }

    // 关闭目录
    if (closedir(dir) != 0) {
        perror("Failed to close directory");
        return 1;
    }

    return 0;
}

