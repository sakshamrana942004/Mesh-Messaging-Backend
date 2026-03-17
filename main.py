from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS (important)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Store users with names
connections = {}
user_count = 0


# -------------------
# WebSocket
# -------------------

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    global user_count

    await websocket.accept()

    # assign unique name
    user_count += 1
    username = f"Node {user_count}"

    connections[websocket] = username

    # notify join
    for conn in connections:
        await conn.send_json({
            "type": "info",
            "message": f"{username} joined"
        })

    try:
        while True:

            data = await websocket.receive_text()

            # broadcast message with name
            for conn in connections:
                await conn.send_json({
                    "type": "chat",
                    "message": f"{username}: {data}"
                })

    except WebSocketDisconnect:

        left_user = connections[websocket]
        del connections[websocket]

        for conn in connections:
            await conn.send_json({
                "type": "info",
                "message": f"{left_user} left"
            })