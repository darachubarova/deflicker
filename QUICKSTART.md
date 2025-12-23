# Quick Start Guide

**Автор:** Чубарова Дарья Алексеевна

This guide will help you get the Mask Stabilization system up and running quickly.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- (Optional) CUDA-capable GPU for faster processing

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/darachubarova/defliker.git
cd mask-stabilization
```

### 2. Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

**Note:** Installing PyTorch may take several minutes depending on your system.

### 3. Verify Installation

```bash
python verify_structure.py
```

You should see all checks passing.

## Running the System

### Option 1: API Server

Start the FastAPI server:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at `http://localhost:8000`

Visit `http://localhost:8000/docs` for interactive API documentation.

### Option 2: Jupyter Notebook

Start Jupyter and open the analysis notebook:

```bash
jupyter notebook notebooks/analysis.ipynb
```

### Option 3: Docker

Build and run with Docker:

```bash
docker-compose up --build
```

## Testing the API

### 1. Check Server Status

```bash
curl http://localhost:8000/
```

### 2. Get Available Classes

```bash
curl http://localhost:8000/api/classes
```

### 3. Upload a Video

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@examples/your_video.mp4"
```

Save the `job_id` from the response.

### 4. Start Segmentation

```bash
curl -X POST "http://localhost:8000/api/segment" \
  -H "Content-Type: application/json" \
  -d '{"job_id": "YOUR_JOB_ID", "target_class": "person"}'
```

### 5. Check Status

```bash
curl "http://localhost:8000/api/status/YOUR_JOB_ID"
```

### 6. Apply Stabilization

```bash
curl -X POST "http://localhost:8000/api/stabilize" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "YOUR_JOB_ID",
    "method": "moving_average",
    "window_size": 5
  }'
```

### 7. Get Metrics

```bash
curl "http://localhost:8000/api/metrics/YOUR_JOB_ID"
```

### 8. Download Frame

```bash
curl "http://localhost:8000/api/frames/YOUR_JOB_ID/comparison/0" \
  --output comparison_frame_0.png
```

## Using the Frontend

Create a web interface using GitHub Spark:

1. Go to GitHub Spark
2. Copy the content from `spark_frontend/SPARK_PROMPT.md`
3. Paste it into GitHub Spark
4. The web UI will be generated automatically
5. Configure it to connect to your API server

## Common Issues

### CUDA Out of Memory

If you encounter GPU memory issues:

1. Reduce batch size in segmentation
2. Use CPU mode by setting device='cpu'
3. Process fewer frames at once

### Module Not Found Errors

Make sure you're in the virtual environment:

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Reinstall dependencies:

```bash
pip install -r requirements.txt
```

### Port Already in Use

If port 8000 is already in use:

```bash
uvicorn src.main:app --port 8001
```

## Next Steps

1. **Place test videos** in the `examples/` directory
2. **Explore the notebook** for detailed analysis
3. **Read the full README** for comprehensive documentation
4. **Try different methods** and parameters to see their effects

## Getting Help

- Check the main README.md for detailed documentation
- Review the API docs at `http://localhost:8000/docs`
- Open an issue on GitHub for bugs or questions

## Workflow Example

Complete workflow from start to finish:

1. Start the API server
2. Upload a video file
3. Wait for upload confirmation
4. Start segmentation (specify target class if needed)
5. Poll status until segmentation completes
6. Apply stabilization method with desired parameters
7. View results and metrics
8. Download comparison images
9. Analyze improvements using the metrics

---

**Estimated Time:** 
- Setup: 5-10 minutes
- First video processing: 1-5 minutes (depends on video length and hardware)
- Analysis: As needed

**Enjoy using the Mask Stabilization System!** 🎉
