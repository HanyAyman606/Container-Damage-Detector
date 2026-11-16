# Container Damage Detection with Classical Computer Vision (no YOLO / no deep learning)

**Goal:** from camera frames of a container face, find **dents / bulges** and **holes / tears**, locate each one by element number (T / B / D), and report the total damaged area as a share of the face area. This covers 5 faces: top (roof), left side, right side, front end wall and door end, for 20 ft and 40 ft containers.

**Core idea:** a healthy corrugated wall is a **repeating structure** (278 mm pitch) lit by a known side light. Damage is anything that breaks the repetition of shape and shading.

**Status of this document:** version 2. It merges the earlier technical plan with the capture setup given by the task owner (350 mm frame, camera 1.4–1.7 m away, tilted side flash) and the reduced damage scope. Everything that is not confirmed is listed in section 9 (Open questions).

---

## 0. Damage scope

| Damage type (MarineInsight list) | In scope | Notes |
|---|---|---|
| 2. Dents and bulges (local deformation from impact) | **Yes** | Main target |
| 4. Holes and tears (full penetration of panels or seams) | **Yes** | Main target |
| 3. Corrosion and rust | **No (excluded)** | Not measured and not counted in the damage area |
| 5. Fractures and cracks | **No (not in the list given)** | The original task text says "fracture"; see open question D2 |
| 6. Door and seal failure | **No** | Not in the list given |
| 1. General damage definition | n/a | Definition only |

Consequences of the reduced scope:
- No color or texture analysis for rust is needed. Rust must only be **masked out** so it is not mistaken for a hole or dent.
- No hairline-crack detection, so the very fine pixel size (about 0.25 mm per pixel) once required for cracks is not needed. A hole or tear is much larger.

---

## 1. Reference geometry (side wall, checked against manufacturer build specs)

| Item | Value |
|---|---|
| Corrugation depth | 36 mm |
| Outer (top) flat, crest | 72 mm (70–75 mm range) |
| Inner (bottom) flat, trough | 70 mm (70–75 mm range) |
| Web (sloped flank), projected width | 68 mm each |
| **Web, true length** | **about 77 mm** = sqrt(68² + 36²) |
| **Web angle to the wall plane** | **about 28°** = atan(36 / 68) |
| **Pitch (one full cycle)** | **278 mm** = 70 + 68 + 72 + 68 (the "208 mm" sometimes quoted is only the rib width 68 + 72 + 68) |
| Cycle order | bottom flat (B), diagonal (D), top flat (T), diagonal (D) |
| 20 ft wall, internal length | about 5.90 m, about 21 cycles |
| 40 ft wall, internal length | about 12.03 m, about 43 cycles |
| Internal height | about 2,390 mm (standard) / 2,695 mm (high cube) |

Notes:
- The side-wall profile above is not valid for every face. The roof, the front end wall and the door panels use other profiles (the owner will complete these). The model must be selected per face.
- Typical counts per side wall: 20 ft: 20–21 top flats, 20–21 bottom flats, 40–42 diagonals; 40 ft: 42–43, 42–43 and 84–86.

---

## 2. Capture setup (given by the task owner) and what follows from it

### 2.1 What was stated

| Item | Stated value | Status |
|---|---|---|
| Camera frame (one "slice") | One top, two diagonals, two bottoms, or one bottom, two diagonals, two tops: about **350 mm** | Given |
| Frame tolerance | **±136 mm**, meaning up to two more diagonals framed or two fewer | Given (my reading, see 2.2) |
| Camera distance | **1.4 m to 1.7 m** from the wall | Given |
| Camera angle | **90°** to the wall | Given as an assumption |
| Lighting | Flash light at the side of the container, **tilted by an unknown angle** | Given, angle unknown |

### 2.2 Frame content

| Case | Width | Content |
|---|---|---|
| Nominal | 348–350 mm | T D B D T (72 + 68 + 70 + 68 + 72 = 350 mm) or B D T D B (70 + 68 + 72 + 68 + 70 = 348 mm) |
| Maximum | 486 mm (= 350 + 136) | for example D T D B D T D (68 + 72 + 68 + 70 + 68 + 72 + 68 = 486 mm), meaning a diagonal added at each end |
| Minimum | 214 mm (= 350 − 136) | about T D B (72 + 68 + 70 = 210 mm) plus slivers |

