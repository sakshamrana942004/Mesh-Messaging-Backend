from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connections = []

# -------------------
# LoRa Setup
# -------------------

LORA_CONNECTED = False

try:
    import meshtastic
    import meshtastic.serial_interface
    from pubsub import pub

    interface = meshtastic.serial_interface.SerialInterface()

    if interface:
        LORA_CONNECTED = True
        print("LoRa device connected")

except Exception as e:

    interface = None
    print("LoRa not connected:", e)


# -------------------
# Receive LoRa
# -------------------

if LORA_CONNECTED:

    def onReceive(packet, interface):

        try:

            text = packet["decoded"]["payload"].decode("utf-8")

            import asyncio

            for conn in connections:
                asyncio.create_task(
                    conn.send_json({
                        "type":"lora",
                        "message":text
                    })
                )

        except:
            pass

    pub.subscribe(onReceive, "meshtastic.receive")


# -------------------
# WebSocket
# -------------------

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()
    connections.append(websocket)

    try:

        while True:

            data = await websocket.receive_text()

            # broadcast to dashboard
            for conn in connections:

                await conn.send_json({
                    "type":"chat",
                    "message":data
                })

            # send to LoRa only if device connected
            if LORA_CONNECTED and interface:

                try:
                    interface.sendText(data)
                except Exception as e:
                    print("LoRa send failed:", e)

    except WebSocketDisconnect:

        connections.remove(websocket)
        print("Client disconnected")