# Project Structure - Visual Guide

## 📁 Complete File Tree

```
video_indexer_project/
│
├── 📄 index_videos.py                    ← RUN THIS! Main entry point
├── 📄 README.md                          ← Full documentation
│
├── 📂 core/                              ← Core System Modules
│   ├── 📄 __init__.py
│   ├── 📄 data_models.py                 ← Data structures (ScoreMetrics, VideoSegment)
│   ├── 📄 video_reader.py                ← Video I/O operations
│   ├── 📄 segment_processor.py           ← Aggregates frame metrics
│   └── 📄 metrics_manager.py             ← Coordinates all metrics
│
└── 📂 metrics/                           ← Individual Metrics (FULLY MODULAR!)
    ├── 📄 __init__.py                    ← Package initialization
    ├── 📄 base_metric.py                 ← Base class for all metrics
    ├── 📄 sharpness_metric.py            ← 🔍 Sharpness calculation
    ├── 📄 brightness_metric.py           ← ☀️ Brightness calculation
    ├── 📄 contrast_metric.py             ← 🎨 Contrast calculation
    ├── 📄 color_vibrancy_metric.py       ← 🌈 Color saturation
    ├── 📄 motion_metric.py               ← 🏃 Motion detection
    ├── 📄 composition_metric.py          ← 📐 Composition quality
    └── 📄 person_detection_metric.py     ← 👤 Person detection + centering
```

---

## 🔄 Data Flow Diagram

```
                    index_videos.py
                           |
                    (Main Orchestrator)
                           |
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    video_reader    segment_processor  data_models
           │               │               │
           │               ▼               │
           │       metrics_manager         │
           │               │               │
           │               ▼               │
           │        ┌──────┴──────┐       │
           │        │             │       │
           │        ▼             ▼       │
           │   Individual    Individual   │
           │    Metric 1      Metric 2    │
           │        │             │       │
           └────────┴─────────────┴───────┘
                           │
                           ▼
                    JSON Index File
```

---

## 🎯 Module Responsibilities

### **index_videos.py** (Main Script)
```
┌─────────────────────────────────┐
│   Main Orchestrator             │
├─────────────────────────────────┤
│ • Parse command-line arguments  │
│ • Initialize VideoIndexer       │
│ • Coordinate indexing process   │
│ • Save JSON output              │
└─────────────────────────────────┘
```

### **core/video_reader.py**
```
┌─────────────────────────────────┐
│   Video I/O Operations          │
├─────────────────────────────────┤
│ • Open video files              │
│ • Read metadata (fps, duration) │
│ • Extract frames                │
│ • Iterate through segments      │
└─────────────────────────────────┘
```

### **core/segment_processor.py**
```
┌─────────────────────────────────┐
│   Metric Aggregation            │
├─────────────────────────────────┤
│ • Sample frames (every 3rd/6th) │
│ • Call metrics_manager          │
│ • Average scores                │
│ • Return ScoreMetrics object    │
└─────────────────────────────────┘
```

### **core/metrics_manager.py**
```
┌─────────────────────────────────┐
│   Metrics Coordinator           │
├─────────────────────────────────┤
│ • Load all metric modules       │
│ • Provide unified interface     │
│ • Call individual metrics       │
│ • Return calculated scores      │
└─────────────────────────────────┘
```

### **metrics/*.py** (Individual Metrics)
```
┌─────────────────────────────────┐
│   Single Metric Calculation     │
├─────────────────────────────────┤
│ • Inherit from BaseMetric       │
│ • Implement calculate() method  │
│ • Return score 0.0 to 1.0       │
│ • Self-contained logic          │
└─────────────────────────────────┘
```

---

## 🔌 How Metrics Are Loaded

```
1. index_videos.py starts
        ↓
2. Creates SegmentProcessor
        ↓
3. SegmentProcessor creates MetricsManager
        ↓
4. MetricsManager imports from metrics/__init__.py
        ↓
5. metrics/__init__.py imports all individual metrics:
   - from .sharpness_metric import SharpnessMetric
   - from .brightness_metric import BrightnessMetric
   - from .contrast_metric import ContrastMetric
   - ... etc ...
        ↓
6. MetricsManager instantiates all metrics:
   self.metrics = {
       'sharpness': SharpnessMetric(),
       'brightness': BrightnessMetric(),
       ...
   }
        ↓
7. Ready to calculate!
```

---

## ➕ Adding a New Metric - Visual Guide

