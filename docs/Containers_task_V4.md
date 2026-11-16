# Containers task (V4)

Updated 16 November 2026. This version replaces V3 with the new setup information: camera distance 1.7 to 1.9 m, camera fixed, continuous light fixed to the camera, container moving on a truck, and a brightness-first approach.

## **What changed from V3**

| Item | V3 | V4 |
|---|---|---|
| Camera distance | 1.4 to 1.7 m | **1.8 m nominal, tolerance 1.7 to 1.9 m** [Given] |
| Camera mounting | at 90°, unknown if fixed | **Fixed, not rotated** [Given]. The container (on a truck) moves. |
| Light | Flash at the side, tilted by an unknown angle | **Light is rigidly fixed to the camera frame, not rotated** [Given]. Tilt value still unknown but **constant**. |
| Light type | Flash (strobe or continuous unknown) | **Continuous** [Assumption, to be confirmed] |
| Scale variation | 21 % | **11.8 %** (about ±5.6 % around 1.8 m) |
| Brightness variation with distance | 1.47× | **1.25×** (+12 % at 1.7 m, −10 % at 1.9 m, relative to 1.8 m) |
| Off-normal angle at top and bottom of a 2.39 m wall | 40° to 35° | **35° (1.7 m) to 32° (1.9 m)**; high cube 38° to 35° |
| New sections | none | Exposure and blur budget, rolling shutter, flicker, ambient light, noise, brightness-first approach |

Note: an earlier chat message gave the off-normal angle at 1.7 m as about 34°. The exact value is 35°.

Figures from V3 (profile drawing, labelled photos) are not repeated here; their numbers are kept in the tables.

## **What is required ?**

Containers have many edges in them so those edges could got fractured so we need to evaluate cv module that see and sense every fracture and evaluate the total damage for 5 faces (top, left, right, front end wall, door end)

Deadline is in two weeks

## **Setup info :**

## **1-Specs**

|**Specification**|**20' Standard (20GP)**|**40' Standard (40GP)**|
|---|---|---|
|External Length|20 ft (6.06 m)|40 ft (12.19 m)|
|External Width|8 ft (2.44 m)|8 ft (2.44 m)|
|External Height|8.5 ft (2.59 m)|8.5 ft (2.59 m)|
|Internal Length|19 ft 4 in (5.90 m)|39 ft 5½ in (12.03 m)|
|Internal Width|7 ft 8 in (2.35 m)|7 ft 8 in (2.35 m)|
|Internal Height|7 ft 10 in (2.39 m)|7 ft 10 in (2.39 m)|
|Door Opening Width|7 ft 8 in (2.34 m)|7 ft 8 in (2.34 m)|
|Door Opening Height|7 ft 6 in (2.28 m)|7 ft 6 in (2.28 m)|
|Cubic Capacity (Usable)|1,172 cu ft (33.2 m³)|2,390 cu ft (67.7 m³)|
|Tare Weight (Empty)|4,850 lbs (2,200 kg)|8,380 lbs (3,800 kg)|
|Max Payload (Cargo)|62,350 lbs (28,280 kg)|58,820 lbs (26,680 kg)|
|Max Gross Weight|67,200 lbs (30,480 kg)|67,200 lbs (30,480 kg)|
|Euro Pallets|11|23–24|
|US Pallets|10|20–21|

_Notes: tare weight, payload and pallet counts vary by manufacturer and loading pattern, so treat them as typical values. Gross weight is the traditional ISO rating (many newer 40 ft units are rated higher)._

The repeating "one out, one in" shape on shipping container walls is called a **trapezoidal corrugation** (also referred to as a **trapezoidal rib** or **swage**).

If you look at the wall from a top-down cross-section, the steel sheet is bent into alternating **isosceles trapezoids**: one projecting outward (**crest** / outer flute) and one recessed inward (**trough** / inner flute), connected by angled sloped walls (**webs**).

```
OUTSIDE OF CONTAINER
      ┌────────┐                        ┌────────┐      ▲
     /  72 mm   \                      /  72 mm   \     │ 36 mm
____/            \____________________/            \____▼___
                  <-- 70 mm (trough) -->
   <---------------- 278 mm (1 full pitch) ---------------->
INSIDE OF CONTAINER
```

