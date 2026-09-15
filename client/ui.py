"""ui.py - Interfaz grafica simple con Tkinter (funciona en Windows y Mac).

Tkinter viene incluido con Python, no hay que instalar nada extra.
Esta clase solo dibuja y captura teclas; la red la maneja net.py.
"""
import tkinter as tk
import protocol


class PongUI:
    def __init__(self, connection, nickname):
        self.conn = connection
        self.nick = nickname

        self.root = tk.Tk()
        self.root.title("Pong - " + nickname)
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=protocol.BOARD_W,
                                height=protocol.BOARD_H, bg="black")
        self.canvas.pack()

        self.status = tk.Label(self.root, text="Conectando...",
                               font=("Arial", 14))
        self.status.pack()

        # Teclas: flechas o W/S mueven la paleta
        self.root.bind("<KeyPress-Up>",   lambda e: self._input(protocol.UP))
        self.root.bind("<KeyPress-Down>", lambda e: self._input(protocol.DOWN))
        self.root.bind("<KeyPress-w>",    lambda e: self._input(protocol.UP))
        self.root.bind("<KeyPress-s>",    lambda e: self._input(protocol.DOWN))
        self.root.bind("<KeyRelease>",    lambda e: self._input(protocol.STOP))

        self.player_num = 0
        self.game_over = False

    def _input(self, direction):
        if not self.game_over:
            self.conn.send(protocol.INPUT, bytes([direction]))

    def set_status(self, text):
        # Tkinter solo se toca desde el hilo principal
        self.root.after(0, lambda: self.status.config(text=text))

    def on_message(self, msg_type, payload):
        """Se llama desde el hilo de red por cada mensaje del servidor."""
        if msg_type == protocol.WELCOME:
            self.player_num = payload[0]
            self.set_status(f"Eres el jugador {self.player_num}")
        elif msg_type == protocol.WAITING:
            self.set_status("Esperando a otro jugador...")
        elif msg_type == protocol.START:
            self.set_status("Partida iniciada. Usa flechas o W/S")
        elif msg_type == protocol.STATE:
            state = protocol.unpack_state(payload)
            self.root.after(0, lambda: self._draw(state))
        elif msg_type == protocol.GAMEOVER:
            self.game_over = True
            winner = payload[0]
            result = "GANASTE!" if winner == self.player_num else "Perdiste"
            self.set_status(f"Fin del juego. {result}")
        elif msg_type == protocol.ERROR:
            self.set_status("Error: " + payload.decode(errors="ignore"))

    def _draw(self, s):
        c = self.canvas
        c.delete("all")
        # Linea central
        c.create_line(protocol.BOARD_W / 2, 0, protocol.BOARD_W / 2,
                      protocol.BOARD_H, fill="gray", dash=(5, 5))
        # Pelota
        c.create_oval(s["ball_x"] - 6, s["ball_y"] - 6,
                      s["ball_x"] + 6, s["ball_y"] + 6, fill="white")
        # Paletas (ancho 10, alto 80)
        c.create_rectangle(15, s["paddle1_y"] - 40, 25, s["paddle1_y"] + 40,
                           fill="cyan")
        c.create_rectangle(protocol.BOARD_W - 25, s["paddle2_y"] - 40,
                           protocol.BOARD_W - 15, s["paddle2_y"] + 40, fill="yellow")
        # Marcador
        c.create_text(protocol.BOARD_W / 2, 30,
                      text=f"{s['score1']}   -   {s['score2']}",
                      fill="white", font=("Arial", 24))

    def run(self):
        self.conn.listen(self.on_message)
        self.root.mainloop()