My reading: 136 mm is the width of two diagonals (2 × 68 mm), so the tolerance is about ±68 mm at each edge of the frame.

### 2.3 Consequences

| Topic | Result |
|---|---|
| Cycles per frame | 350 mm is 1.26 pitches. Frames of 350 mm or 486 mm contain at least one full cycle. A 214 mm frame does **not** (214 < 278 mm). |
| Coverage | If a frame can be as narrow as 214 mm, a step of 350 mm between frames can leave about 136 mm of wall unseen. To guarantee full coverage the step must be at most about 214 mm, so that even the narrowest frame overlaps the next one (a 200 mm step gives a small margin). |
| Field of view | A 350 mm frame subtends about 14.3° at 1.4 m and 11.8° at 1.7 m (a narrow field). |
| Scale variation | Distance changes by 1.7 / 1.4 = 1.21, so mm per pixel changes by about 21 % between the two extremes. |
| Relief parallax | The 36 mm corrugation depth changes magnification by 36 / 1,400 = 2.6 % (at 1.4 m) to 2.1 % (at 1.7 m) between crest and trough. This is small but not negligible for width measurements of 68–72 mm. |
| Pixel size | mm per pixel = frame width in mm ÷ width in pixels. Example: a 350 mm frame on 1,920 px is about 0.18 mm per pixel. The actual value depends on the camera resolution (open question A4). |
| Verticality of the view | The camera is "90° to the wall" only at the row at its own height. If the camera sits at mid-height of a 2.39 m wall and sees the full height, rays at the top and bottom edge are about 40° (1.4 m) or 35° (1.7 m) off the wall normal (44° and 38° for a high cube). A fixed camera that sees the whole height therefore **cannot** be at 90° everywhere. This is open question A1. |
| Position along the wall | A single frame cannot say which element number it shows, because the pattern repeats every 278 mm. The position along the wall must come from another source (open question C1). |

---

## 3. Lighting model (derived, to be confirmed)

Assumptions: light direction tilted by angle α from the wall normal, **in the horizontal plane across the vertical ribs** (the only tilt that changes shading between elements); webs are 28° from the wall plane; uniform paint; no mirror-like reflections; camera response linear.

| Surface | Relative brightness |
|---|---|
| Flats (top and bottom) | cos α |
| Web facing the light | cos(α − 28°) |
| Web facing away | cos(α + 28°) (dark, and fully self-shadowed when α > about 62°) |

| α (light tilt) | Brightness ratio lit web : away web | Cast shadow on the bottom flat |
|---|---|---|
| 30° | 1.9 | none |
| 45° | 3.3 | none |
| 60° | 24 | none |
| 62° | away web at zero | starts (shadow width = 36 · tan α − 68 mm) |
| 70° | away web fully dark | about 31 mm of the 70 mm flat |
| 75° | away web fully dark | about 66 mm of the 70 mm flat |
| 75.4° and above | away web fully dark | the whole 70 mm flat |

What this means:
- **Below about 60°** nothing in the pattern is in cast shadow. The two webs show a clear bright/dark pair and the dark web edges are easy to find.
- **Above about 62°** the away-facing web and part of each bottom flat go completely dark, which can hide a hole or a tear.
- **A dent or bulge** changes the local surface normal, so the brightness changes along the height of a strip and the web edges bend.
- **A hole or tear** shows as a dark void with a sharp border, often with bright torn edges.
- The light angle can in principle be **estimated from each frame** from the web-to-flat brightness ratio. This requires uniform paint and a calibrated camera, and is an assumption (open question B3).
- A tilt in the **vertical** direction (up or down) does not change the shading between ribs, but it changes shadows from rails and posts and the reach of the flash across the 2.4 m height.

---

## 4. Test results of my earlier prototype (what does and does not transfer)

I tested on 4 containers: blue 20 ft, brown 20 ft, white 40 ft, red 40 ft. Each wall was cut into overlapping partial photos of **5 to 11 pitches** with random gain, bias and noise, plus a second run with ±3 % scale jitter. Only the repeating pattern was used (no learned model).

**Caveats:**
- The "truth" was my own manual annotation, not an independent ground truth.
- Thresholds were tuned while working on the red 40 ft photo.
- Both 20 ft images and the white 40 ft image look like clean renders, with almost no scratches or dirt.
- The partial photos were exact crops of one image, which is easier than real photos.
- **A 350 mm frame holds only 1.26 pitches, so these results do not transfer.** Pitch estimation and overlap matching were done on frames with far more pattern.

