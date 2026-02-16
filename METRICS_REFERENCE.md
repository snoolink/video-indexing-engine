# Complete Metrics Reference

## 📊 All Available Metrics (Default Enabled)

The video indexer now includes **15 basic metrics** + **27 cinematic metrics** = **42 total metrics** calculated for each segment!

---

## 🎨 Basic Visual Metrics (8 metrics)

| Metric | Field Name | Range | Description |
|--------|-----------|-------|-------------|
| **Sharpness** | `sharpness` | 0.0-1.0 | Image focus quality using Laplacian variance |
| **Brightness** | `brightness` | 0.0-1.0 | Lighting level in LAB color space |
| **Contrast** | `contrast` | 0.0-1.0 | Visual definition using std deviation |
| **Color Vibrancy** | `color_vibrancy` | 0.0-1.0 | Color saturation in HSV space |
| **Motion Score** | `motion_score` | 0.0-1.0 | Amount of movement using optical flow |
| **Composition** | `composition_score` | 0.0-1.0 | Edge distribution and rule of thirds |
| **Person Score** | `person_score` | 0.0-1.0 | Person detection quality (HOG+SVM) |
| **Center Focus** | `center_focus_score` | 0.0-1.0 | Person centering in frame |

---

## 🎬 Cinematic Metrics (27 metrics)

### Camera Movement (4 metrics)

| Metric | Field Name | Type/Range | Description |
|--------|-----------|------------|-------------|
| **Movement Type** | `camera_movement_type` | String | Pan Left/Right, Tilt Up/Down, Zoom In/Out, Dolly In/Out, Rotation, Static, Handheld, Complex |
| **Movement Quality** | `camera_movement_quality` | 0.0-1.0 | Cinematic quality of movement |
| **Movement Smoothness** | `camera_movement_smoothness` | 0.0-1.0 | How smooth the movement is |
| **Movement Confidence** | `camera_movement_confidence` | 0.0-1.0 | Detection confidence level |

**Movement Types Detected:**
- Static
- Pan Left / Pan Right
- Tilt Up / Tilt Down
- Zoom In / Zoom Out
- Dolly In / Dolly Out
- Rotation CW / Rotation CCW
- Handheld/Shake
- Complex Movement

---

### Stabilization (2 metrics)

| Metric | Field Name | Type/Range | Description |
|--------|-----------|------------|-------------|
| **Stabilization Type** | `stabilization_type` | String | tripod, gimbal, handheld_stabilized, handheld_unstabilized, unknown |
| **Stabilization Score** | `stabilization_score` | 0.0-1.0 | Quality of stabilization |

**Stabilization Types:**
- **Tripod** (95%+ stability) - Locked off, static
- **Gimbal** (85-95%) - Smooth stabilized movement
- **Handheld Stabilized** (70-85%) - IBIS/OIS enabled
- **Handheld Unstabilized** (<70%) - Shaky footage

---

### Focus & Depth of Field (4 metrics)

| Metric | Field Name | Type/Range | Description |
|--------|-----------|------------|-------------|
| **Has Focus Change** | `focus_has_change` | Boolean | Rack focus detected |
| **Focus Change Amount** | `focus_change_amount` | Float | Percentage of focus shift |
| **Focus Sharpness** | `focus_sharpness` | Float | Current sharpness level |
| **Has Bokeh** | `focus_has_bokeh` | Boolean | Shallow depth of field detected |

---

### Lighting (3 metrics)

| Metric | Field Name | Type/Range | Description |
|--------|-----------|------------|-------------|
| **Lighting Type** | `lighting_type` | String | golden_hour, blue_hour, high_key, low_key, natural, backlit, three_point, motivated |
| **Lighting Quality** | `lighting_quality` | 0.0-1.0 | Overall lighting score |
| **Is Dramatic** | `lighting_is_dramatic` | Boolean | High contrast dramatic lighting |

**Lighting Types:**
- **Golden Hour** - Warm, soft, cinematic
- **Blue Hour** - Cool twilight
- **High Key** - Bright, low contrast
- **Low Key** - Dark, dramatic, high contrast
- **Natural** - Daylight, even
- **Backlit** - Silhouettes, rim lighting
- **Three Point** - Studio lighting setup
- **Motivated** - Realistic light sources

---

### Color Grading (4 metrics)

| Metric | Field Name | Type/Range | Description |
|--------|-----------|------------|-------------|
| **Grading Style** | `color_grading_style` | String | warm, cool, teal_orange, desaturated, vibrant, monochrome, vintage, neutral |
| **Grading Strength** | `color_grading_strength` | 0.0-1.0 | How strong the grading is |
| **Saturation** | `color_saturation` | Float | Average saturation level |
| **Warmth** | `color_warmth` | Float | Color temperature (warm/cool) |