|**Geometric Feature**|**Engineering Term**|**Dimension**|**Description**|
|---|---|---|---|
|Full Wave Cycle|Pitch (P)|278 mm (~11 in)|Distance from one outward rib center to the next outward rib center|
|Outward Flat Face|Crest (Outer Flute)|70 mm – 75 mm (typically 72 mm)|The flat face pointing toward the outside of the container|
|Inward Flat Face|Trough (Inner Flute)|70 mm – 75 mm (typically 70 mm)|The flat face pointing toward the inside of the container|
|Depth (Out-to-In)|Corrugation Depth (D)|36 mm (Standard)|Perpendicular distance between the outer crest plane and inner trough plane|
|Angled Side Face|Web (Sloped Flank)|~77 mm (true length / hypotenuse); 68 mm projected width|The diagonal wall connecting a crest to a trough|
|Bend Angle|Web Angle (θ)|~28° (= atan 36/68)|Angle of the sloped web relative to the flat wall plane|
|Bend Radius|Fillet Radius (R)|6 mm – 8 mm (not verified; one source lists about 5 mm)|Internal corner bend radius so the steel doesn't crack during pressing|

_Check: 70 (inner flat) + 68 (web) + 72 (outer flat) + 68 (web) = 278 mm pitch. Web true length = √(68² + 36²) ≈ 77 mm; web angle = atan(36 / 68) ≈ 28°. The rib width alone (68 + 72 + 68) is 208 mm, which is not the pitch._

## Summary Table (Per Single Side Wall)

|**Component**|**20-Foot Container**|**40-Foot Container**|
|---|---|---|
|**Flat Tops (Outer Crests)**|20 – 21|42 – 43|
|**Flat Bottoms (Inner Troughs)**|20 – 21|42 – 43|
|**Diagonals (Sloped Webs)**|40 – 42|84 – 86|
|**Total Full Wave Cycles**|20 – 21|42 – 43|

Labelled photo examples from V3: one 20 ft side wall has 20 top flats (T1–T20), 21 bottom flats (B1–B21, two partial at the corner posts) and 40 diagonals (D1–D40). Another example has 18 top flats, 17 bottom flats and 35 diagonals. The labels on the 40 ft example are too small to read reliably.

## **2-Damage scope**

Only **dents / bulges** and **holes / tears** are measured. Corrosion and rust are excluded: they are only masked so they are never counted as damage.

|**Damage type**|**In scope**|**Notes**|
|---|---|---|
|2. Dents and bulges (local deformation from impact)|Yes|Main target|
|4. Holes and tears (full penetration of panels or seams)|Yes|Main target|
|3. Corrosion and rust|No (excluded)|Masked only, not counted|
|5. Fractures and cracks|No (not in the list given)|Original text says "fracture"; see open question D2. **ENG Awad assumption need to be confirmed**|
|6. Door and seal failure|No|Not in the list given|

## **3-Capture setup (given by Eng Awad assume) and what follows from it**

|**Item**|**Stated value**|**Status**|
|---|---|---|
|Camera frame (one "slice")|One top, two diagonals, two bottoms, or one bottom, two diagonals, two tops: about 350 mm|Given|
|Frame tolerance|±136 mm: up to two more diagonals framed or two fewer|Given (my reading below). **ENG Awad assumption need to be confirmed**|
|Camera distance|**1.8 m nominal, tolerance 1.7 m to 1.9 m**|Given (updated from 1.4 to 1.7 m)|
|Camera mounting|**Fixed, not rotated**|Given (updated)|
|Motion|**The container moves on a truck; the camera does not.** Speed not known.|Given (updated); speed is open question A5|
|Camera angle|90° to the wall|Given as an assumption. **ENG Awad assumption need to be confirmed**|
|Lighting position|**Fixed to the camera frame, not rotated.** Tilt angle unknown but constant.|Given (updated). Angle value: **ENG Awad assumption need to be confirmed**|
|Light type|**Continuous**|Assumption. **ENG Awad assumption need to be confirmed**|

### Frame content (unchanged from V3)

|**Case**|**Width**|**Content**|
|---|---|---|
|Nominal|348–350 mm|T D B D T (72 + 68 + 70 + 68 + 72 = 350 mm) or B D T D B (70 + 68 + 72 + 68 + 70 = 348 mm)|
|Maximum|486 mm (350 + 136)|e.g. D T D B D T D (68 + 72 + 68 + 70 + 68 + 72 + 68 = 486 mm): a diagonal added at each end|
|Minimum|214 mm (350 − 136)|about T D B (72 + 68 + 70 = 210 mm) plus slivers|

