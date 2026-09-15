"""Genera docs/Documentacion_Pong.pdf con la explicacion del codigo y diagramas UML.
Ejecutar: python3 docs/gen_pdf.py
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, Flowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

OUT = __file__.rsplit("/", 1)[0] + "/Documentacion_Pong.pdf"

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=17,
                    textColor=colors.HexColor("#1a3c6e"), spaceAfter=8)
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13,
                    textColor=colors.HexColor("#25567b"), spaceBefore=10, spaceAfter=5)
BODY = ParagraphStyle("BODY", parent=styles["BodyText"], fontSize=10.5,
                      leading=15, alignment=TA_LEFT, spaceAfter=6)
CODE = ParagraphStyle("CODE", parent=styles["Code"], fontSize=8.5,
                      leading=11, backColor=colors.HexColor("#f2f4f7"),
                      borderPadding=6, textColor=colors.HexColor("#222"))
TITLE = ParagraphStyle("TITLE", parent=styles["Title"], fontSize=26,
                       textColor=colors.HexColor("#1a3c6e"))
SUB = ParagraphStyle("SUB", parent=styles["Normal"], fontSize=13,
                     alignment=TA_CENTER, textColor=colors.HexColor("#555"))
CAP = ParagraphStyle("CAP", parent=styles["Normal"], fontSize=9,
                     alignment=TA_CENTER, textColor=colors.HexColor("#777"),
                     spaceBefore=4, spaceAfter=10)


# ---------- Diagramas UML dibujados a mano con Flowables ----------
class SequenceDiagram(Flowable):
    """Diagrama de secuencia del protocolo (Cliente / Servidor / Cliente 2)."""
    def __init__(self, width=16 * cm, height=13 * cm):
        self.width, self.height = width, height

    def draw(self):
        c = self.canv
        lanes = [("PongClient 1", 2.2 * cm), ("PongServer", 8 * cm), ("PongClient 2", 13.8 * cm)]
        top = self.height - 0.4 * cm
        bottom = 0.5 * cm
        # Cabeceras y lineas de vida
        for name, x in lanes:
            c.setFillColor(colors.HexColor("#dceaf7"))
            c.setStrokeColor(colors.HexColor("#25567b"))
            c.roundRect(x - 1.7 * cm, top - 0.7 * cm, 3.4 * cm, 0.7 * cm, 4, fill=1)
            c.setFillColor(colors.HexColor("#1a3c6e"))
            c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(x, top - 0.48 * cm, name)
            c.setStrokeColor(colors.HexColor("#aaaaaa"))
            c.setDash(2, 2)
            c.line(x, top - 0.7 * cm, x, bottom)
            c.setDash()
        x1, xs, x2 = lanes[0][1], lanes[1][1], lanes[2][1]

        def arrow(y, xa, xb, label):
            c.setStrokeColor(colors.HexColor("#2b6cb0"))
            c.setFillColor(colors.HexColor("#2b6cb0"))
            c.setLineWidth(1.2)
            c.line(xa, y, xb, y)
            d = 0.16 * cm
            if xb > xa:
                c.line(xb, y, xb - d, y + d); c.line(xb, y, xb - d, y - d)
            else:
                c.line(xb, y, xb + d, y + d); c.line(xb, y, xb + d, y - d)
            c.setFont("Helvetica", 8)
            c.setFillColor(colors.HexColor("#333"))
            c.drawCentredString((xa + xb) / 2, y + 0.1 * cm, label)

        y = top - 1.6 * cm
        step = 1.0 * cm
        arrow(y, x1, xs, "REGISTER (nick, email)"); y -= step
        arrow(y, xs, x1, "WELCOME (jugador 1)"); y -= step
        arrow(y, xs, x1, "WAITING"); y -= step
        arrow(y, x2, xs, "REGISTER (nick, email)"); y -= step
        arrow(y, xs, x2, "WELCOME (jugador 2)"); y -= step
        arrow(y, xs, x1, "START"); y -= 0.55 * cm
        arrow(y, xs, x2, "START"); y -= step
        arrow(y, x1, xs, "INPUT (arriba/abajo)"); y -= step
        arrow(y, xs, x1, "STATE (pelota, paletas, score)"); y -= 0.55 * cm
        arrow(y, xs, x2, "STATE (pelota, paletas, score)"); y -= step
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(colors.HexColor("#888"))
        c.drawCentredString(xs, y + 0.2 * cm, "... loop ~30 veces/seg ...")
        y -= step
        arrow(y, xs, x1, "GAMEOVER (ganador)"); y -= 0.55 * cm
        arrow(y, xs, x2, "GAMEOVER (ganador)")


class MessageFormat(Flowable):
    """Diagrama del formato binario del mensaje."""
    def __init__(self, width=16 * cm, height=3.2 * cm):
        self.width, self.height = width, height

    def draw(self):
        c = self.canv
        y = 1.3 * cm
        h = 1.2 * cm
        boxes = [("type\n1 byte", 3.2 * cm, "#f6c6c6"),
                 ("length\n2 bytes (big-endian)", 5.5 * cm, "#c6ddf6"),
                 ("payload\nN bytes", 6.5 * cm, "#c9f0d0")]
        x = 0.4 * cm
        for label, w, color in boxes:
            c.setFillColor(colors.HexColor(color))
            c.setStrokeColor(colors.HexColor("#555"))
            c.rect(x, y, w, h, fill=1)
            c.setFillColor(colors.HexColor("#222"))
            c.setFont("Helvetica-Bold", 9)
            lines = label.split("\n")
            c.drawCentredString(x + w / 2, y + h / 2 + 2, lines[0])
            c.setFont("Helvetica", 7.5)
            c.drawCentredString(x + w / 2, y + h / 2 - 9, lines[1])
            x += w
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(colors.HexColor("#777"))
        c.drawString(0.4 * cm, y - 0.5 * cm, "Cabecera fija de 3 bytes + payload de tamano variable")


class ComponentDiagram(Flowable):
    """Diagrama de componentes / arquitectura desacoplada."""
    def __init__(self, width=16 * cm, height=9.2 * cm):
        self.width, self.height = width, height

    def draw(self):
        c = self.canv

        def box(x, y, w, h, title, sub, color):
            c.setFillColor(colors.HexColor(color))
            c.setStrokeColor(colors.HexColor("#555"))
            c.roundRect(x, y, w, h, 5, fill=1)
            c.setFillColor(colors.HexColor("#1a3c6e"))
            c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(x + w / 2, y + h - 0.5 * cm, title)
            c.setFillColor(colors.HexColor("#444"))
            c.setFont("Helvetica", 7.3)
            yy = y + h - 0.95 * cm
            for line in sub:
                c.drawCentredString(x + w / 2, yy, line)
                yy -= 0.34 * cm

        # Servidor (C)
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.HexColor("#1a3c6e"))
        c.drawString(0.5 * cm, 8.9 * cm, "SERVIDOR (C)")
        box(0.5 * cm, 5.4 * cm, 3.5 * cm, 2.2 * cm, "server.c",
            ["red +", "concurrencia", "(sockets, hilos)"], "#ffe2c6")
        box(4.4 * cm, 5.4 * cm, 3.3 * cm, 2.2 * cm, "protocol.c",
            ["codec", "binario"], "#f6c6c6")
        box(0.5 * cm, 2.9 * cm, 3.5 * cm, 2.1 * cm, "game.c",
            ["reglas de", "Pong"], "#c9f0d0")
        box(4.4 * cm, 2.9 * cm, 3.3 * cm, 2.1 * cm, "logger.c",
            ["log consola", "+ archivo"], "#e6d5f2")

        # Cliente (Python)
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.HexColor("#1a3c6e"))
        c.drawString(9 * cm, 8.9 * cm, "CLIENTE (Python)")
        box(9 * cm, 5.4 * cm, 3.3 * cm, 2.2 * cm, "net.py",
            ["conexion", "de red"], "#ffe2c6")
        box(12.6 * cm, 5.4 * cm, 3.3 * cm, 2.2 * cm, "protocol.py",
            ["codec", "binario"], "#f6c6c6")
        box(9 * cm, 2.9 * cm, 3.3 * cm, 2.1 * cm, "ui.py",
            ["interfaz", "Tkinter"], "#c9f0d0")
        box(12.6 * cm, 2.9 * cm, 3.3 * cm, 2.1 * cm, "client.py",
            ["punto de", "entrada"], "#e6d5f2")

        # Conexion TCP entre los dos protocolos (protocol.c <-> protocol.py).
        # La linea sube por encima de las cajas para no solaparse con el texto.
        c.setStrokeColor(colors.HexColor("#2b6cb0"))
        c.setLineWidth(1.4)
        c.setDash(4, 3)
        cx1 = 4.4 * cm + 3.3 * cm / 2   # centro superior de protocol.c
        cx2 = 12.6 * cm + 3.3 * cm / 2  # centro superior de protocol.py
        ytop = 7.6 * cm                 # justo encima de las cajas (que llegan a 7.6cm)
        yup = 8.35 * cm                 # altura del "puente"
        c.line(cx1, ytop, cx1, yup)
        c.line(cx1, yup, cx2, yup)
        c.line(cx2, yup, cx2, ytop)
        c.setDash()
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(colors.HexColor("#2b6cb0"))
        c.drawCentredString((cx1 + cx2) / 2, yup + 0.1 * cm, "TCP / MyAppGameProtocol")


def code(txt):
    safe = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(safe.replace("\n", "<br/>"), CODE)


def build():
    doc = SimpleDocTemplate(OUT, pagesize=A4, topMargin=2 * cm,
                            bottomMargin=1.8 * cm, leftMargin=2.2 * cm,
                            rightMargin=2.2 * cm)
    S = []

    # Portada
    S += [Spacer(1, 5 * cm),
          Paragraph("Pong en Red", TITLE),
          Spacer(1, 0.3 * cm),
          Paragraph("Documentacion del codigo y del protocolo", SUB),
          Spacer(1, 0.2 * cm),
          Paragraph("Proyecto N1 - Internet: Arquitectura y Protocolos", SUB),
          Spacer(1, 6 * cm),
          Paragraph("Arquitectura cliente/servidor - Sockets Berkeley (TCP)", SUB),
          Paragraph("Servidor en C  -  Cliente en Python (Tkinter)", SUB),
          PageBreak()]

    # 1. Introduccion
    S += [Paragraph("1. Introduccion", H1),
          Paragraph(
              "Este proyecto implementa el clasico juego <b>Pong</b> en red, con una "
              "arquitectura <b>cliente/servidor</b>. El servidor mantiene el estado del "
              "juego y comunica a los clientes mediante un protocolo binario propio, "
              "<b>MyAppGameProtocol</b>, que corre sobre TCP usando la API de Sockets "
              "Berkeley. El servidor esta escrito en <b>C</b> (requisito del enunciado) y "
              "el cliente en <b>Python</b> con Tkinter, por lo que corre igual en Windows y Mac.", BODY),
          Paragraph("Decisiones principales", H2),
          Paragraph(
              "<b>TCP (SOCK_STREAM):</b> se elige porque los comandos del juego (registro, "
              "movimientos, marcador) no se pueden perder ni desordenar; TCP garantiza "
              "entrega confiable y en orden.<br/>"
              "<b>Protocolo binario:</b> los mensajes viajan como bytes crudos (no texto), "
              "tal como pide el enunciado.<br/>"
              "<b>Arquitectura desacoplada:</b> cada responsabilidad (red, protocolo, "
              "logica de juego, interfaz) vive en su propio archivo.", BODY)]

    # 2. Arquitectura (UML de componentes)
    S += [Paragraph("2. Arquitectura desacoplada (Diagrama de componentes)", H1),
          Paragraph(
              "El protocolo no sabe nada del juego ni de los sockets: solo convierte "
              "mensajes en bytes y viceversa. Esto permite cambiar una capa sin tocar las "
              "otras. El siguiente diagrama muestra los modulos y como se comunican.", BODY),
          Spacer(1, 0.3 * cm),
          ComponentDiagram(),
          Paragraph("Figura 1. Componentes del servidor (C) y del cliente (Python).", CAP)]

    # 3. El protocolo
    S += [PageBreak(),
          Paragraph("3. MyAppGameProtocol (protocolo propio y binario)", H1),
          Paragraph("3.1 Formato del mensaje", H2),
          Paragraph(
              "Todo mensaje tiene una cabecera fija de 3 bytes seguida de un payload de "
              "tamano variable:", BODY),
          Spacer(1, 0.2 * cm),
          MessageFormat(),
          Paragraph("Figura 2. Formato binario del mensaje.", CAP),
          Paragraph(
              "<b>type</b> (1 byte): tipo de mensaje. <b>length</b> (2 bytes, big-endian): "
              "tamano del payload. <b>payload</b>: los datos, cuyo contenido depende del tipo.", BODY),
          Paragraph("3.2 Vocabulario de mensajes", H2)]

    tabla = [["Tipo", "Nombre", "Direccion", "Para que sirve"],
             ["1", "REGISTER", "Cliente -> Servidor", "Enviar nickname y email"],
             ["2", "WELCOME", "Servidor -> Cliente", "Asignar numero de jugador (1 o 2)"],
             ["3", "WAITING", "Servidor -> Cliente", "Esperando al otro jugador"],
             ["4", "START", "Servidor -> Cliente", "La partida empieza"],
             ["5", "INPUT", "Cliente -> Servidor", "Mover paleta (arriba/abajo/quieto)"],
             ["6", "STATE", "Servidor -> Cliente", "Estado: pelota, paletas y marcador"],
             ["7", "GAMEOVER", "Servidor -> Cliente", "Fin de partida y ganador"],
             ["8", "ERROR", "Servidor -> Cliente", "Reportar un error"]]
    t = Table(tabla, colWidths=[1.2 * cm, 2.6 * cm, 4.2 * cm, 6.5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3c6e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#aaaaaa")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef3f8")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    S += [t,
          Paragraph("Tabla 1. Vocabulario de mensajes de MyAppGameProtocol.", CAP),
          Paragraph("3.3 Payload de STATE (10 bytes)", H2),
          Paragraph(
              "ball_x (2) + ball_y (2) + paddle1_y (2) + paddle2_y (2) + score1 (1) + "
              "score2 (1). Las coordenadas usan un tablero logico de 640 x 480.", BODY)]

    # 4. Reglas de procedimiento (UML de secuencia)
    S += [PageBreak(),
          Paragraph("4. Reglas de procedimiento (Diagrama de secuencia)", H1),
          Paragraph(
              "El siguiente diagrama muestra el intercambio de mensajes desde que los dos "
              "jugadores se conectan hasta que termina la partida.", BODY),
          Spacer(1, 0.2 * cm),
          SequenceDiagram(),
          Paragraph("Figura 3. Secuencia de mensajes entre clientes y servidor.", CAP)]

    # 5. Explicacion del codigo
    S += [PageBreak(),
          Paragraph("5. Explicacion del codigo por seccion", H1),

          Paragraph("5.1 protocol.c / protocol.py - Codec binario", H2),
          Paragraph(
              "Convierte mensajes en bytes y viceversa. En C, <b>proto_send</b> arma la "
              "cabecera byte a byte y <b>proto_recv</b> la reconstruye. En Python se usa "
              "<b>struct.pack('&gt;BH', ...)</b> (B=1 byte, H=2 bytes, &gt;=big-endian).", BODY),
          code(">>> C (armar la cabecera)\n"
               "header[0] = type;                 // tipo\n"
               "header[1] = (length >> 8) & 0xFF;  // byte alto\n"
               "header[2] = length & 0xFF;         // byte bajo\n\n"
               ">>> Python (empaquetar en binario)\n"
               "struct.pack('>BH', msg_type, len(payload)) + payload"),

          Paragraph("5.2 game.c - Logica del juego", H2),
          Paragraph(
              "Contiene solo las reglas de Pong (mover paletas, rebotes, marcador). No sabe "
              "nada de red ni de bytes, por eso es facil de probar y explicar.", BODY),
          code("g->ball_x += g->ball_vx;   // mover la pelota\n"
               "g->ball_y += g->ball_vy;\n"
               "if (g->ball_y <= 0 || g->ball_y >= BOARD_H)\n"
               "    g->ball_vy = -g->ball_vy;   // rebote arriba/abajo"),

          Paragraph("5.3 server.c - Red y concurrencia", H2),
          Paragraph(
              "Crea el socket TCP (socket/bind/listen/accept), atiende a cada cliente en un "
              "hilo, empareja jugadores y corre el game loop de cada partida. Soporta varias "
              "parejas jugando en paralelo gracias a los hilos (pthreads).", BODY),
          code("./server <PORT> <LogFile>     # como se ejecuta\n"
               "server_fd = socket(AF_INET, SOCK_STREAM, 0);\n"
               "bind(...); listen(...); accept(...);\n"
               "pthread_create(&t, NULL, client_thread, ca);  // un hilo por cliente"),

          Paragraph("5.4 logger.c - Registro de eventos", H2),
          Paragraph(
              "Imprime cada evento en consola y lo guarda en el archivo de log con fecha y "
              "hora. Usa un mutex para que los hilos no mezclen sus lineas.", BODY),

          Paragraph("5.5 Cliente Python (net.py, ui.py, client.py)", H2),
          Paragraph(
              "<b>net.py</b> maneja la conexion (enviar/recibir por el socket). "
              "<b>ui.py</b> dibuja el juego con Tkinter y captura las teclas (flechas o W/S). "
              "<b>client.py</b> pide nickname/email, se registra y abre la ventana.", BODY)]

    # 6. Ejecucion
    S += [Paragraph("6. Como ejecutar", H1),
          Paragraph("Servidor (compilar y correr):", BODY),
          code("cd server\nmake\n./server 5000 pong.log"),
          Paragraph("Cliente (en cada maquina Windows/Mac con Python 3):", BODY),
          code("cd client\npython client.py <IP_DEL_SERVIDOR> 5000"),
          Paragraph(
              "Se abren dos clientes para jugar una partida. Controles: flechas o teclas W / S. "
              "El despliegue en AWS esta detallado en docs/AWS_DEPLOY.md.", BODY)]

    # 7. Conclusiones
    S += [Paragraph("7. Conclusiones", H1),
          Paragraph(
              "TCP encaja con Pong porque garantiza entrega y orden de los comandos. Separar "
              "red, protocolo, logica y logging hace el codigo corto, mantenible y facil de "
              "explicar. Un protocolo binario con cabecera [tipo][longitud] es simple de "
              "codificar en C y en Python, y los hilos permiten atender varias parejas de "
              "jugadores de forma concurrente.", BODY),
          Paragraph("8. Referencias", H1),
          Paragraph(
              "Beej's Guide to Network Programming - https://beej.us/guide/bgnet/<br/>"
              "TCP Server-Client en C - geeksforgeeks.org/tcp-server-client-implementation-in-c<br/>"
              "Pong (Wikipedia) - https://en.wikipedia.org/wiki/Pong", BODY)]

    doc.build(S)
    print("PDF generado en:", OUT)


if __name__ == "__main__":
    build()