**Grading Styles:**
- **Warm** - Golden, sunset tones
- **Cool** - Blue/teal tones
- **Teal-Orange** - Hollywood cinematic look
- **Desaturated** - Muted, cinematic
- **Vibrant** - Saturated, colorful
- **Monochrome** - Black and white
- **Vintage** - Film-like aesthetic
- **Neutral** - No strong grading

---

### Exposure (3 metrics)

| Metric | Field Name | Type/Range | Description |
|--------|-----------|------------|-------------|
| **Exposure Quality** | `exposure_quality` | String | properly_exposed, underexposed, overexposed |
| **Exposure Score** | `exposure_score` | 0.0-1.0 | Overall exposure quality |
| **Is Well Exposed** | `exposure_is_well_exposed` | Boolean | Proper exposure without clipping |

---

### Shot Framing (3 metrics)

| Metric | Field Name | Type/Range | Description |
|--------|-----------|------------|-------------|
| **Framing Type** | `shot_framing_type` | String | extreme_close_up, close_up, medium, wide, extreme_wide, insert |
| **Composition Score** | `shot_composition_score` | 0.0-1.0 | Overall composition quality |
| **Follows Rule of Thirds** | `shot_follows_rule_of_thirds` | Boolean | Subject follows rule of thirds |

**Shot Types:**
- **Extreme Close-Up** (ECU) - Face details
- **Close-Up** (CU) - Head and shoulders
- **Medium Shot** (MS) - Waist up
- **Wide Shot** (WS) - Full body
- **Extreme Wide** (EWS) - Establishing shot
- **Insert** - Object detail

---

## 📈 Total Metrics Summary

```
Basic Metrics:        8
Cinematic Metrics:   27
─────────────────────────
TOTAL:               42 metrics per segment!
```

---

## 🎯 Usage Examples

### Search by Camera Movement
```python
# Find all smooth dolly shots
segments = search_index(
    camera_movement_type="Dolly In",
    camera_movement_smoothness_min=0.75
)
```

### Search by Lighting Style
```python
# Find golden hour footage
segments = search_index(
    lighting_type="golden_hour",
    lighting_quality_min=0.7
)
```

### Search by Color Grading
```python
# Find teal-orange cinematic look
segments = search_index(
    color_grading_style="teal_orange",
    color_grading_strength_min=0.6
)
```

### Search by Multiple Criteria
```python
# Find high-quality cinematic shots
segments = search_index(
    camera_movement_type="Dolly In",
    stabilization_type="gimbal",
    exposure_is_well_exposed=True,
    shot_framing_type="medium",
    lighting_type="golden_hour"
)
```

---

## 🔍 Index JSON Structure

Each segment in the index now contains:

```json
{
  "video_file": "video1.mp4",
  "start_time": 10.5,
  "end_time": 11.5,
  "duration": 1.0,
  "metrics": {
    "sharpness": 0.85,
    "brightness": 0.92,
    "contrast": 0.78,
    "color_vibrancy": 0.83,
    "motion_score": 0.45,
    "composition_score": 0.89,
    "person_score": 0.75,
    "center_focus_score": 0.82,
    
    "camera_movement_type": "Dolly In",
    "camera_movement_quality": 0.88,
    "camera_movement_smoothness": 0.92,
    "camera_movement_confidence": 0.85,
    
    "stabilization_type": "gimbal",
    "stabilization_score": 0.89,
    
    "focus_has_change": false,
    "focus_change_amount": 2.3,
    "focus_sharpness": 1250.5,
    "focus_has_bokeh": true,
    
    "lighting_type": "golden_hour",
    "lighting_quality": 0.91,
    "lighting_is_dramatic": false,
    
    "color_grading_style": "warm",
    "color_grading_strength": 0.78,
    "color_saturation": 145.2,
    "color_warmth": 142.8,
    
    "exposure_quality": "properly_exposed",
    "exposure_score": 0.94,
    "exposure_is_well_exposed": true,
    
    "shot_framing_type": "medium",
    "shot_composition_score": 0.87,
    "shot_follows_rule_of_thirds": true
  }
}
```

---

## 🚀 Performance

**Cinematic metrics are calculated every 6th frame** (vs every 3rd for basic metrics) to balance:
- Accuracy (capturing cinematic qualities)
- Performance (not every frame)
- Index size (reasonable JSON file size)

**For a 1-second segment at 30fps:**
- Basic metrics: ~10 frame samples
- Cinematic metrics: ~5 frame samples
- Total processing: ~1-2 seconds per segment

---

## 💡 Tips

1. **Camera Movement** is great for finding dynamic shots
2. **Stabilization** helps filter professional vs amateur footage
3. **Lighting Type** perfect for mood-based searches
4. **Color Grading** finds consistent aesthetic styles
5. **Exposure** ensures technical quality
6. **Shot Framing** helps match specific shot compositions

All metrics work together to provide comprehensive video quality assessment!
