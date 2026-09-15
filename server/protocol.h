/* protocol.h - Definicion del protocolo binario MyAppGameProtocol.
 * Este archivo describe SOLO el formato de los mensajes (desacoplado de la red). */
#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <stdint.h>

/* Tipos de mensaje (1 byte). Ver docs/PROTOCOL.md */
#define MSG_REGISTER 1
#define MSG_WELCOME  2
#define MSG_WAITING  3
#define MSG_START    4
#define MSG_INPUT    5
#define MSG_STATE    6
#define MSG_GAMEOVER 7
#define MSG_ERROR    8

/* Direcciones para MSG_INPUT */
#define INPUT_STOP 0
#define INPUT_UP   1
#define INPUT_DOWN 2

/* Tablero logico */
#define BOARD_W 640
#define BOARD_H 480

#define MAX_PAYLOAD 512

/* Un mensaje ya decodificado */
typedef struct {
    uint8_t  type;
    uint16_t length;
    uint8_t  payload[MAX_PAYLOAD];
} Message;

/* Envia un mensaje por el socket fd. Devuelve 0 si ok, -1 si error. */
int proto_send(int fd, uint8_t type, const uint8_t *payload, uint16_t length);

/* Lee un mensaje completo desde el socket fd. Devuelve 0 si ok, -1 si error/cierre. */
int proto_recv(int fd, Message *msg);

#endif
