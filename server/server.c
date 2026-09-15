/* server.c - Servidor de Pong. Sockets Berkeley (TCP) + hilos (pthreads).
 * Uso: ./server <PORT> <LogFile>
 *
 * Arquitectura desacoplada:
 *   - protocol.c : formato binario de los mensajes
 *   - game.c     : reglas del juego
 *   - logger.c   : registro de eventos
 *   - server.c   : SOLO red y concurrencia (este archivo)
 *
 * Modelo: cada cliente que llega se pone en espera. Cuando hay dos,
 * se crea una partida y un hilo que la corre (game loop) para esa pareja.
 * Esto permite N parejas jugando en paralelo. */
#include "protocol.h"
#include "game.h"
#include "logger.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define TICK_US 33000  /* ~30 actualizaciones por segundo */

/* Datos de un jugador conectado. */
typedef struct {
    int fd;
    char nick[64];
} Player;

/* Una partida = dos jugadores + su estado. */
typedef struct {
    Player p1, p2;
    Game game;
} Match;

/* Sala de espera: guarda un jugador hasta que llegue su pareja. */
static Player waiting;
static int has_waiting = 0;
static pthread_mutex_t wait_lock = PTHREAD_MUTEX_INITIALIZER;
static int match_counter = 0;

/* Empaqueta el estado del juego en el payload de STATE (10 bytes). */
static void pack_state(Game *g, uint8_t *buf) {
    buf[0] = (g->ball_x >> 8) & 0xFF;   buf[1] = g->ball_x & 0xFF;
    buf[2] = (g->ball_y >> 8) & 0xFF;   buf[3] = g->ball_y & 0xFF;
    buf[4] = (g->paddle1_y >> 8) & 0xFF;buf[5] = g->paddle1_y & 0xFF;
    buf[6] = (g->paddle2_y >> 8) & 0xFF;buf[7] = g->paddle2_y & 0xFF;
    buf[8] = (uint8_t)g->score1;
    buf[9] = (uint8_t)g->score2;
}

/* Hilo que lee los INPUT de UN jugador y los guarda en el juego. */
typedef struct { int fd; int *input_slot; int *alive; } InputArg;

static void *input_thread(void *arg) {
    InputArg *ia = (InputArg *)arg;
    Message msg;
    while (*ia->alive) {
        if (proto_recv(ia->fd, &msg) < 0) { *ia->alive = 0; break; }
        if (msg.type == MSG_INPUT && msg.length >= 1) {
            *ia->input_slot = msg.payload[0];
        }
    }
    return NULL;
}

/* Hilo principal de una partida: corre el game loop y difunde el estado. */
static void *match_thread(void *arg) {
    Match *m = (Match *)arg;
    int id = ++match_counter;
    log_msg("Partida #%d iniciada: '%s' (P1) vs '%s' (P2)", id, m->p1.nick, m->p2.nick);

    game_init(&m->game);

    /* Avisar arranque a ambos */
    proto_send(m->p1.fd, MSG_START, NULL, 0);
    proto_send(m->p2.fd, MSG_START, NULL, 0);

    /* Un hilo por jugador para leer sus inputs sin bloquear el loop */
    int alive = 1;
    InputArg a1 = { m->p1.fd, &m->game.input1, &alive };
    InputArg a2 = { m->p2.fd, &m->game.input2, &alive };
    pthread_t t1, t2;
    pthread_create(&t1, NULL, input_thread, &a1);
    pthread_create(&t2, NULL, input_thread, &a2);

    /* Game loop */
    uint8_t state[10];
    while (alive && !m->game.over) {
        game_step(&m->game);
        pack_state(&m->game, state);
        if (proto_send(m->p1.fd, MSG_STATE, state, 10) < 0) break;
        if (proto_send(m->p2.fd, MSG_STATE, state, 10) < 0) break;
        usleep(TICK_US);
    }

    if (m->game.over) {
        uint8_t w = (uint8_t)m->game.winner;
        proto_send(m->p1.fd, MSG_GAMEOVER, &w, 1);
        proto_send(m->p2.fd, MSG_GAMEOVER, &w, 1);
        log_msg("Partida #%d terminada. Ganador: jugador %d (%d-%d)",
                id, m->game.winner, m->game.score1, m->game.score2);
    }

    alive = 0;
    close(m->p1.fd);
    close(m->p2.fd);
    pthread_cancel(t1);
    pthread_cancel(t2);
    free(m);
    return NULL;
}

