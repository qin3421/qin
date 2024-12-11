#include <stdio.h>
#include <unistd.h>
#include <errno.h>

int main() {
    const char *dir_name = "mydir";  // 假设你要删除名为 "mydir" 的目录

    if (rmdir(dir_name) == 0) {
        printf("Directory '%s' deleted successfully.\n", dir_name);
    } else {
        perror("Error deleting directory");
    }

    return 0;
}