_My reading: 136 mm is the width of two diagonals (2 × 68 mm), so the tolerance is about ±68 mm at each edge of the frame._ **ENG Awad assumption need to be confirmed**

### Frame width with the new distance range (new)

If the 350 mm is the width at the nominal 1.8 m, the frame width changes in proportion to the distance. If the distance effect and the ±136 mm tolerance are independent, they add:

|**Distance**|**Frame width (350 mm at 1.8 m)**|**With ±136 mm tolerance**|
|---|---|---|
|1.7 m|331 mm|195 to 467 mm|
|1.8 m|350 mm|214 to 486 mm|
|1.9 m|369 mm|233 to 505 mm|

**ENG Awad assumption need to be confirmed** (see A6 and A7).

### Derived values

|**Topic**|**Result**|
|---|---|
|Cycles per frame|350 mm is 1.26 pitches. Frames of 350 mm or more contain at least one full cycle. A frame narrower than 278 mm (195 or 214 mm) does not.|
|Coverage|The step between frames must be at most the narrowest frame: about 195 mm if the distance effect and the tolerance add, about 214 mm if the tolerance already includes the distance effect.|
|Field of view|A 350 mm frame subtends about 11.1° at 1.8 m (11.8° at 1.7 m, 10.5° at 1.9 m).|
|Scale variation|1.9 / 1.7 = 1.118, so mm per pixel changes by about 11.8 % between the extremes (about ±5.6 % around 1.8 m).|
|Brightness variation|Light on the wall falls roughly with the square of the distance: (1.9 / 1.7)² = 1.25, so about +12 % at 1.7 m and −10 % at 1.9 m relative to 1.8 m. This is the estimate for a small lamp; a large lamp falls more slowly.|
|Relief parallax|The 36 mm depth changes magnification by about 2.1 % (1.7 m), 2.0 % (1.8 m) and 1.9 % (1.9 m) between crest and trough.|
|Pixel size|mm per pixel = frame width in mm ÷ width in pixels (example: 350 mm on 1,920 px is about 0.18 mm per pixel).|
|Camera "at 90°"|True only at the row at the camera height. If the camera sits at mid-height of a 2.39 m wall, rays at the top and bottom edge are about 35° (1.7 m) to 32° (1.9 m) off the wall normal (38° to 35° for a high cube).|
|Depth of field|The focus must hold over the 0.2 m distance range (was 0.3 m).|
|Position along the wall|A frame cannot say which element number it shows, because the pattern repeats every 278 mm. The position must come from another source (open question C1).|

### Moving container: exposure, frame rate and rolling shutter (new)

The truck speed is unknown (A5), so three example speeds are used. Blur = speed × exposure time. The pixel size assumes 350 mm on 1,920 px (0.18 mm per pixel).

|**Truck speed**|**Max exposure for 1 mm blur**|**Max exposure for 1 px (0.18 mm) blur**|**Min frame rate (frame step 195 mm)**|**Rolling-shutter skew for a 10 ms readout**|
|---|---|---|---|---|
|2 km/h|1.8 ms (1/550 s)|0.33 ms (1/3,100 s)|2.9 fps|5.6 mm (lean 0.13°)|
|5 km/h|0.72 ms (1/1,400 s)|0.13 ms (1/7,700 s)|7.1 fps|13.9 mm (lean 0.33°)|
|10 km/h|0.36 ms (1/2,800 s)|0.065 ms (1/15,000 s)|14.2 fps|27.8 mm (lean 0.67°)|

- Motion blur is horizontal: the ribs are vertical and the truck moves sideways. Blur softens the web edges and lowers the contrast of small holes. It does not affect the vertical-constancy test for dents (brightness along each rib).
- With a rolling shutter, the bottom rows are exposed later than the top rows, so the ribs lean. A lean looks like bending of the web edges and can produce false dents. Use a global-shutter camera, or fit and remove a linear lean per rib (a real dent is a local deviation, not a straight lean). Lean = atan(speed × readout time ÷ frame height), here for a 2,390 mm frame height.
- Mains-driven lamps flicker at 100 or 120 Hz. A short exposure samples that cycle and, with a rolling shutter, gives horizontal brightness bands that break the vertical-constancy test. Use constant-current DC lighting with no PWM.

## **4-Lighting model (derived by me, to be confirmed) ENG Awad assumption need to be confirmed**

