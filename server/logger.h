/* logger.h - Registro de eventos por consola y a archivo de log. */
#ifndef LOGGER_H
#define LOGGER_H

/* Inicializa el logger con el archivo dado. Devuelve 0 si ok. */
int log_init(const char *filename);

/* Escribe una linea de log (con fecha) en consola y en el archivo.
 * Uso igual que printf: log_msg("Cliente %d conectado", id); */
void log_msg(const char *fmt, ...);

/* Cierra el archivo de log. */
void log_close(void);

#endif
