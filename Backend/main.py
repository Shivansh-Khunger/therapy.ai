# Import fastapi modules
import logging
from fastapi import FastAPI, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn

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

async def process_video(frames):
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))
    with mp_pose.Pose(min_detection_confidence = 0.5, min_tracking_confidence = 0.5) as pose:
        for frame in frames:
            frame_np = np.frombuffer(frame, dtype=np.uint8)
            decoded_frame = cv2.imdecode(frame_np, flags=1)
            
            # Recolor frame to RGB
            decoded_frame = cv2.cvtColor(decoded_frame, cv2.COLOR_BGR2RGB)
            decoded_frame.flags.writeable = False
            
            # Make detection
            results = pose.process(decoded_frame)
            
            # Recolor back to BGR
            decoded_frame.flags.writeable = True
            decoded_frame    = cv2.cvtColor(decoded_frame,cv2.COLOR_RGB2BGR)
            
            # Render detections
            mp_drawing.draw_landmarks(decoded_frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            # Encode the processed frame to JPEG
            ret, buffer = cv2.imencode('.jpg', decoded_frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
    # Release resources
    out.release()
        

@app.post("/process_video/")
async def process_video_endpoint(frames: bytes, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_video, frames.split(b'--frame\r\n'))
    return StreamingResponse(process_video(frames.split(b'--frame\r\n')), media_type="multipart/x-mixed-replace; boundary=frame")
         

if __name__ == "__main__":

    # Needed for app to hotreload
    logging.basicConfig(level=logging.INFO)
    uvicorn.run("main:app", host="0.0.0.0", port=9080, reload=True)