### 4.1 Finding the repeating landmark in each partial photo

| Container | Landmarks found (recall) | Correct among detections (precision) | Mean position error (fraction of pitch) |
|---|---|---|---|
| red 40 ft | 100 % | 99 % | 0.02 |
| white 40 ft | 96 % | 97 % | 0.03 |
| blue 20 ft | 81 % | 95 % | 0.03 |
| brown 20 ft | 65 % | 100 % | 0.03 |

The same held with scale jitter. Pitch estimation was unreliable on some short blue-wall photos (mean error 7.7 %, a harmonic mix-up).

### 4.2 Chaining the photos and numbering the elements end to end

| Container | Landmarks found / truth (no jitter) | With ±3 % jitter | Overlap match margin |
|---|---|---|---|
| red 40 ft | 41 / 42 | 41 / 42 | 0.03–0.04 (best) |
| white 40 ft | 38 / 42 | 37 / 42 | about 0 (ambiguous) |
| brown 20 ft | 16 / 18 | 14 / 18 | about 0 (ambiguous) |
| blue 20 ft | 8 / 20 | 1 / 20 | about 0 (ambiguous) |

"Overlap match margin" is the correlation score of the best overlap minus the second best. A margin near 0 means the matcher cannot tell which period is correct.

Findings that still matter for 350 mm frames:
- **Clean walls break overlap matching** because shifts of exactly one pitch look identical. With 350 mm frames the overlap is smaller still, so absolute position must come from a separate source (section 2.3).
- **Start and stop of the wall** were found from the pattern (non-periodic band at the corner post, deep edge line at the post). This idea still holds for the first and last frames.
- **Text and labels near the post** broke the periodic score and must be masked.

---

## 5. Computer-vision principles needed (reduced to the current scope)

| # | Principle | What it is | Used for |
|---|---|---|---|
| 1 | Pinhole camera model, intrinsics / extrinsics | Maps 3D points to pixels | Scale, perspective, relief parallax |
| 2 | Lens distortion correction | Radial and tangential distortion removed using checkerboard calibration | Straight corrugation edges, accurate widths |
| 3 | **Homography** (planar perspective transform) | 3×3 matrix H with x' ~ Hx, from at least 4 point pairs, refined with RANSAC | Fronto-parallel view if the camera is not exactly 90° (essential for rows far from the camera axis) |
| 4 | Metric scale calibration | Known real size (278 mm pitch; 72 / 68 / 70 / 68 mm elements) gives mm per pixel | Converting pixel areas to mm² |
| 5 | Radiometric calibration | Linear camera response, flat-field correction, exposure normalisation | Reliable brightness ratios, light-angle estimate |
| 6 | Photometric model of the lit corrugation | Lambertian shading, brightness ∝ cos of angle between normal and light | Predicting normal shading; seeing dents as deviations |
| 7 | Shape-from-shading / photometric stereo | Surface orientation from brightness under known light | Dent / bulge depth (needs known or several lights) |
| 8 | Denoising and smoothing | Gaussian, median, bilateral | Noise suppression before edge work |
| 9 | Image gradients and edge detection | Sobel, Canny, sub-pixel edges | Web edges, tear borders |
| 10 | Line fitting and RANSAC | Robust fit despite outliers | Straightness of web edges; a dent bends them |
| 11 | **Periodicity analysis** | Autocorrelation, FFT, Gabor filters, local phase | Element phase inside a frame, pattern breaks |
| 12 | Template and correlation matching | Normalised cross-correlation, phase correlation | Frame-to-frame overlap |
| 13 | Feature detection and matching | SIFT / ORB / AKAZE, RANSAC | Overlap on non-periodic texture |
| 14 | Robust statistics | Median, MAD, trimmed estimates | "Normal pattern" model despite damaged strips |
| 15 | Pattern / background modelling | Median of same-type strips as reference, residual as anomaly | Dent and bulge detection |
| 16 | Thresholding and segmentation | Otsu, adaptive threshold, watershed | Dark voids (holes, tears), defect masks |
| 17 | Morphology | Opening, closing, dilation | Cleaning masks |
| 18 | Connected components and region analysis | Labelling, area, bounding box, shape | Grouping damaged pixels into defects, area |
| 19 | Motion blur and focus assessment | Laplacian-variance focus measure, exposure and shutter model | Rejecting unusable frames |
| 20 | Evaluation metrics | Precision, recall, IoU, area error | Proving the system works |
| 21 | Synthetic defect generation | Warp dents, draw holes and tears on clean images | Tuning thresholds when real labelled damage is scarce |

