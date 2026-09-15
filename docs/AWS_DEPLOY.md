# Desplegar el servidor Pong en AWS (AWS Academy)

El **servidor** corre en la nube (una instancia EC2 con Linux) y los **clientes**
se conectan a su IP pública desde Windows o Mac.

## 1. Crear la instancia EC2

1. Entra a AWS Academy → **Learner Lab** → *Start Lab* → abre la consola de AWS.
2. Ve a **EC2** → *Launch Instance*.
3. Elige **Amazon Linux 2023** (o Ubuntu), tipo **t2.micro** (capa gratuita).
4. En **Key pair**, crea o selecciona una llave `.pem` para conectarte por SSH.

## 2. Abrir el puerto del juego (Security Group)

En el *Security Group* de la instancia agrega una regla **inbound**:

| Tipo       | Protocolo | Puerto | Origen     |
|------------|-----------|--------|------------|
| Custom TCP | TCP       | 5000   | 0.0.0.0/0  |

> Usa el mismo puerto con el que arrancas el servidor.

## 3. Subir el código y compilar

Conéctate por SSH y clona el repositorio:

```bash
ssh -i tu-llave.pem ec2-user@<IP_PUBLICA>

sudo yum install -y git gcc make        # (Ubuntu: sudo apt install -y git gcc make)
git clone <URL_DE_TU_REPO>
cd Pong/server
make
```

## 4. Ejecutar el servidor

```bash
./server 5000 pong.log
```

Para dejarlo corriendo aunque cierres la sesión SSH:

```bash
nohup ./server 5000 pong.log &
```

## 5. Conectar los clientes

En cada máquina (Windows / Mac) con Python 3:

```bash
cd client
python client.py <IP_PUBLICA_EC2> 5000
```

Abre dos clientes (pueden estar en máquinas distintas) para jugar una partida.