Assumptions: the light is tilted by an angle α from the wall normal, in the horizontal plane across the vertical ribs; webs are 28° from the wall plane; uniform paint; no mirror-like reflections; linear camera response. **ENG Awad assumption need to be confirmed**

|**Surface**|**Relative brightness**|
|---|---|
|Flats (top and bottom)|cos α|
|Web facing the light|cos(α − 28°)|
|Web facing away|cos(α + 28°); dark, and fully self-shadowed when α is above about 62°|

|**α (light tilt)**|**Brightness ratio, lit web : away web**|**Cast shadow on the 70 mm bottom flat**|
|---|---|---|
|30°|1.9|none|
|45°|3.3|none|
|60°|24|none|
|62°|away web at zero|starts (shadow width = 36·tan α − 68 mm)|
|70°|away web fully dark|about 31 mm|
|75°|away web fully dark|about 66 mm|
|75.4° and above|away web fully dark|the whole 70 mm flat|

- Below about 60° nothing is in cast shadow; the two webs show a clear bright / dark pair.
- Above about 62° the away-facing web and part of each bottom flat go completely dark, which can hide a hole or a tear.
- A dent or bulge changes the local surface normal, so the brightness changes along the strip and the web edges bend.
- A hole or tear shows as a dark void with a sharp border, often with bright torn edges.
- A vertical tilt (up or down) does not change the shading between ribs, but it changes shadows from rails and posts.

### What the fixed light changes (new)

- The light is fixed to the camera, so α is the same in every frame. It is measured once in a calibration instead of being estimated per frame. The per-frame ratio of lit web to away web (needs uniform paint and a calibrated camera; open question B3) is then used as a consistency check.
- With one lamp on one side, the same web type is always the lit one and the same type is always the away one.
- The shading depends on the position inside the frame, not on the rib number, so the brightness template does not depend on the truck position.
- **Recommended range for α: 30° to 45°.** The lit:away ratio is 1.9 to 3.3, nothing is in cast shadow, and the angle is below the 56° glare angle. **ENG Awad assumption need to be confirmed**
- **Glare angle:** on glossy or wet paint, a lit web reflects the light straight into a camera at 90° when α ≈ 2 × 28° = 56°. The model above assumes matte paint, so this needs open questions B6 and E2.
- **Ambient light competes with a continuous lamp** much more than with a strobe (B4). Daylight fills the shadows, lowers the lit:away ratio and can hide holes. Use a shaded gantry or night operation, or calibrate the ratios under the real ambient mix.
- 8-bit image values are gamma-encoded. Convert to linear (or use RAW) before computing the cos α ratios above.

### Observation from an uncontrolled photo (not from the real rig) (new)

One front-on photo of a blue container, brightness 0 to 255 averaged over the wall rows, 9 cycles:

|**Part**|**Mean level**|**Relative to crest**|**Spread (std)**|
|---|---|---|---|
|Crest (flat outer face)|103.4|100 %|0.7|
|Trough (flat recessed face)|94.6|91 %|2.6|
|Web (crest to trough side)|79.6 (darkest pixel)|77 %|5.5|
|Web (trough to crest side)|79.8 (darkest pixel)|77 %|3.1|

- Crests are the most uniform. The trough is about 9 % darker than the crest. The two webs are equally dark; the crest-to-trough web is wider and recovers gradually, the other is narrow.
- The model predicts equal flats, but the trough is darker, so a trough-occlusion term is needed. Equal webs suggest near-diffuse light rather than a tilted lamp.
- These numbers show the kind of values the calibration will produce. They are not calibration values. **ENG Awad assumption need to be confirmed**

## **5-Brightness-first approach (new)**

Brightness is the first feature to build, because with a fixed light the expected brightness of each part is a known constant.

1. **Calibrate on a clean, undamaged wall** at 1.7, 1.8 and 1.9 m, truck stopped, then repeat at running speed. Record:
   - a flat-field map of the light falloff over the 2.4 m height (B5);
   - the expected levels of crest, trough, lit web and away web, as ratios to the crest;
   - the noise (standard deviation) of each part;
   - α, from the lit:away web ratio.