Removed from the earlier version: color-based rust detection, texture analysis for rust, and fine crack (ridge) filters, because corrosion and hairline cracks are out of scope.

---

## 6. Pipeline: every stage, what it needs, challenges, remedies

### Stage 0 — Capture protocol and quality gate
- **Goal:** frames that the later stages can use.
- **Needs:** camera at 1.4–1.7 m, as close to 90° to the wall as possible; side flash with a stable, known tilt; frames of 214–486 mm width with enough overlap (step at most about 214 mm); first frame includes the corner post and last frame includes the opposite post.
- **Challenges:** motion blur, glare or saturation from the flash, wrong exposure, distance drift, missed frames.
- **Remedies:** reject frames with low focus, saturated pixels or low contrast; log camera distance if a sensor is available; keep a frame counter or position record per frame.

### Stage 1 — Pre-processing
- **Methods:** lens distortion correction (one-time checkerboard calibration), flat-field and exposure normalisation, mild denoising.
- **Challenges:** flash falloff across the 2.4 m height; shading that looks like dents.
- **Remedies:** calibrate the flash falloff on a flat panel; keep brightness normalisation per row; do not over-smooth edges.

### Stage 2 — Wall isolation
- **Goal:** find the wall region and exclude posts, rails, ground and background.
- **Methods:** the periodic vertical stripes mark the wall; long horizontal lines mark the top and bottom rail.
- **Challenges:** a 350 mm frame may show only wall; posts and rails appear only at some rows.

### Stage 3 — Geometry (homography)
- **Goal:** make the wall fronto-parallel so strips are vertical and pixel size is the same everywhere.
- **Needs:** a good estimate of the camera angle; if the camera is fixed and sees the full height, the angle changes with the row (section 2.3).
- **Methods:** use vanishing lines from the vertical corrugation edges and the horizontal rails; or per-row calibration with a calibration target.
- **Challenge:** if the camera is only approximately at 90°, a small tilt skews the 68 / 72 / 70 mm element widths. A tilt θ changes widths by a factor cos θ.
- **Remedy:** calibrate the real camera pose once and check it with the known element widths.

### Stage 4 — Scale calibration and container type
- **Goal:** mm per pixel and 20 ft vs 40 ft.
- **Problem with 350 mm frames:** only 1.26 pitches are visible, so pitch estimation by FFT is weak.
- **Methods:** measure the known elements instead of the pitch (72 / 68 / 70 / 68 mm) from the segmented frame; or take scale from a distance sensor or a fixed calibration (distance known per position). The 20 ft vs 40 ft decision comes from total length, not from a single frame.
- **Challenge:** distance varies by 21 % across the allowed range; relief parallax of 2–3 %.

### Stage 5 — Element segmentation inside a frame
- **Goal:** split the frame into T / D / B / D elements and know the phase.
- **Methods:** a template of the cycle (from a calibration pass or from the specs) matched to the profile; edges from the dark and bright web pair; phase by NCC with the template.
- **Challenges:** contrast depends on paint and light angle; the 214 mm frame has less than one cycle; damage near an edge confuses the match.
- **Remedies:** use the lit-web / away-web brightness pair as the main landmark; require a minimum of three edges for a valid phase; mark the frame as "low confidence" otherwise.

### Stage 6 — Position along the wall and element numbering
- **Problem:** the pattern repeats, so a frame cannot say its own element number.
- **Possible sources:** encoder or speed of the moving part times frame time; frame counter from the first frame at the corner post; start and stop detected from the pattern (non-periodic band at the post, deep post-edge line).
- **Challenge:** drift over 12 m; slip; a missed frame breaks the count.
- **Remedies:** combine the count with periodic checks against anchors (posts, seams, forklift pockets); expect about 21 or 43 cycles per side as a check.

