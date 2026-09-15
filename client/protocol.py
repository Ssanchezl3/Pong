"""protocol.py - Codec binario MyAppGameProtocol (lado cliente).

Mismo formato que el servidor en C:
    [type:1 byte][length:2 bytes big-endian][payload:length bytes]
Ver docs/PROTOCOL.md
"""
import struct

# Tipos de mensaje
REGISTER = 1
WELCOME = 2
WAITING = 3
START = 4
INPUT = 5
STATE = 6
GAMEOVER = 7
ERROR = 8

# Direcciones de INPUT
STOP = 0
UP = 1
DOWN = 2

# Tablero logico
BOARD_W = 640
BOARD_H = 480


def encode(msg_type, payload=b""):
    """Arma los bytes de un mensaje listos para enviar."""
    return struct.pack(">BH", msg_type, len(payload)) + payload


def decode_header(header):
    """Devuelve (tipo, longitud) a partir de los 3 bytes de cabecera."""
    return struct.unpack(">BH", header)


def unpack_state(payload):
    """Convierte el payload de STATE (10 bytes) en un diccionario."""
    ball_x, ball_y, p1, p2 = struct.unpack(">HHHH", payload[:8])
    score1, score2 = payload[8], payload[9]
    return {
        "ball_x": ball_x, "ball_y": ball_y,
        "paddle1_y": p1, "paddle2_y": p2,
        "score1": score1, "score2": score2,
    }
