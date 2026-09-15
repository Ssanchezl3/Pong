/* logger.c - Imprime eventos en consola y en un archivo, con marca de tiempo.
 * Usa un mutex para que varios hilos no mezclen sus lineas. */
#include "logger.h"
#include <stdio.h>
#include <stdarg.h>
#include <time.h>
#include <pthread.h>

static FILE *log_file = NULL;
static pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

int log_init(const char *filename) {
    log_file = fopen(filename, "a");
    return (log_file == NULL) ? -1 : 0;
}

void log_msg(const char *fmt, ...) {
    pthread_mutex_lock(&lock);

    /* Marca de tiempo legible */
    char stamp[32];
    time_t now = time(NULL);
    strftime(stamp, sizeof(stamp), "%Y-%m-%d %H:%M:%S", localtime(&now));

    /* Construye el mensaje del usuario */
    char body[512];
    va_list args;
    va_start(args, fmt);
    vsnprintf(body, sizeof(body), fmt, args);
    va_end(args);

    /* Consola */
    printf("[%s] %s\n", stamp, body);
    fflush(stdout);

    /* Archivo */
    if (log_file) {
        fprintf(log_file, "[%s] %s\n", stamp, body);
        fflush(log_file);
    }

    pthread_mutex_unlock(&lock);
}

void log_close(void) {
    if (log_file) fclose(log_file);
}
