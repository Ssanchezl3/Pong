"""net.py - Conexion de red del cliente (sockets Berkeley, TCP).

Desacoplado de la interfaz: solo se encarga de enviar y recibir mensajes.
"""
import socket
import threading
import protocol


class Connection:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self._running = True

    def send(self, msg_type, payload=b""):
        """Envia un mensaje al servidor."""
        self.sock.sendall(protocol.encode(msg_type, payload))

    def _recv_exact(self, n):
        """Lee exactamente n bytes (TCP puede fragmentar)."""
        data = b""
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if not chunk:
                return None
            data += chunk
        return data

    def recv(self):
        """Lee un mensaje completo. Devuelve (tipo, payload) o None si se cerro."""
        header = self._recv_exact(3)
        if header is None:
            return None
        msg_type, length = protocol.decode_header(header)
        payload = self._recv_exact(length) if length > 0 else b""
        if payload is None:
            return None
        return msg_type, payload

    def listen(self, on_message):
        """Corre un hilo que llama on_message(tipo, payload) por cada mensaje."""
        def loop():
            while self._running:
                msg = self.recv()
                if msg is None:
                    break
                on_message(*msg)
        threading.Thread(target=loop, daemon=True).start()

    def close(self):
        self._running = False
        self.sock.close()
