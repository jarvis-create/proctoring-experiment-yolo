# Online Exam Proctoring System

A comprehensive AI-powered online exam proctoring system built with **Nuxt.js** frontend and **FastAPI** backend, featuring real-time computer vision monitoring and automated cheating detection.

## 🔍 Features

### Real-time Monitoring
- **Face Detection & Recognition** - Monitors student presence and identity
- **Multiple Face Detection** - Alerts when unauthorized persons are detected
- **Phone/Object Detection** - Uses YOLO v8 to detect mobile phones and other prohibited objects
- **Gaze Tracking** - Monitors if students are looking away from the screen
- **Tab Switch Detection** - Detects when students switch to other applications or tabs

### Exam Management
- **Timed Exams** - Built-in countdown timer with customizable duration
- **Question Navigation** - Multiple choice questions with answer tracking
- **Warning System** - Real-time alerts for suspicious behavior
- **Video Stream** - Live camera feed with overlay detection visualization

### Technical Stack
- **Frontend**: Nuxt.js 3, Vue.js, Tailwind CSS, Face-api.js
- **Backend**: FastAPI, Python, YOLO v8 (Ultralytics)
- **Computer Vision**: Real-time object detection and face analysis
- **Real-time Communication**: RESTful API with image processing

## 🚀 Quick Start

### Prerequisites
- Node.js (v18+)
- Python (v3.12+)
- pnpm or npm

### Frontend Setup (Nuxt.js)
```bash
# Install dependencies
pnpm install

# Start development server
pnpm run dev
```
Frontend will be available at `http://localhost:3000`

### Backend Setup (FastAPI)
```bash
cd api/fastapi-detect

# Install dependencies (using uv)
uv sync

# Start the API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Backend will be available at `http://localhost:8000`

### API Documentation
Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📁 Project Structure

```
proctoring-exp/
├── components/
│   └── Proctor.vue          # Main exam interface component
├── api/
│   └── fastapi-detect/      # FastAPI backend
│       ├── main.py          # FastAPI app configuration
│       ├── routes.py        # API endpoints
│       ├── utils.py         # Utility functions
│       └── yolov8n.pt       # YOLO model weights
├── public/
│   └── models/              # Face-api.js ML models
├── app.vue                  # Root Vue component
├── nuxt.config.ts          # Nuxt configuration
└── package.json            # Frontend dependencies
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
SERVER_URL=http://localhost:8000
```

### CORS Configuration
The FastAPI backend is configured to allow requests from:
- `http://localhost:3000`
- `http://localhost:3001`
- `https://staging-proctor.test.com`

## 📊 API Endpoints

### Analysis Endpoints
- `POST /analyze` - Analyze uploaded image for proctoring violations
- `POST /analyze_local_image` - Analyze local image file
- `POST /analyze_image_efficient` - Efficient async image analysis

### Response Format
```json
{
  "phone_detected": false,
  "face_detected": true,
  "multiple_faces_detected": false,
  "looking_away": false,
  "results": [
    {
      "class": "person",
      "confidence": 0.95
    }
  ]
}
```

## 🎯 Detection Capabilities

### Supported Objects (YOLO v8)
- **Person detection** - Identifies human presence
- **Cell phone detection** - Detects mobile devices
- **Remote control detection** - Identifies remote controls
- **Custom object classes** - Extensible for additional objects

### Face Analysis (Face-api.js)
- Face detection and recognition
- Age and gender estimation
- Facial expression analysis
- Face landmark detection

## 🛡️ Security Features

- **Real-time monitoring** - Continuous camera feed analysis
- **Automated warnings** - Immediate alerts for violations
- **Tab switch detection** - Prevents external resource usage
- **Multi-face detection** - Prevents collaboration
- **Object detection** - Identifies prohibited items

## 🚀 Deployment

### Frontend (Nuxt.js)
```bash
# Build for production
pnpm run build

# Preview production build
pnpm run preview
```

### Backend (FastAPI)
```bash
# Using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000

# Using gunicorn for production
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [YOLO v8](https://github.com/ultralytics/ultralytics) for object detection
- [Face-api.js](https://github.com/justadudewhohacks/face-api.js) for face analysis
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Nuxt.js](https://nuxt.com/) for the frontend framework

---

**Note**: This system is designed for educational and assessment purposes. Ensure compliance with privacy laws and regulations in your jurisdiction before deployment.