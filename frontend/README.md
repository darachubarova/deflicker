# Mask Stabilization Frontend

A clean, modern HTML/CSS/JS frontend for the mask stabilization API.

## Features

- **Drag-and-drop video upload** with support for MP4, AVI, and MOV files
- **Configuration options** for object class selection and stabilization methods
- **Real-time progress tracking** with status updates
- **Interactive frame viewer** with navigation controls
- **Metrics display** showing IoU improvements and stabilization results
- **Responsive design** that works on different screen sizes

## Usage

### Quick Start

1. **Start the API server:**
   ```bash
   cd /path/to/mask-stabilization
   uvicorn src.main:app --host 0.0.0.0 --port 8000
   ```

2. **Open the frontend:**
   - Simply open `index.html` in a web browser, or
   - Serve it with a simple HTTP server:
     ```bash
     cd frontend
     python -m http.server 8080
     ```
   - Then navigate to `http://localhost:8080/index.html`

### Workflow

1. **Upload a Video**: Drag and drop or click to browse for a video file
2. **Configure Settings**:
   - Select object class (person, car, bus, truck, dog, cat, horse)
   - Choose stabilization method (Moving Average, Median Filter, Exponential Smoothing)
   - Adjust parameters (window size or alpha)
3. **Stabilize**: Click the "STABILIZE VIDEO" button
4. **View Results**: Navigate through frames and view metrics

## Technical Details

### API Integration

The frontend communicates with the API at `http://localhost:8000` using the following endpoints:

- `POST /api/upload` - Upload video file
- `POST /api/segment` - Start segmentation process
- `POST /api/stabilize` - Apply stabilization
- `GET /api/status/{job_id}` - Poll processing status
- `GET /api/metrics/{job_id}` - Retrieve metrics
- `GET /api/results/{job_id}` - Get results summary
- `GET /api/frames/{job_id}/{frame_type}/{frame_num}` - Fetch frame images

### Design

- **Color Scheme**: 
  - Primary: #3182ce (blue)
  - Success: #38a169 (green)
  - Gradient background: Purple gradient
- **Layout**: Card-based with max-width of 900px
- **Typography**: System fonts for optimal performance
- **Animations**: Smooth transitions and hover effects

## Browser Compatibility

Works with modern browsers that support:
- ES6 JavaScript
- CSS Grid and Flexbox
- Fetch API
- HTML5 File API

Tested on:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## File Structure

```
frontend/
├── index.html          # Single-file frontend (includes CSS and JS)
└── README.md          # This file
```

## Configuration

To change the API base URL, edit the `API_BASE` constant in the JavaScript section:

```javascript
const API_BASE = 'http://localhost:8000';
```

## Troubleshooting

**CORS Issues**: If you encounter CORS errors, ensure the API server has CORS middleware configured (already included in `src/main.py`).

**API Not Responding**: Verify the API server is running on port 8000.

**Upload Fails**: Check that the video file format is supported (MP4, AVI, MOV) and the file size is reasonable.