2. **Use ratios, not raw values.** Divide every pixel by the crest brightness of the same cycle. Paint color, dirt level and lamp power cancel, and the distance effect (25 %) is mostly removed.
3. **Get the distance from the image.** The widths 72 / 68 / 70 / 68 mm are known, so the pixel widths give the scale and the distance per frame, and then the expected light falloff.
4. **Find dents and bulges** from the vertical ribs: after step 2 each band should have constant brightness from top to bottom. A dent breaks that, either as a brightness gradient along the rib or as a web edge that bends sideways.
5. **Find holes and tears** as pixels darker than the away-web floor (minus a few standard deviations of the noise), with a sharp border and often bright torn edges. This needs α below about 62° so that the away web is not black.
6. **Mask** rust, stickers, labels, scratches and the corner posts.
7. **Add scale last.** Damaged area = pixels × (mm per pixel)²; damage ratio = damaged area ÷ face area, per face.

### Noise (new)

- A pixel's brightness is roughly the light on the wall × exposure time × aperture. A short exposure (needed for the moving truck) leaves little signal, so the camera gain is raised to make the image bright again.
- Light arrives as photons and the count is random (shot noise, proportional to the square root of the count). With 10,000 photons the noise is about 1 %; with 100 photons it is about 10 %.
- Gain multiplies the signal and the noise together, so the signal-to-noise ratio does not improve, and the amplifier adds its own noise.
- This matters because the differences to detect are small: trough vs crest is about 9 %, dents change the brightness along a rib by a few percent, and the away web is already dark, so it has the most relative noise.
- What to do: measure the noise in calibration and set thresholds a few standard deviations from the expected values; **average along each rib** (averaging 400 pixels lowers the noise about 20 times); add lamp power so the exposure can be short at low gain; use a wide aperture and large pixels; fit a noise model so the threshold scales with brightness.

## **Impact on the pipeline (short)**

- The earlier prototype used photos of 5–11 pitches; a 350 mm frame holds only 1.26 pitches, so its results do not transfer (pitch estimation and overlap matching were done on far more pattern).
- Scale should come from a distance measurement or the known element widths (72 / 68 / 70 / 68 mm), not from the pitch alone. At 1.8 m the scale changes by about ±5.6 % across the distance range.
- The position along the wall (encoder, speed × time, or a frame counter from the corner post) is needed to number elements; image overlap only refines it. The container moves, so the encoder or speed signal must come from the truck or a sensor at the gantry.
- Dents are found as deviations from the median of the same-type strips (T or B), from bending of the web edges, and from brightness change along a strip; holes and tears as dark voids with sharp borders. Rust, stickers, labels and scratches are masked.
- Damaged area = pixels × (mm per pixel)²; damage ratio = damaged area ÷ face area, per face.
- The camera must run with auto-exposure, auto white balance and gamma correction off, so that brightness ratios are stable.

## **6-Open questions**

Items marked [Given] were told by Eng Awad or the requester. Items marked [Assumption] were assumed without any guarantee: please confirm or correct them. Every question below is **needed to be questioned to eng awad**. Rows marked "(updated)" or "(new)" changed from V3.

### **A. Camera**

