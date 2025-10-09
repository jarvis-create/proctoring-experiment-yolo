import asyncio
from fastapi import APIRouter, status, HTTPException
from loggers import routelogger
from fastapi import UploadFile, File
from ultralytics import YOLO
from utils import get_file_url
from tempfile import NamedTemporaryFile
from pathlib import Path
import shutil
from concurrent.futures import ThreadPoolExecutor

model = YOLO("yolov8n.pt")
executor = ThreadPoolExecutor(max_workers=4)



def run_yolo_predict(model, source):
    return model.predict(source=source, conf=0.3, save=False)

router = APIRouter()

@router.get('/get')
async def hello_world():
    return {"Hello": "World"}


@router.post('/analyze', tags=['Analyze'])
async def analyze_r2_image(file: UploadFile = File(...)):

    file_url = get_file_url(file)

    routelogger.info(f"route url is {file_url}")



    results = model.predict(file_url, conf=0.3, save=True)
   
    detections = []

    for r in results:
        boxes = r.boxes
        for box in boxes:
            b = box.xyxy[0].tolist()  # get box coordinates in (top, left, bottom, right) format
            c = box.cls
            detections.append({
                "class": model.names[int(c)],
                "confidence": float(box.conf),
                # "bbox": [float(coord) for coord in b]
            })

    # Analyze detections
    phone_detected =  any(d["class"] == "remote" or d["class"] == "cell phone" for d in detections)
    faces = [d for d in detections if d["class"] == "person"]
    face_detected = len(faces) > 0
    multiple_faces_detected = len(faces) > 1

    return {
        "phone_detected": phone_detected,
        "face_detected": face_detected,
        "multiple_faces_detected": multiple_faces_detected,
        "looking_away": False,
        "results": detections,
    }

    

@router.post('/analyze_local_image', tags=['Analyze'])
async def analyze_local_image(file: UploadFile = File(...)):
    routelogger.info('Starting analyze_image function')

    if not file.content_type.startswith('image/'):
        routelogger.error('Uploaded file is not an image.')
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    try:
        with NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        routelogger.info(f"Temporary file saved at {tmp_path}")
    except Exception as e:
        routelogger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to process the uploaded file.")

    try:
        model = YOLO("yolov8n.pt")
        routelogger.info("YOLO model loaded successfully.")

        results = model.predict(source=tmp_path, conf=0.3, save=True)
        routelogger.info("YOLO prediction completed.")

        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                b = box.xyxy[0].tolist()  # box coordinates
                c = box.cls
                detections.append({
                    "class": model.names[int(c)],
                    "confidence": float(box.conf),
                    # "bbox": [float(coord) for coord in b]
                })

        # Analyze detections
        phone_detected = any(d["class"] in ["remote", "cell phone"] for d in detections)
        faces = [d for d in detections if d["class"] == "person"]
        face_detected = len(faces) > 0
        multiple_faces_detected = len(faces) > 1

        routelogger.info("Detection analysis completed.")

        return {
            "phone_detected": phone_detected,
            "face_detected": face_detected,
            "multiple_faces_detected": multiple_faces_detected,
            "looking_away": False,
            "results": detections,
        }

    except Exception as e:
        routelogger.error(f"Error during YOLO prediction: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze the image.")

    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
            routelogger.info(f"Temporary file {tmp_path} deleted.")
        except Exception as e:
            routelogger.warning(f"Failed to delete temporary file {tmp_path}: {e}")


@router.post('/analyze_image_efficicient',tags=['Analyze'])

async def efficiently_analyze_image(file: UploadFile = File()):

    try:
        with NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        routelogger.info(f"Temporary file saved at {tmp_path}")
    except Exception as e:
        routelogger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to process the uploaded file.")

    loop = asyncio.get_event_loop()

    results = await loop.run_in_executor(executor, run_yolo_predict, model, tmp_path)

    detections = []
    for r in results:
        boxes = r.boxes
        for box in boxes:
            b = box.xyxy[0].tolist()
            c = box.cls
            detections.append({
                "class": model.names[int(c)],
                "confidence": float(box.conf),
            })

    phone_detected = any(d["class"] in ["remote", "cell phone"] for d in detections)
    faces = [d for d in detections if d["class"] == "person"]
    face_detected = len(faces) > 0
    multiple_faces_detected = len(faces) > 1

    return {
        "phone_detected": phone_detected,
        "face_detected": face_detected,
        "multiple_faces_detected": multiple_faces_detected,
        "looking_away": False,
        "results": detections,
    }