```
Step 1: Create File
📂 metrics/
   └── 📄 my_new_metric.py    ← CREATE THIS
       
       class MyNewMetric(BaseMetric):
           def calculate(self, frame):
               # Your calculation
               return score

─────────────────────────────────

Step 2: Register in __init__
📂 metrics/
   └── 📄 __init__.py          ← EDIT THIS
       
       from .my_new_metric import MyNewMetric
       __all__ = [..., 'MyNewMetric']

─────────────────────────────────

Step 3: Add to Data Model
📂 core/
   └── 📄 data_models.py       ← EDIT THIS
       
       @dataclass
       class ScoreMetrics:
           ...
           my_new_score: float = 0.0  # ADD

─────────────────────────────────

Step 4: Register in Manager
📂 core/
   └── 📄 metrics_manager.py   ← EDIT THIS
       
       self.metrics = {
           ...
           'my_new': MyNewMetric(),  # ADD
       }

─────────────────────────────────

Step 5: Use in Processor
📂 core/
   └── 📄 segment_processor.py ← EDIT THIS
       
       my_scores = []
       for frame in frames:
           score = manager.calculate_my_new(frame)
           my_scores.append(score)
       metrics.my_new_score = np.mean(my_scores)

─────────────────────────────────

Step 6: Done! ✅
Run: python3 index_videos.py videos/ index.json
```

---

## 🎨 Metric Inheritance Hierarchy

```
                  BaseMetric
                  (Abstract)
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
  SharpnessMetric  BrightnessMetric  ...
        │             │             │
        └─────────────┴─────────────┘
                      │
              All implement:
              • calculate()
              • get_description()
              • get_name()
```

---

## 📦 Import Dependencies

```
index_videos.py
    ├── imports: core.data_models
    ├── imports: core.video_reader
    └── imports: core.segment_processor
                      └── imports: core.metrics_manager
                                       └── imports: metrics.*
                                                    └── inherits: metrics.base_metric
```

**No circular dependencies!** Clean hierarchy from top to bottom.

---

## 🚀 Execution Flow (Step by Step)

```
1️⃣  User runs:
    $ python3 index_videos.py videos/ index.json

2️⃣  index_videos.py main():
    - Parse arguments
    - Create VideoIndexer(segment_duration=1.0)

3️⃣  VideoIndexer.__init__():
    - Create SegmentProcessor()

4️⃣  SegmentProcessor.__init__():
    - Create MetricsManager()

5️⃣  MetricsManager.__init__():
    - Load all metrics from metrics/ folder
    - Create instances: SharpnessMetric(), BrightnessMetric(), etc.

6️⃣  VideoIndexer.index_folder():
    - Find all video files
    - For each video: call index_video()

7️⃣  VideoIndexer.index_video():
    - Create VideoReader(video_path)
    - Iterate through segments

8️⃣  For each segment:
    - VideoReader extracts frames
    - SegmentProcessor.process_segment(frames)

9️⃣  SegmentProcessor.process_segment():
    - For each frame (sampled):
        - Call MetricsManager.calculate_sharpness(frame)
        - Call MetricsManager.calculate_brightness(frame)
        - ... etc for all metrics ...
    - Average all scores
    - Return ScoreMetrics object

🔟 MetricsManager.calculate_*():
    - Call specific metric's calculate() method
    - Return score (0.0 to 1.0)

1️⃣1️⃣ Build index structure:
    - Collect all VideoSegments
    - Create IndexMetadata
    - Save to JSON

1️⃣2️⃣ Done! ✅
```

---

## 📊 File Size Comparison

```
metrics/
├── sharpness_metric.py         (~2 KB)  ← Small, focused
├── brightness_metric.py        (~2 KB)  ← Easy to understand
├── contrast_metric.py          (~2 KB)  ← Simple to modify
├── color_vibrancy_metric.py    (~2 KB)  ← Quick to test
├── motion_metric.py            (~3 KB)  ← Self-contained
├── composition_metric.py       (~3 KB)  ← Independent
└── person_detection_metric.py  (~5 KB)  ← Isolated logic

Total: ~19 KB of metric code

Compare to monolithic:
metrics_calculator.py           (~15 KB)  ← Hard to navigate
                                          ← Harder to modify
                                          ← All or nothing
```

**Modular = Better!**

---

## 🎯 Quick Reference

| Want to... | Edit this file |
|------------|----------------|
| Add new metric | `metrics/new_metric.py` + update 4 files |
| Modify metric calculation | `metrics/specific_metric.py` |
| Change sampling rate | `core/segment_processor.py` |
| Add metric field | `core/data_models.py` |
| Change video I/O | `core/video_reader.py` |
| Modify aggregation | `core/segment_processor.py` |

---

## ✨ Benefits Visualization

```
Monolithic Approach:
┌─────────────────────────────────────────┐
│                                         │
│   All Metrics in One Giant File         │
│                                         │
│   • Hard to navigate (500+ lines)       │
│   • Risky to modify (break others)      │
│   • Difficult to test individually      │
│   • Merge conflicts                     │
│                                         │
└─────────────────────────────────────────┘

Modular Approach:
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Metric 1│ │Metric 2│ │Metric 3│ │Metric 4│
│        │ │        │ │        │ │        │
│ ~50    │ │ ~50    │ │ ~50    │ │ ~50    │
│ lines  │ │ lines  │ │ lines  │ │ lines  │
└────────┘ └────────┘ └────────┘ └────────┘
    ✓          ✓          ✓          ✓
  Easy      Safe to   Test solo   No merge
  to find   modify    possible    conflicts
```

---

This modular structure makes the entire system more **maintainable**, **extensible**, and **understandable**!
