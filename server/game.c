/* game.c - Reglas de Pong: movimiento de paletas, rebotes y puntaje. */
#include "game.h"
#include "protocol.h"  /* BOARD_W, BOARD_H, INPUT_UP, INPUT_DOWN */

#define PADDLE_SPEED 8
#define PADDLE_X1 20             /* X fija de la paleta izquierda */
#define PADDLE_X2 (BOARD_W - 20) /* X fija de la paleta derecha */

void game_init(Game *g) {
    g->ball_x = BOARD_W / 2;
    g->ball_y = BOARD_H / 2;
    g->ball_vx = 5;
    g->ball_vy = 3;
    g->paddle1_y = BOARD_H / 2;
    g->paddle2_y = BOARD_H / 2;
    g->score1 = 0;
    g->score2 = 0;
    g->input1 = 0;
    g->input2 = 0;
    g->over = 0;
    g->winner = 0;
}

/* Mantiene un valor dentro de [min, max]. */
static int clamp(int v, int min, int max) {
    if (v < min) return min;
    if (v > max) return max;
    return v;
}

/* Mueve una paleta segun el input del jugador. */
static void move_paddle(int *y, int input) {
    if (input == INPUT_UP)   *y -= PADDLE_SPEED;
    if (input == INPUT_DOWN) *y += PADDLE_SPEED;
    *y = clamp(*y, PADDLE_H / 2, BOARD_H - PADDLE_H / 2);
}

/* Reinicia la pelota al centro tras un punto. */
static void reset_ball(Game *g, int direction) {
    g->ball_x = BOARD_W / 2;
    g->ball_y = BOARD_H / 2;
    g->ball_vx = 5 * direction;
    g->ball_vy = 3;
}

/* True si la pelota toca la paleta situada en paddle_x / paddle_y. */
static int hits_paddle(Game *g, int paddle_y) {
    return g->ball_y >= paddle_y - PADDLE_H / 2 &&
           g->ball_y <= paddle_y + PADDLE_H / 2;
}

void game_step(Game *g) {
    if (g->over) return;

    move_paddle(&g->paddle1_y, g->input1);
    move_paddle(&g->paddle2_y, g->input2);

    g->ball_x += g->ball_vx;
    g->ball_y += g->ball_vy;

    /* Rebote en techo y piso */
    if (g->ball_y <= 0 || g->ball_y >= BOARD_H) g->ball_vy = -g->ball_vy;

    /* Rebote en paleta izquierda */
    if (g->ball_x <= PADDLE_X1 && g->ball_vx < 0) {
        if (hits_paddle(g, g->paddle1_y)) g->ball_vx = -g->ball_vx;
    }
    /* Rebote en paleta derecha */
    if (g->ball_x >= PADDLE_X2 && g->ball_vx > 0) {
        if (hits_paddle(g, g->paddle2_y)) g->ball_vx = -g->ball_vx;
    }

    /* Punto para el jugador 2 (pelota salio por la izquierda) */
    if (g->ball_x < 0) {
        g->score2++;
        reset_ball(g, 1);
    }
    /* Punto para el jugador 1 (pelota salio por la derecha) */
    if (g->ball_x > BOARD_W) {
        g->score1++;
        reset_ball(g, -1);
    }

    /* Fin de la partida */
    if (g->score1 >= WIN_SCORE) { g->over = 1; g->winner = 1; }
    if (g->score2 >= WIN_SCORE) { g->over = 1; g->winner = 2; }
}
