"""client.py - Punto de entrada del cliente Pong.

Uso:
    python client.py <host> <puerto>

Pide nickname y email, se registra en el servidor y abre la ventana del juego.
Funciona en Windows y Mac (solo requiere Python 3, Tkinter ya viene incluido).
"""
import sys
import protocol
from net import Connection
from ui import PongUI


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000

    nickname = input("Nickname: ").strip() or "Jugador"
    email = input("Email: ").strip() or "sin@email.com"

    # Conectar y registrar (payload = "nick\0email")
    conn = Connection(host, port)
    payload = nickname.encode() + b"\0" + email.encode()
    conn.send(protocol.REGISTER, payload)

    # Abrir la interfaz
    ui = PongUI(conn, nickname)
    ui.run()
    conn.close()


if __name__ == "__main__":
    main()