/* Registra a un cliente recien conectado y lo empareja o lo deja esperando. */
static void handle_new_client(int fd, struct sockaddr_in *addr) {
    Message msg;
    if (proto_recv(fd, &msg) < 0 || msg.type != MSG_REGISTER) {
        proto_send(fd, MSG_ERROR, (uint8_t *)"Se esperaba REGISTER", 20);
        close(fd);
        return;
    }

    Player p;
    p.fd = fd;
    /* El payload es "nick\0email"; tomamos el nick hasta el primer 0 */
    strncpy(p.nick, (char *)msg.payload, sizeof(p.nick) - 1);
    p.nick[sizeof(p.nick) - 1] = '\0';
    log_msg("REGISTER de '%s' desde %s", p.nick, inet_ntoa(addr->sin_addr));

    pthread_mutex_lock(&wait_lock);
    if (!has_waiting) {
        /* Primer jugador: queda esperando pareja */
        waiting = p;
        has_waiting = 1;
        uint8_t num = 1;
        proto_send(fd, MSG_WELCOME, &num, 1);
        proto_send(fd, MSG_WAITING, NULL, 0);
        pthread_mutex_unlock(&wait_lock);
        log_msg("'%s' esperando oponente...", p.nick);
    } else {
        /* Segundo jugador: se forma la partida */
        Match *m = malloc(sizeof(Match));
        m->p1 = waiting;
        m->p2 = p;
        has_waiting = 0;
        pthread_mutex_unlock(&wait_lock);

        uint8_t num = 2;
        proto_send(fd, MSG_WELCOME, &num, 1);

        pthread_t t;
        pthread_create(&t, NULL, match_thread, m);
        pthread_detach(t);
    }
}

/* Argumento para el hilo que recibe a un cliente. */
typedef struct { int fd; struct sockaddr_in addr; } ClientArg;

static void *client_thread(void *arg) {
    ClientArg *ca = (ClientArg *)arg;
    handle_new_client(ca->fd, &ca->addr);
    free(ca);
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Uso: %s <PORT> <LogFile>\n", argv[0]);
        return 1;
    }
    int port = atoi(argv[1]);

    if (log_init(argv[2]) < 0) {
        fprintf(stderr, "No se pudo abrir el archivo de log: %s\n", argv[2]);
        return 1;
    }

    /* 1. Crear socket TCP */
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) { log_msg("Error creando socket"); return 1; }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    /* 2. Enlazar a la direccion/puerto */
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;  /* escucha en todas las interfaces */
    addr.sin_port = htons(port);

    if (bind(server_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        log_msg("Error en bind al puerto %d", port);
        return 1;
    }

    /* 3. Escuchar */
    if (listen(server_fd, 10) < 0) { log_msg("Error en listen"); return 1; }
    log_msg("Servidor Pong escuchando en el puerto %d", port);

    /* 4. Aceptar clientes; un hilo por cada uno */
    while (1) {
        struct sockaddr_in caddr;
        socklen_t clen = sizeof(caddr);
        int cfd = accept(server_fd, (struct sockaddr *)&caddr, &clen);
        if (cfd < 0) continue;

        ClientArg *ca = malloc(sizeof(ClientArg));
        ca->fd = cfd;
        ca->addr = caddr;
        pthread_t t;
        pthread_create(&t, NULL, client_thread, ca);
        pthread_detach(t);
    }

    close(server_fd);
    log_close();
    return 0;
}