|**#**|**Question**|**Why it matters**|**Current assumption**|
|---|---|---|---|
|A1 (updated)|Does the camera rotate, pan, tilt or move?<br>الكاميرا ثابتة ولا بتلف أو بتتحرك؟|A fixed camera at 1.7–1.9 m cannot be at 90° to the whole 2.4 m height (32–35° off at the top and bottom)|[Given] camera fixed, not rotated; the container moves. [Assumption] 90° is true for the whole frame **ENG Awad assumption need to be confirmed**|
|A2 (updated)|Is the distance to the wall fixed, or varying within 1.7–1.9 m? Is it measured?<br>المسافة الحقيقية بين الكاميرا والحيطة كام، وهل بتتقاس؟|Scale changes by 11.8 %, brightness by 25 %|[Given] 1.8 m, tolerance 1.7–1.9 m. [Assumption] it varies with the truck position and is estimated per frame from the known widths **ENG Awad assumption need to be confirmed**|
|A3|What is the frame height: the full wall height (about 2.4 m) or a short height?<br>ارتفاع الصورة كام: ارتفاع الحيطة كله (حوالي 2.4 متر) ولا ارتفاع أقصر؟|A 350 × 2,400 mm frame is about 1 : 7; a short height means several frames per column|[Assumption] full-height strips **ENG Awad assumption need to be confirmed**|
|A4 (updated)|What is the camera resolution, lens (focal length), sensor size and pixel size?<br>دقة الكاميرا كام والعدسة إيه (البعد البؤري)، وحجم الحساس وحجم البكسل كام؟|Sets mm per pixel, the smallest hole or dent that can be found, and the noise level|Unknown; none made|
|A5 (updated)|What is the truck speed? Constant or variable? Direction of travel? Frame rate, exposure time, trigger?<br>سرعة الشاحنة كام، وثابتة ولا بتتغير؟ واتجاه الحركة؟ ومعدل الفريمات ووقت التعريض والتريجر إيه؟|Sets the maximum exposure (blur), the minimum frame rate and the rolling-shutter skew|[Given] the container moves. [Assumption] constant speed **ENG Awad assumption need to be confirmed**|
|A6 (updated)|Is the 350 mm width a fixed field of view, and at which distance?<br>عرض 350 mm ده مجال رؤية ثابت عند أنهي مسافة؟|If 350 mm is the width at 1.8 m it becomes 331 mm at 1.7 m and 369 mm at 1.9 m|[Assumption] 350 mm at 1.8 m **ENG Awad assumption need to be confirmed**|
|A7|What exactly does the ±136 mm tolerance mean?<br>الـ ±136 mm يعني إيه بالظبط؟|Decides whether a full cycle is always in the frame, and the spacing (195 mm or 214 mm step)|[Given] two more or two fewer diagonals. [Assumption] 2 × 68 = 136 mm **ENG Awad assumption need to be confirmed**|
|A8|Which camera views which face (left, right, front, door, roof)? How is the roof captured?<br>أنهي كاميرا بتصور أنهي جانب: يمين، شمال، الواجهة الأمامية، الباب، السقف؟ والسقف بيتصور إزاي؟|Different geometry and light for each face|None made|
|A9 (updated)|Focus and depth of field over the 0.2 m distance range?<br>التركيز وعمق المجال على مدى مسافة 0.2 متر هيبقى عامل إزاي؟|Out-of-focus edges break the element widths|None made|
|A10 (new)|Is the camera global shutter or rolling shutter? What is the readout time?<br>الكاميرا Global shutter ولا Rolling shutter؟ وزمن القراءة (readout) كام؟|A rolling shutter makes the ribs lean on a moving container (0.33° at 5 km/h and 10 ms)|None made|
|A11 (new)|Can auto-exposure, auto white balance and gamma be switched off, and can the camera give RAW or 10–12 bit images without compression?<br>ينفع نقفل الـ auto-exposure والـ auto white balance والـ gamma ونصور RAW أو 10–12 bit من غير ضغط؟|Brightness ratios need stable, linear values|[Assumption] yes **ENG Awad assumption need to be confirmed**|

### **B. Lighting**

|**#**|**Question**|**Why it matters**|**Current assumption**|
|---|---|---|---|
|B1 (updated)|Is the light continuous (LED) or a strobe? Is it constant-current DC with no PWM and no flicker?<br>الإضاءة مستمرة (LED) ولا فلاش ومضة؟ وهل بتشتغل بتيار ثابت DC من غير PWM وفليكر؟|Exposure, motion blur, and flicker bands with a rolling shutter|[Assumption] continuous **ENG Awad assumption need to be confirmed**|
|B2 (updated)|Where is the light mounted relative to the camera: one side or both sides? Distance from the camera axis? Size of the lamp?<br>مصدر الضوء متركب فين بالنسبة للكاميرا: على جنب واحد ولا الجنبين؟ وبعده عن محور الكاميرا كام، وحجمه إيه؟|Direction of shading and shadow; which web is lit|[Given] fixed to the camera frame, not rotated. [Assumption] one lamp at one side **ENG Awad assumption need to be confirmed**|
|B3 (updated)|What is the tilt angle (value)? Horizontal, vertical or both?<br>زاوية ميل الضوء كام (قيمة ثابتة)؟ أفقية ولا رأسية ولا الاتنين؟|Above about 62° the away web goes fully dark; near 56° glossy paint can glare|[Given] unknown but constant. [Assumption] horizontal tilt, measured once in calibration **ENG Awad assumption need to be confirmed**|
|B4 (updated)|Is there ambient daylight (outdoor, shaded gantry or tunnel, day or night)?<br>في ضوء نهار أو إضاءة محيطة؟ (برا ولا جوه نفق أو مظلة؟ نهار ولا ليل؟)|A continuous lamp competes with daylight; daylight fills the shadows and hides holes|[Assumption] shaded or night, the lamp dominates **ENG Awad assumption need to be confirmed**|
|B5|Is the light uniform over the 2.4 m height?<br>الإضاءة متساوية على ارتفاع 2.4 متر كله؟|Falloff looks like a brightness trend|[Assumption] it can be calibrated on a flat panel at 3 distances **ENG Awad assumption need to be confirmed**|
|B6|Light color, any polarizer, and is the paint glossy or wet?<br>لون الإضاءة إيه، وفي فلتر استقطاب؟ والدهان لامع أو مبلول؟|Reflections and glare on shiny paint|None made|
|B7 (new)|Is the lamp stable over time (warm-up, aging)? How often can it be calibrated?<br>الإضاءة ثابتة مع الوقت (سخونة أو عمر الـ LED) ولا بتتغير؟ نعاير كل قد إيه؟|A drift changes all brightness ratios|[Assumption] stable within a day, calibrate daily **ENG Awad assumption need to be confirmed**|

