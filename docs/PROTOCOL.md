# MyAppGameProtocol — Especificación

Protocolo de **capa de aplicación** para el juego Pong, sobre **TCP/IP** usando la API de Sockets Berkeley.

## 1. ¿Por qué TCP (SOCK_STREAM)?

Pong necesita que **todos los comandos lleguen y lleguen en orden**: registro del jugador,
movimientos de paleta, actualización de estado y marcador. Si se pierde un mensaje, el juego
se desincroniza. TCP garantiza **entrega confiable y ordenada**, por eso se elige sobre UDP.

## 2. Formato del mensaje (codificación binaria)

Todo mensaje tiene una **cabecera fija de 3 bytes** seguida de un payload de longitud variable:

```
+--------+------------------+---------------------+
| type   | length (2 bytes) | payload (length B)  |
| 1 byte | big-endian       | ...                 |
+--------+------------------+---------------------+
```

- `type`   : 1 byte. Identifica el tipo de mensaje (ver tabla).
- `length` : 2 bytes, entero sin signo en **big-endian (network byte order)**. Tamaño del payload.
- `payload`: `length` bytes. Su contenido depende del tipo.

## 3. Vocabulario de mensajes

| Tipo | Nombre       | Dirección        | Payload                                            |
|------|--------------|------------------|----------------------------------------------------|
| 1    | REGISTER     | Cliente → Server | `nickname\0email` (texto, separados por byte 0)    |
| 2    | WELCOME      | Server → Cliente | 1 byte: número de jugador asignado (1 o 2)         |
| 3    | WAITING      | Server → Cliente | vacío. Esperando al otro jugador                   |
| 4    | START        | Server → Cliente | vacío. La partida empieza                          |
| 5    | INPUT        | Cliente → Server | 1 byte: dirección de la paleta (0=quieto,1=arriba,2=abajo) |
| 6    | STATE        | Server → Cliente | 10 bytes: estado del juego (ver 3.1)               |
| 7    | GAMEOVER     | Server → Cliente | 1 byte: número del jugador ganador                 |
| 8    | ERROR        | Server → Cliente | texto con la descripción del error                 |

### 3.1 Payload de STATE (10 bytes, todos big-endian)

| Offset | Campo       | Bytes | Descripción                    |
|--------|-------------|-------|--------------------------------|
| 0      | ball_x      | 2     | Posición X de la pelota        |
| 2      | ball_y      | 2     | Posición Y de la pelota        |
| 4      | paddle1_y   | 2     | Posición Y de la paleta izq.   |
| 6      | paddle2_y   | 2     | Posición Y de la paleta der.   |
| 8      | score1      | 1     | Puntos jugador 1               |
| 9      | score2      | 1     | Puntos jugador 2               |

Las coordenadas están sobre un tablero lógico de **640 x 480**.

## 4. Reglas de procedimiento

1. El cliente abre la conexión TCP y envía **REGISTER** con su nickname y email.
2. El servidor responde **WELCOME** (nº de jugador). Si aún no hay pareja, envía **WAITING**.
3. Cuando hay dos jugadores emparejados, el servidor envía **START** a ambos.
4. Durante la partida:
   - El cliente envía **INPUT** cada vez que el usuario mueve la paleta.
   - El servidor actualiza el estado (~30 veces/seg) y difunde **STATE** a ambos clientes.
5. Al llegar a la puntuación máxima, el servidor envía **GAMEOVER** y cierra la partida.
6. Cualquier error se comunica con **ERROR** y puede cerrar la conexión.
