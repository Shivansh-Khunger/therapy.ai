# Import fastapi modules
import logging
import os
import time
from fastapi import FastAPI, File, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import base64

# Import machine learning mudules
import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Define fastapi app
app = FastAPI()

# Allow all origins (for development purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def process_frame(frame_base64):
    frame = base64.b64decode(frame_base64)
    with mp_pose.Pose(
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    ) as pose:
        frame_np = np.frombuffer(frame, dtype=np.uint8)
        decoded_frame = cv2.imdecode(frame_np, flags=1)

        # Get original dimensions
        height, width, _ = decoded_frame.shape
        aspect_ratio = width / height

        # Resize frame for processing
        decoded_frame = cv2.resize(decoded_frame, (640, int(640 / aspect_ratio)))

        # Recolor frame to RGB
        decoded_frame = cv2.cvtColor(decoded_frame, cv2.COLOR_BGR2RGB)
        decoded_frame.flags.writeable = False

        # Make detection
        results = pose.process(decoded_frame)

        # Recolor back to BGR
        decoded_frame.flags.writeable = True
        decoded_frame = cv2.cvtColor(decoded_frame, cv2.COLOR_RGB2BGR)

        # Render detections
        mp_drawing.draw_landmarks(
            decoded_frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
        )

        # Encode the processed frame to JPEG
        ret, buffer = cv2.imencode(".jpg", decoded_frame)
        frame_bytes = buffer.tobytes()

        # Save the processed frame to a file
        filename = f"processed_images/{time.time()}.jpg"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            f.write(buffer)

        # Convert the processed frame to base64
        frame_base64 = base64.b64encode(frame_bytes).decode()

        return frame_base64


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            processed_frame = await process_frame(data)
            await websocket.send_bytes(processed_frame)
    except WebSocketDisconnect:
        # Handle disconnection
        print("Client disconnected")


if __name__ == "__main__":
    try:
        # Needed for app to hotreload
        logging.basicConfig(level=logging.INFO)
        uvicorn.run("main:app", host="0.0.0.0", port=9080, reload=True)
    finally:
        quit
