# Pong — Cliente/Servidor en Red

Proyecto N1 — Internet: Arquitectura y Protocolos.

Juego Pong multijugador en línea con arquitectura **cliente/servidor**, comunicación
por **sockets Berkeley (TCP)** y un **protocolo binario propio** (MyAppGameProtocol).

## 1. Introducción

El objetivo es practicar programación en red, concurrencia y diseño de protocolos.
Dos jugadores se conectan a un servidor que mantiene el estado del juego, valida los
movimientos y notifica a ambos clientes. El servidor soporta **varias parejas jugando
en paralelo** mediante hilos.

- **Servidor:** C (obligatorio), sockets Berkeley + `pthreads` + logger.
- **Cliente:** Python 3 con Tkinter → corre igual en **Windows y Mac** (sin instalar nada).
- **Transporte:** **TCP (SOCK_STREAM)**, porque los comandos no se pueden perder ni desordenar.

## 2. Desarrollo

### Arquitectura desacoplada

Cada responsabilidad está en su propio archivo:

```
Pong/
├── server/            # Aplicación servidor (C)
│   ├── server.c       #   solo red + concurrencia (sockets, hilos, emparejamiento)
│   ├── protocol.c/.h  #   codec binario del protocolo
│   ├── game.c/.h      #   reglas del juego (lógica pura, sin red)
│   ├── logger.c/.h    #   registro por consola y a archivo
│   └── Makefile
├── client/            # Aplicación cliente (Python)
│   ├── client.py      #   punto de entrada
│   ├── net.py         #   conexión de red
│   ├── protocol.py    #   codec binario (mismo formato que en C)
│   └── ui.py          #   interfaz gráfica (Tkinter)
└── docs/
    └── PROTOCOL.md    # especificación de MyAppGameProtocol
```

### El protocolo MyAppGameProtocol

Mensajes binarios con cabecera fija de 3 bytes:

```
[type:1 byte][length:2 bytes big-endian][payload:length bytes]
```

Detalle completo (tipos de mensaje, reglas de procedimiento y formato de STATE) en
[`docs/PROTOCOL.md`](docs/PROTOCOL.md).

### Compilar y ejecutar el servidor

```bash
cd server
make
./server <PORT> <LogFile>      # ejemplo: ./server 5000 pong.log
```

El servidor imprime cada evento por consola y lo guarda en el archivo de log.

### Ejecutar el cliente (Windows / Mac / Linux)

Requiere solo **Python 3** (Tkinter viene incluido):

```bash
cd client
python client.py <host> <puerto>   # ejemplo: python client.py 127.0.0.1 5000
```

Pide *nickname* y *email*, se registra y abre la ventana. **Controles:** flechas ↑ ↓ o teclas **W / S**.
Abre **dos clientes** para jugar una partida.

## 3. Conclusiones

- TCP encaja bien con Pong porque garantiza entrega y orden de los comandos.
- Separar red, protocolo, lógica y logging hace el código corto y fácil de mantener y explicar.
- Un protocolo binario con cabecera `[tipo][longitud]` es simple de codificar en C y Python.
- Los hilos permiten atender varias parejas de jugadores de forma concurrente.

## 4. Referencias

- Beej's Guide to Network Programming — https://beej.us/guide/bgnet/
- Beej's Guide to C — https://beej.us/guide/bgc/
- TCP Server-Client en C — https://www.geeksforgeeks.org/tcp-server-client-implementation-in-c/
- Pong (Wikipedia) — https://en.wikipedia.org/wiki/Pong

---

Guía de despliegue en AWS: [`docs/AWS_DEPLOY.md`](docs/AWS_DEPLOY.md)