### Stage 7 — Registration of overlapping frames
- **Goal:** put frames on one axis so that a defect seen twice is counted once.
- **Methods:** use the known step as a prior; refine with NCC on the overlap (the overlap is at least a part of a cycle, so non-periodic texture is needed to remove period ambiguity); check with feature matches.
- **Challenge:** with an overlap of only about 70–140 mm, a clean wall gives ambiguous matches.
- **Remedy:** use the position source from stage 6 as the main constraint, and the image match only to refine.

### Stage 8 — Strips and cells
- **Goal:** one frame is already one slice; cut each element into strips and each strip into cells along the height.
- **Output:** a table of cells indexed by (element number, height) with area in px and mm².
- **Challenge:** diagonals are narrow (68 mm projected); an error of 1–2 px matters at low resolution.
- **Remedy:** snap boundaries to the edge response; compute areas on the rectified image.

### Stage 9 — Damage detection (dents / bulges and holes / tears only)

| Damage | Principle | Details |
|---|---|---|
| **Dents / bulges** | Pattern deviation and shading change | (1) web edges bend: fit a straight line per web edge with RANSAC and measure the deviation; (2) the brightness along a strip departs from the median of the same-type strips (a dent changes the surface normal); (3) local phase of the corrugation shifts or the element width changes. Bulge versus dent (outward vs inward) from the sign of the brightness change given the known light side. |
| **Holes / tears** | Dark void and edge detection | Compact or elongated dark region with a sharp border that breaks the strip's pattern; bright torn edges; any hole counts as damage whatever its size. Tears along welds or seams show as a line crossing the pattern. |
| Rust, stains, labels, scratches | Mask only | Must not be reported as damage. |

Method: compare every strip with the median of all strips of the same type, normalise by robust variation (MAD), flag large deviations, then classify the flagged region as dent / bulge or hole / tear.

- **Challenges:** smooth wide dents that span whole strips look like normal flats; shading depends on the (unknown) light angle; dirt, scratches and stickers; depth cannot be read from brightness alone.
- **Remedies:** compare along the strip and between neighbouring strips; use the light-angle estimate; a second light direction or a depth cue if depth is required.

### Stage 10 — Masking non-damage content
- **Content to mask:** logos, ID text, caution labels, stickers, rust, ground, reflections, post and rail regions.
- **Methods:** text and sticker detection, color rules for yellow labels, per-container label templates, shadow detection.
- **Remedy:** mask first, report damage second; list the masked area in the report.

### Stage 11 — Accumulation and measurement
- **Goal:** merge cell results into defects and compute totals.
- **Methods:** join flagged cells that touch across strips and frames; remove duplicates in overlaps; damaged area = pixels × (mm per pixel)²; damage ratio = damaged area ÷ face area (about 12.03 m × 2.39 m for a 40 ft side, 5.9 m × 2.39 m for a 20 ft side); report per defect: type, element numbers, height, area, confidence.
- **Challenges:** projected area of a dent is not its true surface area; double counting in overlaps; threshold dependence.
- **Remedy:** consistent thresholds, area with uncertainty, severity rules from the repair standard in use (for example IICL).

### Stage 12 — Validation and uncertainty
- **Needs:** real or synthetic damaged images with masks; test containers different from tuning containers.
- **Metrics:** precision, recall, IoU per damage type, area error, per-frame confidence.

### Stage 13 — Report
- Annotated face map, table of defects (type, element numbers, height, area mm², confidence), total damage ratio per face, masked areas, frame-quality warnings.

---

## 7. Cross-cutting challenges

| Challenge | Why it matters | What to do |
|---|---|---|
| Unknown flash tilt | Changes the shading of every element and can hide damage when it is above about 62° | Measure or fix the tilt; estimate it per frame; keep it below about 60° |
| Lighting falloff over the 2.4 m height | Looks like a brightness trend | Calibrate on a flat reference |
| Camera not at 90° (full-height view) | Skews widths and areas | Homography or a scanning camera (open question A1) |
| Distance 1.4–1.7 m | 21 % scale change | Distance measurement or per-frame scale from known element widths |
| Only 1.26 pitches per frame | Weak pitch and position estimate | Position source plus known element widths |
| Periodic ambiguity | Frames can be placed one pitch off | Encoder or count, non-periodic anchors, flag low confidence |
| Other faces use other profiles | Side-wall model is wrong there | Profile per face (owner to complete) |
| Rust, dirt, labels | Look like damage | Mask, never count |
| Different container types and colors | Contrast changes | Per-type calibration, check on several colors |
| Limited labelled damage | Hard to validate | Synthetic defects plus a small labelled set |

