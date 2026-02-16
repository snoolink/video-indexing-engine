```# Video Indexer - Modular Metrics System

## 📁 Project Structure

```
video_indexer_project/
├── index_videos.py              # Main entry point (run this!)
├
── core/                         # Core system modules
│   ├── data_models.py           # Data structures (ScoreMetrics, VideoSegment, etc.)
│   ├── video_reader.py          # Video file I/O operations
│   ├── segment_processor.py     # Aggregates metrics from frames
│   └── metrics_manager.py       # Coordinates all metric calculations
│
├── metrics/                     # Individual metric modules (FULLY MODULAR!)
│   ├── __init__.py              # Package initialization
│   ├── base_metric.py           # Base class for all metrics
│   ├── sharpness_metric.py      # Sharpness calculation
│   ├── brightness_metric.py     # Brightness calculation
│   ├── contrast_metric.py       # Contrast calculation
│   ├── color_vibrancy_metric.py # Color saturation calculation
│   ├── motion_metric.py         # Motion detection
│   ├── composition_metric.py    # Composition quality
│   └── person_detection_metric.py # Person detection + centering
│
└── utils/                       # Utility functions (future)
```

---

## 🎯 Key Features

### **1. Fully Modular Metrics**
- Each metric is in its own file
- Add new metrics by creating a new file
- Remove metrics by deleting the file
- Modify metrics without touching others

### **2. Clean Architecture**
```
index_videos.py (main)
    ↓
core/metrics_manager.py (coordinator)
    ↓
