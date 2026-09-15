/* game.h - Logica pura del juego Pong (sin sockets ni hilos). */
#ifndef GAME_H
#define GAME_H

#define PADDLE_H 80    /* alto de la paleta */
#define WIN_SCORE 5    /* puntos para ganar */

/* Estado de una partida entre dos jugadores. */
typedef struct {
    int ball_x, ball_y;      /* posicion de la pelota */
    int ball_vx, ball_vy;    /* velocidad de la pelota */
    int paddle1_y, paddle2_y;/* posicion Y de cada paleta */
    int score1, score2;      /* marcador */
    int input1, input2;      /* ultimo INPUT recibido de cada jugador */
    int over;                /* 1 si la partida termino */
    int winner;              /* jugador ganador (1 o 2) */
} Game;

/* Inicializa la partida en su estado de arranque. */
void game_init(Game *g);

/* Avanza la simulacion un paso (mueve paletas y pelota, revisa puntos). */
void game_step(Game *g);

#endif
