# Import fastapi modules
import logging
import os
import time
import json
from fastapi import FastAPI, File, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import base64

# Import machine learning mudules
import cv2
import mediapipe as mp
import numpy as np

# Import modules for webrtc
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
from av import VideoFrame
import asyncio

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

exercise_list = [
    "wand_exercise"
]

async def calculate_angle(a,b,c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
    return angle

class FrameProcessor(VideoStreamTrack):
    kind = "video"

    def __init__(self):
        super().__init__()  # don't forget this!
        self.queue = asyncio.Queue()

    async def recv(self):
        frame = await self.queue.get()

        # Process the frame
        img = frame.to_ndarray(format="bgr24")

        # Process the frame with MediaPipe here
        # ...
        frame = process_frame(img)

        return frame
    
async def process_frame(frame):
    # frame = base64.b64decode(frame_base64)
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
        
                # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark
            
            # Get coordinates
            shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
            
            # Calculate angle
            angle = await calculate_angle(shoulder, elbow, wrist)

            cv2.putText(decoded_frame, str(angle), 
                           tuple(np.multiply(elbow, [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA
                                )
                       
        except:
            pass

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


# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             data = await websocket.receive_text()
#             processed_frame = await process_frame(data)
#             await websocket.send_bytes(processed_frame)
#     except WebSocketDisconnect:
#         # Handle disconnection
#         print("Client disconnected")

@app.post("/offer")
async def offer(offer: RTCSessionDescription):
    print("Offer received")
    pc = RTCPeerConnection()
    frame_processor = FrameProcessor()

    @pc.on("track")
    def on_track(track):
        print("Track received")
        @track.on("frame")
        async def on_frame(frame):  
            print("on_frame called")
            await frame_processor.queue.put(frame)

    await pc.setRemoteDescription(offer)
    for t in pc.getTransceivers():
        if t.kind == "video":
            pc.addTrack(frame_processor)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return RTCSessionDescription(sdp=pc.localDescription.sdp, type=pc.localDescription.type)

@app.get("/exercises")
async def exercise_list():
    return json.dumps(exercise_list)

if __name__ == "__main__":
    try:
        # Needed for app to hotreload
        logging.basicConfig(level=logging.INFO)
        uvicorn.run("main:app", host="0.0.0.0", port=9080, reload=True)
    finally:
        quit