metrics/*.py (individual calculations)
```

### **3. Easy to Extend**
Adding a new metric takes 3 simple steps (see below)

---

## 🚀 Quick Start

### Installation
```bash
pip install opencv-python numpy --break-system-packages
```

### Basic Usage
```bash
# Navigate to project directory
cd video_indexer_project/

# Index your videos
python3 index_videos.py path/to/videos/ output_index.json

# With custom segment duration
python3 index_videos.py path/to/videos/ output_index.json -d 0.5
```

---

## 📊 Available Metrics

Each metric is in its own file and completely independent:

| Metric | File | What it Measures |
|--------|------|------------------|
| **Sharpness** | `sharpness_metric.py` | Image focus using Laplacian variance |
| **Brightness** | `brightness_metric.py` | Lighting quality in LAB color space |
| **Contrast** | `contrast_metric.py` | Visual definition using std deviation |
| **Color Vibrancy** | `color_vibrancy_metric.py` | Color saturation in HSV space |
| **Motion** | `motion_metric.py` | Movement using optical flow |
| **Composition** | `composition_metric.py` | Edge distribution (rule of thirds) |
| **Person Detection** | `person_detection_metric.py` | Person presence and centering (HOG+SVM) |

---

## ➕ How to Add a New Metric

### Example: Adding a Face Detection Metric

### **Step 1: Create the Metric File**
Create `metrics/face_detection_metric.py`:

```python
"""
Face Detection Metric

Detects faces in frames using Haar Cascade.
"""

import cv2
import numpy as np
from .base_metric import BaseMetric


class FaceDetectionMetric(BaseMetric):
    """
    Detect faces and score based on size.
    
    Range: 0.0 (no face) to 1.0 (optimal face size)
    """
    
    def __init__(self):
        super().__init__()
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def calculate(self, frame: np.ndarray, **kwargs) -> float:
        """Calculate face detection score"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return 0.0
        
        # Score based on largest face
        h, w = frame.shape[:2]
        largest_face = max(faces, key=lambda f: f[2] * f[3])
        face_area = largest_face[2] * largest_face[3]
        frame_area = h * w
        
        coverage = face_area / frame_area
        return min(coverage / 0.2, 1.0)
    
    def get_description(self) -> str:
        return "Detects faces using Haar Cascade classifier"
```

### **Step 2: Register in `metrics/__init__.py`**
Add import and export:

```python
from .face_detection_metric import FaceDetectionMetric

__all__ = [
    # ... existing metrics ...
    'FaceDetectionMetric',  # ADD THIS
]
```

### **Step 3: Add to `core/data_models.py`**
Add field to `ScoreMetrics` dataclass:

```python
@dataclass
class ScoreMetrics:
    # ... existing fields ...
    face_score: float = 0.0  # ADD THIS
```

### **Step 4: Register in `core/metrics_manager.py`**
Add to `__init__` and create convenience method:

```python
from metrics import FaceDetectionMetric  # Import

class MetricsManager:
    def __init__(self):
        self.metrics = {
            # ... existing metrics ...
            'face_detection': FaceDetectionMetric(),  # ADD THIS
        }
    
    def calculate_face_detection(self, frame):
        """Calculate face detection metric"""
        return self.metrics['face_detection'].calculate(frame)
```

### **Step 5: Add to `core/segment_processor.py`**
Update `process_segment()` method:

```python
def process_segment(self, frames):
    # ... existing code ...
    face_scores = []
    
    for i, frame in enumerate(frames):
        if i % 6 == 0:  # Sample every 6th frame
            face_scores.append(
                self.metrics_manager.calculate_face_detection(frame)
            )
    
    metrics.face_score = np.mean(face_scores) if face_scores else 0.0
    return metrics
```

### **Step 6: Done!**
Re-run the indexer and your new metric is included:

```bash
python3 index_videos.py videos/ index.json
```

The metric will automatically:
- Be calculated for all segments
- Be stored in the JSON index
- Appear in the GUI sliders (if using search GUI)

---

## 🗑️ How to Remove a Metric

### Example: Removing Motion Metric

1. **Delete** `metrics/motion_metric.py`
2. **Remove** from `metrics/__init__.py`:
   ```python
   # Delete this line:
   from .motion_metric import MotionMetric
   ```
3. **Remove** from `core/data_models.py`:
   ```python
   # Delete this line:
   motion_score: float = 0.0
   ```
4. **Remove** from `core/metrics_manager.py`:
   ```python
   # Delete from __init__:
   'motion': MotionMetric(),
   
   # Delete the method:
   def calculate_motion(self, ...): ...
   ```
5. **Remove** from `core/segment_processor.py`:
   ```python
   # Delete motion calculation code
   ```

Done! The metric is completely removed.

---

## 🔧 How to Modify a Metric

Want to change how sharpness is calculated? Just edit `metrics/sharpness_metric.py`!

**Example:** Change sharpness normalization:

```python
# In metrics/sharpness_metric.py
def calculate(self, frame, **kwargs):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = laplacian.var()
    
    # CHANGE THIS LINE:
    self.typical_max = 2000.0  # Was 1000.0
    
    score = min(variance / self.typical_max, 1.0)
    return score
```

Save and re-index. That's it!

---

## 📋 Module Descriptions

### **core/data_models.py**
Data structures used throughout the system:
- `ScoreMetrics` - Container for all metric scores
- `VideoSegment` - Segment with timing and metrics
- `VideoMetadata` - Video file metadata
- `IndexMetadata` - Index metadata

### **core/video_reader.py**
Handles all video I/O:
- Read video metadata (fps, duration, resolution)
- Read segments by frame or time
- Iterate through all segments
- Find videos in folder

### **core/segment_processor.py**
Processes segments:
- Aggregates frame-level metrics into segment scores
- Handles frame sampling (every 3rd, every 6th, etc.)
- Returns ScoreMetrics for each segment

### **core/metrics_manager.py**
Coordinates all metrics:
- Loads all metric modules
- Provides unified interface
- Calculates all metrics for a frame

### **metrics/base_metric.py**
Base class for all metrics:
- Defines common interface
- Provides utility methods (normalize, etc.)
- All metrics inherit from this

### **metrics/*.py**
Individual metric calculations:
- Each file is independent
- Inherits from BaseMetric
- Implements `calculate()` method

---

## 🎨 Benefits of This Structure

### **1. Modularity**
- Each metric is completely independent
- Add/remove/modify without affecting others
- Easy to understand and maintain

### **2. Extensibility**
- Adding metrics is straightforward
- Clear patterns to follow
- No need to modify core logic

### **3. Testability**
- Test each metric independently
- Mock dependencies easily
- Isolate bugs quickly

### **4. Reusability**
- Use individual metrics in other projects
- Mix and match as needed
- Share metrics between projects

### **5. Collaboration**
- Different developers can work on different metrics
- Clear ownership of files
- Easier code reviews

---

## 🔍 Example: Testing a Single Metric

You can test metrics individually without running the whole system:

```python
# Test sharpness metric alone
from metrics.sharpness_metric import SharpnessMetric
import cv2

metric = SharpnessMetric()
frame = cv2.imread('test_image.jpg')
score = metric.calculate(frame)

print(f"Sharpness score: {score:.3f}")
print(f"Description: {metric.get_description()}")
```

---

## 📝 Folder Purpose Summary

| Folder | Purpose | Add Files Here? |
|--------|---------|-----------------|
| `core/` | Core system functionality | Rarely (new system features) |
| `metrics/` | Individual metric calculations | **YES!** (add new metrics) |
| `utils/` | Helper functions | YES (utilities) |
| root | Main entry point | NO (keep clean) |

---

## 🚦 Workflow

```
1. User runs: python3 index_videos.py videos/ index.json
                    ↓
2. index_videos.py loads core modules
                    ↓
3. core/segment_processor.py initializes metrics_manager
                    ↓
4. core/metrics_manager.py loads ALL metrics from metrics/
                    ↓
5. For each video segment:
   - video_reader extracts frames
   - segment_processor calls metrics_manager
   - metrics_manager calls each metric's calculate()
   - Results aggregated into ScoreMetrics
                    ↓
6. All segments saved to JSON index
```

---

## 💡 Design Patterns

- **Strategy Pattern**: Each metric is a strategy
- **Factory Pattern**: MetricsManager creates metrics
- **Template Method**: BaseMetric defines interface
- **Single Responsibility**: Each file does one thing
- **Open/Closed**: Open for extension, closed for modification

---

## 📦 Dependencies

- **opencv-python** - Video processing and CV algorithms
- **numpy** - Numerical computations
- **Python 3.7+** - Dataclasses, type hints

---

## 🎯 Common Tasks

### Add a new metric
1. Create `metrics/my_metric.py`
2. Update `metrics/__init__.py`
3. Add to `core/data_models.py`
4. Register in `core/metrics_manager.py`
5. Use in `core/segment_processor.py`

### Remove a metric
1. Delete `metrics/my_metric.py`
2. Remove from all files above

### Modify sampling rate
Edit `core/segment_processor.py`:
```python
if i % 3 == 0:  # Change to % 5 for every 5th frame
```

### Change metric calculation
Edit the specific `metrics/metric_name.py` file

---

## 🔗 Related Files

- `video_search_gui.py` - Phase 2: Search interface (separate)
- `README_NEW_SYSTEM.md` - Overall system documentation
- `QUICKSTART.md` - Quick start guide

---

## ✨ Summary

This modular structure makes it incredibly easy to:
- ✅ Add new metrics (just create a new file!)
- ✅ Remove metrics (just delete the file!)
- ✅ Modify metrics (edit one file!)
- ✅ Test metrics (run individually!)
- ✅ Understand the system (clear organization!)

**The metrics/ folder is your playground - add as many metrics as you want!**
```