---

## 8. Limits of the prototype and next steps

- The prototype used photos of 5–11 pitches taken as exact crops, not 350 mm frames with a tilted light.
- Truth positions came from my own annotation.
- The damage map on the red 40 ft container flagged 0.7 % of the wall, mostly in the lower-middle region with visible wrinkles, but it also flagged a white sticker and a label. It misses smooth wide dents. It was a first sketch, not a measurement.

Next steps:
1. Answer the open questions in section 9, especially A1 (camera motion), A3 (frame height), A4 (resolution) and B (lighting).
2. Collect real frames in the real setup, including damaged panels (dents, bulges, holes, tears), with the light in its real position.
3. Rebuild the prototype for 350 mm frames with the position source from stage 6.
4. Build a synthetic dent / hole generator for the lit corrugation, and a small labelled test set.
5. Improve dent detection with edge straightness and shading before relying on the area number.

---

## 9. Open questions

The items marked **[Given]** were told to me by the task owner. The items marked **[My assumption]** are things I assumed without any guarantee; please confirm or correct them.

### A. Camera

| # | Question | Why it matters | Current assumption |
|---|---|---|---|
| A1 | Is the camera **fixed**, or does it **rotate / pan / tilt**, or does it move along the container? | A fixed camera at 1.4–1.7 m cannot be at 90° to the whole 2.4 m height (rays reach 35–44° off the normal at the top and bottom) | **[Given]** camera at 90°; **[My assumption]** this is true for the whole frame |
| A2 | What is the **real distance** to the wall: fixed, or a range of 1.4–1.7 m that varies between containers, positions or faces? Is it measured? | Scale changes by 21 % between the extremes | **[Given]** 1.4–1.7 m; **[My assumption]** varies and must be measured or estimated per frame |
| A3 | What is the **frame height**: the full wall height (about 2.4 m) in one frame, or a short height? | A 350 mm × 2,400 mm frame has an aspect ratio of about 1 : 7. If the height is shorter, several frames per column are needed | **[My assumption]** frames are full-height strips |
| A4 | What is the **camera resolution** and **lens (focal length)**? | Sets mm per pixel and the smallest hole or dent that can be found | Unknown; no assumption made |
| A5 | **Frame rate, shutter / exposure time, and trigger**? Does the container or the camera move, and at what speed? | Motion blur and frame spacing | **[My assumption]** one of them moves at constant speed |
| A6 | Is the **350 mm frame width a fixed field of view** (at which distance), or the result of cropping? | If 350 mm is the width at 1.4 m, it becomes about 425 mm at 1.7 m; this is only +21 %, smaller than the ±136 mm (±39 %) tolerance | **[Given]** 350 ±136 mm; **[My assumption]** the tolerance is about ±68 mm at each edge |
| A7 | What does the **tolerance ±136 mm** exactly mean (frame width, two diagonals more or less)? | Decides whether a full cycle is always in the frame and the frame spacing | **[Given]** two more or two fewer diagonals; **[My assumption]** 2 × 68 mm = 136 mm |
| A8 | **Which camera views which face** (left, right, front, door, roof)? Is there one camera for all faces, or one per face? How is the roof captured? | Different geometry and light for each face | Not assumed |
| A9 | **Lens distortion and focus**: fixed focus, depth of field over the 0.3 m distance range? | Out-of-focus edges break the element widths | Not assumed |

### B. Lighting

| # | Question | Why it matters | Current assumption |
|---|---|---|---|
| B1 | How does the flash **operate**: continuous or strobe, triggered with the camera? Intensity and duration? | Exposure and motion blur | Not assumed |
| B2 | Where is it mounted: **one side or both sides** of the frame? Distance from the wall? | Direction of shading and shadow | **[Given]** "in the sides" of the container; **[My assumption]** one light at one side per frame |
| B3 | What is the **tilt angle** (value or range)? Fixed or variable? Is it tilted horizontally (across the ribs), vertically, or both? | Above about 62° the away-facing web goes fully dark; vertical tilt does not change shading between ribs | **[Given]** tilted, angle unknown; **[My assumption]** horizontal tilt, can be estimated per frame |
| B4 | Is there **ambient daylight** (outdoor, day or night)? | Competes with the flash and changes shading | **[My assumption]** the flash dominates |
| B5 | Is the light **uniform over the 2.4 m height**? | Falloff looks like a brightness trend | **[My assumption]** it can be calibrated on a flat panel |
| B6 | Light color and any polarizer? | Reflections on wet or shiny paint | Not assumed |

