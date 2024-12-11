#include <sys/stat.h>
#include <sys/types.h>
#include <stdio.h>
#include <errno.h>

int main() {
    const char *dir_name = "new_directory";
    int result;

    // 创建目录，权限设置为 rwxr-xr-x (0755)
    result = mkdir(dir_name, 0755);
    if (result == 0) {
        printf("Directory '%s' created successfully.\n", dir_name);
    } else {
        // 检查错误原因
        if (errno == EEXIST) {
            printf("Directory '%s' already exists.\n", dir_name);
        } else {
            perror("mkdir failed");
        }
    }
    return 0;
}

