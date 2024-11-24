#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char *argv[])
{
    printf("hello world (pid:%d)\n", (int) getpid());
    int rc = fork();
    if (rc < 0) {
        // fork failed; exit
        fprintf(stderr, "fork failed\n");
        exit(1);
    } else if (rc == 0) {
        // child (new process)
        
	    printf("hello, I am child (pid:%d)\n", (int) getpid());
		int rc2 = fork();
		if(rc2 < 0 )
		{
			fprintf(stderr, "fork failed\n");
			exit(1);
		}else if (rc2 == 0)
		{
			printf("hello, I am child  (pid:%d)\n", (int)getpid());
		}else{
			sleep(1);
			printf("hello, I am parent of %d (pid:%d)\n", rc2, getpid());
		}

		
    } else {
        // parent goes down this path (original process)
       sleep(3);
		printf("hello, I am parent of %d (pid:%d)\n",
	       rc, (int) getpid());
	
    }

    return 0;
}
