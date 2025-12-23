# GitHub Spark Prompt for Mask Stabilization Frontend

## Application Overview

Create a web application for video mask stabilization that allows users to upload videos, perform segmentation, apply stabilization methods, and visualize results with metrics.

## Core Features

### 1. Video Upload Section
- File upload component accepting video files (.mp4, .avi, .mov)
- Display uploaded video preview
- Show video metadata (resolution, FPS, frame count)
- Upload button that sends video to API: `POST /api/upload`

### 2. Segmentation Configuration
- Dropdown to select target class:
  - Options: "person", "car", "bus", "truck", "boat", "cat", "dog", "horse", "sheep", "cow", "background (all objects)"
- Button to start segmentation: `POST /api/segment`
- Progress indicator showing segmentation status
- Poll status endpoint: `GET /api/status/{job_id}`

### 3. Stabilization Controls
- Method selector with radio buttons:
  - Moving Average
  - Median Filter  
  - Exponential Smoothing
- Parameter inputs:
  - For Moving Average/Median: Window Size slider (3-9, step 2, default 5)
  - For Exponential Smoothing: Alpha slider (0.1-0.9, step 0.1, default 0.3)
- Apply button: `POST /api/stabilize`

### 4. Results Visualization
- Frame viewer with:
  - Frame number slider/selector
  - Three panels showing:
    1. Original frame
    2. Mask before stabilization
    3. Mask after stabilization
  - Or single panel showing comparison image
- Image endpoint: `GET /api/frames/{job_id}/{frame_type}/{frame_num}`
  - frame_type: "mask_before", "mask_after", "comparison"

### 5. Metrics Dashboard
- Fetch metrics: `GET /api/metrics/{job_id}`
- Display key metrics:
  - Mean IoU before/after
  - Instability score reduction
  - Improvement percentage
- Interactive line chart showing:
  - IoU scores over frame transitions
  - Before (red line) vs After (green line)
  - X-axis: Frame transition number
  - Y-axis: IoU score (0-1)
- Summary cards with:
  - Mean IoU improvement
  - Instability reduction percentage
  - Processing method used

### 6. Status and Feedback
- Global status indicator showing current processing stage:
  - "Ready", "Uploading", "Segmenting", "Stabilizing", "Complete", "Error"
- Progress bar with percentage
- Toast notifications for success/error messages

## UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Mask Stabilization System                          [v1.0]  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Upload Section]                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 📁 Drop video here or click to upload               │   │
│  │    Accepted: .mp4, .avi, .mov                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Video Info: 1920x1080, 30fps, 150 frames                   │
│                                                              │
│  [Segmentation]                                              │
│  Target Class: [Dropdown: person ▾]  [Segment Video]        │
│                                                              │
│  [Stabilization]                                             │
│  Method: ◉ Moving Average  ◯ Median Filter  ◯ Exp Smooth    │
│  Window Size: [━━●━━━━━] 5                                   │
│  [Apply Stabilization]                                       │
│                                                              │
│  [Progress]                                                  │
│  Status: Segmenting... [████████░░░░░░░░] 60%               │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  [Results]                                                   │
│                                                              │
│  Frame: [◀] 25 / 150 [▶]                                    │
│  ┌───────────┬────────────────┬────────────────┐            │
│  │ Original  │ Before Stabil. │ After Stabil.  │            │
│  │           │                │                │            │
│  │  [Image]  │    [Image]     │    [Image]     │            │
│  │           │                │                │            │
│  └───────────┴────────────────┴────────────────┘            │
│                                                              │
│  [Metrics]                                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  IoU Over Time                                      │    │
│  │  1.0 ┤                                              │    │
│  │      ├─────╱╲─────                                  │    │
│  │  0.8 ┤────╱  ╲────                                  │    │
│  │      │   ╱    ╲                                     │    │
│  │  0.6 ┤──╱      ╲───                                 │    │
│  │      └──────────────────────────                    │    │
│  │       0    25   50   75  100  125  150              │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  📊 Mean IoU: 0.923 → 0.967 (+4.8%)                         │
│  📉 Instability: 0.077 → 0.033 (-57.1%)                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## API Integration

