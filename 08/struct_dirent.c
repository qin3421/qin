#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <sys/types.h>

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
        printf("Name: %s\n", entry->d_name);
        printf("  Inode: %ld\n", (long)entry->d_ino);
        printf("  Type: ");
        
        // 判断文件类型
        switch (entry->d_type) {
            case DT_REG:
                printf("Regular file\n");
                break;
            case DT_DIR:
                printf("Directory\n");
                break;
            case DT_LNK:
                printf("Symbolic link\n");
                break;
            default:
                printf("Other\n");
        }
        printf("  Record length: %d\n", entry->d_reclen);
    }

    // 关闭目录
    closedir(dir);
    return 0;
}