### C. Position and numbering

| # | Question | Why it matters | Current assumption |
|---|---|---|---|
| C1 | What gives the **position along the wall** (encoder, speed and time, frame counter)? | A frame cannot know its element number | **[My assumption]** a counter from the corner post, or an encoder |
| C2 | Does the first frame always start at a corner post, and is the wall always scanned in the same direction? | Start and stop indicators | **[My assumption]** yes |
| C3 | Is the **20 ft vs 40 ft** type known beforehand or detected? | Number of cycles and wall length | **[My assumption]** detected from total length |
| C4 | Container **ID (OCR / ANPR)** is part of another project and **not** part of this one | Confirmed by the task owner | **[Given]** not included |

### D. Damage definition and output

| # | Question | Why it matters | Current assumption |
|---|---|---|---|
| D1 | Minimum **size or depth** of a dent / bulge or hole to count? | Sets the detection threshold | Not assumed |
| D2 | Are **cracks and fractures** really out? The original task text speaks about fractures | Hairline cracks would need a much finer pixel size | **[Given]** only dents and bulges plus holes and tears; **[My assumption]** tears cover the "fractures" of the original text |
| D3 | How is the **damage area defined**: projected area on the wall, or true surface area? Per face or per container? | Total damage number | **[My assumption]** projected area ÷ face area, per face |
| D4 | Is **dent depth** needed or only area? | Depth needs a depth cue (light model or a second view) | **[My assumption]** area only |
| D5 | What severity rules (IICL or the customer's own) apply? | Report format | Not assumed |
| D6 | What to do with rust, dirt, stickers and labels that overlap damage? | They are masked and excluded | **[Given]** corrosion excluded |

### E. Data

| # | Question | Why it matters | Current assumption |
|---|---|---|---|
| E1 | Are there **real images from the real setup**, including damaged panels, and are they labelled? | Without them, thresholds are tuned on synthetic or unrelated photos | Prototype used unrelated renders and photos |
| E2 | Which **paint colors and conditions** (new, dirty, wet)? | Contrast of the pattern | **[My assumption]** uniform paint with no mirror-like reflections |
| E3 | Faces other than the side wall: **profile dimensions** of roof, front end wall and door | The side-wall model is wrong for these faces | **[My assumption]** the owner will provide them |

### F. Technology (from the merged plan)

| # | Question | Why it matters | Current assumption |
|---|---|---|---|
| F1 | Is **classical CV only** a firm requirement (no deep learning at all, also no small classical ML classifier)? | A trained classifier could help separate dents from stains | **[Given]** no YOLO; **[My assumption]** no deep learning at all |
| F2 | **Compute platform and speed**: real-time or offline? GPU, embedded or PC? Language and libraries (for example OpenCV)? | Limits the algorithms | Not assumed |
| F3 | **Accuracy target** (for example minimum recall for holes) and how it will be tested? | Defines success | Not assumed |
| F4 | Will the system handle **all container types** (high cube, reefer, open-top) or only standard 20GP / 40GP? | Different profiles and sizes | **[My assumption]** standard 20GP and 40GP only |
| F5 | The geometry values come from **manufacturer specs** and may differ between builders (tolerances, door and end-wall profiles). Do we calibrate per container type? | Fixed numbers may not hold for every container | **[My assumption]** the side-wall profile of section 1 is valid |
| F6 | Is the **camera calibrated** (intrinsics, distortion, pose) and can we use a calibration target? | Needed for metric area | **[My assumption]** a one-time calibration is possible |
| F7 | Is human **review of low-confidence frames** allowed? | Affects how the report is built | **[My assumption]** yes |

### G. Statements in this document that are not verified

- The **lighting model** (section 3) is my own derivation from the corrugation geometry; it has not been tested on real images.
- The **prototype results** (section 4) come from my own tests on single images, with my own manual truth.
- The 6–8 mm **bend radius** from the original task document is unverified (one source lists about 5 mm).
- The numbers for the corrugation profile come from several manufacturer specification sheets; real containers can deviate.
