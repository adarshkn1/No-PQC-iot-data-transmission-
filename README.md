# RabbitMQ Client-Server with Docker & Wireshark Inspection

This project demonstrates sending random data from a Python client to a Python server via RabbitMQ running in Docker, and provides explicit instructions for sniffing and inspecting raw AMQP payload data in Wireshark.

---

## 🛠️ Project Structure

- **`docker-compose.yml`**: Docker service definition for RabbitMQ 3 (with Management Plugin).
- **`server.py`**: Python script that connects to RabbitMQ and consumes messages from `random_data_queue`.
- **`client.py`**: Python script that generates random telemetry JSON payloads and publishes them to `random_data_queue`.
- **`README.md`**: Guide for execution and Wireshark raw packet analysis.

---

## 🚀 Step 1: Start RabbitMQ in Docker

Ensure Docker Desktop is running on your machine, then launch RabbitMQ using:

```bash
docker compose up -d
```

Verify that the container is up and running:

```bash
docker ps
```

> **RabbitMQ Access Points:**
> - **AMQP Protocol (Unencrypted)**: `localhost:5672`
> - **Management Dashboard**: [http://localhost:15672](http://localhost:15672) (Login: `guest` / `guest`)

---

## 💻 Step 2: Run the Server and Client

### 1. Start the Server (Consumer)
Open a terminal and start the server script. It will listen for incoming messages on `random_data_queue`:

```bash
python server.py
```

### 2. Start the Client (Producer)
Open a **second** terminal and run the client script to begin transmitting random data:

```bash
# Send 10 messages (default):
python client.py

# Or send 25 messages:
python client.py 25

# Or run in continuous loop mode:
python client.py continuous
```

---

## 🔍 Step 3: Wireshark Guide for Raw Data Inspection

Because RabbitMQ uses plain AMQP 0-9-1 over TCP port `5672` without TLS encryption, the message body is sent directly in cleartext.

### 1. Select the Capture Interface in Wireshark
1. Open **Wireshark**.
2. Since both Client and Server connect to `localhost:5672` on Windows:
   - Double-click on **`Adapter for loopback traffic capture`** (Npcap Loopback Adapter) or **`vEthernet (WSL / Docker)`**.

### 2. Apply Display Filter
In the top display filter bar in Wireshark, enter:
```wireshark
amqp
```
or
```wireshark
tcp.port == 5672
```
Press **Enter**.

### 3. Locate and Inspect Raw Message Data
1. Run `python client.py` to send packets while Wireshark is capturing.
2. In Wireshark, look for packets with the Info column showing **`Basic.Publish`** (Client to Server) or **`Content Body`**.
3. Click on a **`Basic.Publish`** or **`Content Body`** packet.
4. In the middle pane (Packet Details):
   - Expand **Advanced Message Queuing Protocol 0-9-1**.
   - Expand **Content Body**.
   - Click on the **Payload** byte field.
5. In the bottom pane (Packet Bytes), you will clearly see the **raw unencrypted JSON text** sent by the client (e.g. `{"event_id": "...", "timestamp": "...", "metrics": {...}}`).

### 4. Alternative: Follow TCP Stream
- Right-click any packet in the Wireshark list -> **Follow** -> **TCP Stream**.
- A new window will pop up showing the full ASCII stream of AMQP header handshakes and the plain text JSON payload!

---

## 🧹 Cleanup

To stop and remove the RabbitMQ Docker container:

```bash
docker compose down
```
