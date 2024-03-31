# Import fastapi modules
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import logging
import uvicorn

# Import machine learning mudules
import cv2
import mediapipe as mp
from io import BytesIO

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
    
app = FastAPI()

@app.post("/process_video/")
async def process_video(video_file: UploadFile = File(...)):
    
    contents = await video_file.read()
    video_stream = BytesIO(contents)
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))
    
    cap = cv2.VideoCapture(video_stream)
    if not cap.isOpened():
        raise HTTPException(status_code=500, detail="Error opening video stream")

    with mp_pose.Pose(min_detection_confidence = 0.5, min_tracking_confidence = 0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False    
        
            # Make detection
            results = pose.process(image)
            
            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image,cv2.COLOR_RGB2BGR)
            
            # Render detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            out.write(image)
        
    cap.release()
    out.release()
    
    # Return the processed video stream as response
    with open('output.avi', 'rb') as f:
        video_data = f.read()

    return StreamingResponse(BytesIO(video_data), media_type="video/x-msvideo")    

if __name__ == "__main__":
    
    # Needed for app to hotreload
    logging.basicConfig(level=logging.INFO)
    uvicorn.run("main:app", host="0.0.0.0", port=9080, reload=True)