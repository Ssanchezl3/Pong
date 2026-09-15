# Makefile para el servidor de Pong (C)
CC = gcc
CFLAGS = -Wall -Wextra -pthread
OBJS = server.o protocol.o game.o logger.o

server: $(OBJS)
	$(CC) $(CFLAGS) -o server $(OBJS)

server.o: server.c protocol.h game.h logger.h
protocol.o: protocol.c protocol.h
game.o: game.c game.h protocol.h
logger.o: logger.c logger.h

clean:
	rm -f server $(OBJS)

.PHONY: clean