### **C. Position and numbering**

|**#**|**Question**|**Why it matters**|**Current assumption**|
|---|---|---|---|
|C1 (updated)|What gives the position along the wall (encoder, speed and time, frame counter)? The container moves, so where does the signal come from?<br>إيه اللي بيحدد الموضع على طول الحيطة (إنكودر، السرعة × الوقت، عداد فريمات)؟|A frame cannot know its element number|[Assumption] a counter from the corner post, or an encoder **ENG Awad assumption need to be confirmed**|
|C2|Does the first frame always start at a corner post, and is the wall always scanned in the same direction?<br>أول فريم بيبدأ دايما من عمود الركن؟ والحيطة بتتصور دايما في نفس الاتجاه؟|Start and stop indicators; which web is lit|[Assumption] yes **ENG Awad assumption need to be confirmed**|
|C3|Is 20 ft vs 40 ft known beforehand or detected?<br>بنعرف من قبل إن الكونتينر 20 ولا 40 قدم، ولا بيتكشف أوتوماتيك؟|Number of cycles and wall length|[Assumption] detected from total length **ENG Awad assumption need to be confirmed**|

### **D. Damage definition and output**

|**#**|**Question**|**Why it matters**|**Current assumption**|
|---|---|---|---|
|D1|Minimum size or depth of a dent / bulge or hole to count?<br>أقل حجم أو عمق للبعجة أو الانتفاخ أو الخرق عشان يتحسب؟|Sets the detection threshold|None made|
|D2|Are cracks and fractures really out? The original task text speaks about fractures.<br>الشروخ والكسور فعلا مش مطلوبة؟ نص المهمة الأصلي بيتكلم عن الكسور.|Hairline cracks would need a much finer pixel size|[Given] only dents and bulges plus holes and tears. [Assumption] tears cover the "fractures" **ENG Awad assumption need to be confirmed**|
|D3|How is the damage area defined: projected or true surface area? Per face or per container?<br>مساحة التلف تتحسب إزاي: المساحة المسقطة ولا الحقيقية؟ لكل جانب ولا للكونتينر كله؟|Total damage number|[Assumption] projected area ÷ face area, per face **ENG Awad assumption need to be confirmed**|
|D4|Is dent depth needed, or only area?<br>محتاجين عمق البعجة ولا المساحة بس؟|Depth needs a depth cue (light model or a second view)|[Assumption] area only **ENG Awad assumption need to be confirmed**|
|D5|Which severity rules (IICL or the customer's own)?<br>إيه قواعد تصنيف الشدة: IICL ولا قواعد العميل؟|Report format|None made|
|D6|Rust, dirt, stickers and labels overlapping damage?<br>الصدا والوسخ والاستيكرز والكتابة اللي فوق التلف نعمل فيهم إيه؟|They are masked and excluded|[Given] corrosion excluded|

### **E. Data**

|**#**|**Question**|**Why it matters**|**Current assumption**|
|---|---|---|---|
|E1|Are there real images from the real setup, including damaged panels, and are they labelled?<br>في صور حقيقية من الإعداد الفعلي فيها ألواح تالفة، وهل متعلم عليها؟|Without them, thresholds are tuned on unrelated photos|The prototype used unrelated renders and photos|
|E2|Which paint colors and conditions (new, dirty, wet)?<br>ألوان الدهان إيه والحالة إيه: جديد ولا وسخ ولا مبلول؟|Contrast of the pattern; glare|[Assumption] uniform paint, no mirror-like reflections **ENG Awad assumption need to be confirmed**|
|E3|Profiles of the other faces (roof, front end wall, door)?<br>شكل الجوانب التانية إيه: السقف والواجهة الأمامية والباب؟|The side-wall model is wrong for these faces|[Assumption] Eng Awad will provide them **ENG Awad assumption need to be confirmed**|
|E4 (new)|Can a calibration run be made with a clean, undamaged container at 1.7, 1.8 and 1.9 m, truck stopped and moving?<br>ينفع نعمل تشغيل معايرة بكونتينر سليم ونضيف على 3 مسافات (1.7 و1.8 و1.9 متر)، والشاحنة واقفة وبتتحرك؟|The brightness-first method needs the expected levels and the noise measured on the real rig|[Assumption] yes **ENG Awad assumption need to be confirmed**|

### **F. Technology**

|**#**|**Question**|**Why it matters**|**Current assumption**|
|---|---|---|---|
|F1|Is classical CV only a firm rule (no deep learning, also no small classical ML classifier)?<br>هل الاعتماد على الرؤية الكلاسيكية بس شرط ثابت (من غير ديب ليرنينج ومن غير مصنف ML صغير)؟|A trained classifier could help separate dents from stains|[Given] no YOLO. [Assumption] no deep learning at all **ENG Awad assumption need to be confirmed**|
|F2|Compute platform and speed: real-time or offline? GPU, embedded or PC? Language and libraries (e.g. OpenCV)?<br>منصة التشغيل والسرعة إيه: ريل تايم ولا أوفلاين؟ GPU ولا embedded ولا PC؟ واللغة والمكتبات (زي OpenCV)؟|Limits the algorithms; a truck at 10 km/h needs about 14 fps|None made|
|F3|Accuracy target (e.g. minimum recall for holes) and how it is tested?<br>هدف الدقة كام (زي أقل ريكول للخروق) وهنختبره إزاي؟|Defines success|None made|
|F4|All container types (high cube, reefer, open-top) or only standard 20GP / 40GP?<br>كل أنواع الكونتينرات (high cube وreefer وopen-top) ولا الستاندرد 20GP و40GP بس؟|Different profiles and sizes|[Assumption] standard 20GP and 40GP only **ENG Awad assumption need to be confirmed**|
|F5|The geometry values come from manufacturer specs and may differ between builders. Calibrate per container type?<br>أبعاد الهندسة جاية من مواصفات المصنعين وممكن تختلف. نعمل معايرة لكل نوع كونتينر؟|Fixed numbers may not hold for every container|[Assumption] the side-wall profile is valid **ENG Awad assumption need to be confirmed**|
|F6|Is the camera calibrated (intrinsics, distortion, pose)? Can a calibration target be used?<br>الكاميرا متعايرة (intrinsics وdistortion والوضع)؟ ينفع نستخدم لوحة معايرة؟|Needed for metric area|[Assumption] a one-time calibration is possible **ENG Awad assumption need to be confirmed**|
|F7|Is human review of low-confidence frames allowed?<br>مسموح بمراجعة بشرية للفريمات اللي ثقتها قليلة؟|Affects how the report is built|[Assumption] yes **ENG Awad assumption need to be confirmed**|

## **G. Statements not verified**

- The lighting model (section 4) is my own derivation from the corrugation geometry; it has not been tested on real images. **ENG Awad assumption need to be confirmed**
- The 56° glare angle assumes a glossy surface and a camera exactly on the wall normal. **ENG Awad assumption need to be confirmed**
- The brightness numbers in the "uncontrolled photo" table come from one photo with unknown lighting. **ENG Awad assumption need to be confirmed**
- The exposure, frame-rate and rolling-shutter tables use example truck speeds (2, 5, 10 km/h) and a 10 ms readout; the real values are not known. **ENG Awad assumption need to be confirmed**
- The inverse-square brightness estimate (25 %) is for a small lamp; a large lamp, or one far from the wall, changes less. **ENG Awad assumption need to be confirmed**
- The noise discussion is qualitative; the real noise must be measured in calibration. **ENG Awad assumption need to be confirmed**
- The prototype results come from my own tests on single images, with my own manual truth. **ENG Awad assumption need to be confirmed**
- The 6–8 mm bend radius in the original table is unverified (one source lists about 5 mm). **ENG Awad assumption need to be confirmed**
- The corrugation profile numbers come from several manufacturer specification sheets; real containers can deviate. **ENG Awad assumption need to be confirmed**
