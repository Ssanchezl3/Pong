/* protocol.c - Codec binario: convierte mensajes <-> bytes en el socket.
 * Usa cabecera de 3 bytes: [type:1][length:2 big-endian][payload]. */
#include "protocol.h"
#include <unistd.h>
#include <string.h>

/* Escribe exactamente n bytes (TCP puede enviar de a poco). */
static int send_all(int fd, const uint8_t *buf, int n) {
    int sent = 0;
    while (sent < n) {
        int r = write(fd, buf + sent, n - sent);
        if (r <= 0) return -1;
        sent += r;
    }
    return 0;
}

/* Lee exactamente n bytes. */
static int recv_all(int fd, uint8_t *buf, int n) {
    int got = 0;
    while (got < n) {
        int r = read(fd, buf + got, n - got);
        if (r <= 0) return -1;
        got += r;
    }
    return 0;
}

int proto_send(int fd, uint8_t type, const uint8_t *payload, uint16_t length) {
    uint8_t header[3];
    header[0] = type;
    header[1] = (length >> 8) & 0xFF;  /* byte alto (big-endian) */
    header[2] = length & 0xFF;         /* byte bajo */
    if (send_all(fd, header, 3) < 0) return -1;
    if (length > 0 && send_all(fd, payload, length) < 0) return -1;
    return 0;
}

int proto_recv(int fd, Message *msg) {
    uint8_t header[3];
    if (recv_all(fd, header, 3) < 0) return -1;
    msg->type = header[0];
    msg->length = (header[1] << 8) | header[2];
    if (msg->length > MAX_PAYLOAD) return -1;
    if (msg->length > 0 && recv_all(fd, msg->payload, msg->length) < 0) return -1;
    return 0;
}