Base URL: `http://localhost:8000` (configurable)

### Endpoints to use:

1. **Upload Video**
   ```
   POST /api/upload
   Content-Type: multipart/form-data
   Body: { file: <video file> }
   Returns: { job_id, status, video_info }
   ```

2. **Get Classes**
   ```
   GET /api/classes
   Returns: { "0": "background", "15": "person", ... }
   ```

3. **Start Segmentation**
   ```
   POST /api/segment
   Body: { job_id, target_class }
   Returns: { job_id, status, message }
   ```

4. **Apply Stabilization**
   ```
   POST /api/stabilize
   Body: { job_id, method, window_size?, alpha? }
   Returns: { job_id, status, message }
   ```

5. **Check Status**
   ```
   GET /api/status/{job_id}
   Returns: { job_id, status, progress, message }
   ```

6. **Get Metrics**
   ```
   GET /api/metrics/{job_id}
   Returns: { iou_before, iou_after, improvement, ... }
   ```

7. **Get Frame**
   ```
   GET /api/frames/{job_id}/{frame_type}/{frame_num}
   Returns: Image file
   ```

## Styling Guidelines

- Use a clean, modern design
- Color scheme:
  - Primary: Blue (#2563eb)
  - Success: Green (#10b981)
  - Warning: Orange (#f59e0b)
  - Error: Red (#ef4444)
- Responsive layout
- Clear visual hierarchy
- Loading states for async operations
- Smooth transitions

## User Flow

1. User uploads a video
2. System shows video preview and metadata
3. User selects target segmentation class (optional)
4. User clicks "Segment Video"
5. Progress bar shows segmentation progress
6. Once complete, user selects stabilization method and parameters
7. User clicks "Apply Stabilization"
8. Results display with before/after comparison
9. Metrics chart shows improvement
10. User can navigate through frames to see stabilization effect

## Additional Features

- Download stabilized masks button
- Reset/clear current job
- Multiple job comparison (advanced)
- Export metrics as CSV/JSON
- Share results via link

## Technical Notes

- Poll status endpoint every 1-2 seconds during processing
- Show loading spinners during API calls
- Handle errors gracefully with user-friendly messages
- Cache frame images to avoid repeated requests
- Pre-load adjacent frames for smooth navigation
- Debounce parameter changes to avoid excessive API calls

## Error Handling

- Invalid video format: "Please upload a valid video file"
- Segmentation failed: "Segmentation failed. Please try again or use a different video"
- Network error: "Connection error. Please check your connection and try again"
- No results: "Complete segmentation and stabilization first to see results"

---

## Prompt for GitHub Spark

**Copy the text below to create the app in GitHub Spark:**

Create a video mask stabilization web application with the following features:

1. Video upload with drag-and-drop, supporting .mp4, .avi, .mov files
2. Video preview showing resolution, FPS, and frame count
3. Segmentation controls with class selection dropdown (person, car, etc.) 
4. Stabilization method selector (Moving Average, Median Filter, Exponential Smoothing)
5. Parameter sliders (window size 3-9 for MA/Median, alpha 0.1-0.9 for Exponential)
6. Three-panel frame viewer showing original, before stabilization, after stabilization
7. Frame navigation slider to browse through video frames
8. Interactive line chart showing IoU scores before/after over time
9. Metrics dashboard displaying mean IoU, instability reduction, improvement percentage
10. Real-time progress tracking with status indicator and progress bar

Connect to API at http://localhost:8000 with these endpoints:
- POST /api/upload (multipart/form-data)
- POST /api/segment (JSON: job_id, target_class)
- POST /api/stabilize (JSON: job_id, method, window_size, alpha)
- GET /api/status/{job_id}
- GET /api/metrics/{job_id}
- GET /api/frames/{job_id}/{frame_type}/{frame_num}

Style: Modern, clean design with blue primary color, responsive layout, smooth transitions. Include loading states, error handling with toast notifications, and status polling every 2 seconds during processing.
