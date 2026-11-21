import sys
import time
import inspect
import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

from core.edge_detector import EdgeDetector
from core.brightness_calc import BrightnessDetector

DEFAULT_IMAGE = "test_data/cropped_container2_2.jpg"


# ----------------------------------------------------------------------
# Pipeline — mirrors main.py exactly
# ----------------------------------------------------------------------
def run_pipeline(image, ed, bd, min_height_ratio, max_deviation):
    debug = image.copy()

    # Step 1: detect vertical regions
    ed.image = image
    regions = ed.get_vertical_regions()

    # Step 2: brightness / hole detection per region
    bd.image = image
    total_anomaly = 0
    total_area    = 0
    region_brightness = []

    for region in regions:
        bd.bounds = region
        s, e = region
        total_area += image.shape[0] * (e - s)

        # calculate_damage_area returns (anomaly_area, majority_brightness)
        anomaly_area, majority_brightness = bd.calculate_damage_area(debug_image=debug)
        region_brightness.append(majority_brightness)
        total_anomaly += anomaly_area

    # Step 3: Crest / Trough labels (same alternating logic as main.py)
    if region_brightness:
        crest_index = int(np.argmax(region_brightness))
        for i, (s, e) in enumerate(regions):
            label = "1" if (i - crest_index) % 2 == 0 else "0"
            (tw, _), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.putText(debug, label, ((s + e) // 2 - tw // 2, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    # Step 4: edge damage (uses sliders min_height_ratio / max_deviation)
    edge_results, edge_damage, debug = ed.check_edges_damage(
        min_height_ratio=min_height_ratio,
        max_deviation=max_deviation,
        debug_image=debug,
    )

    brightness_area = total_anomaly
    total_anomaly  += edge_damage
    pct = total_anomaly / total_area * 100 if total_area > 0 else 0

    stats = {
        "regions":         len(regions),
        "total_area":      total_area,
        "brightness_area": brightness_area,
        "edge_damage":     edge_damage,
        "total_damage":    total_anomaly,
        "pct":             pct,
        "edges":           edge_results,
    }
    return debug, stats


# ----------------------------------------------------------------------
# Widgets
# ----------------------------------------------------------------------
class ParamSlider(QtWidgets.QWidget):
    """Integer slider that can represent floats (scale) or odd-only ints (odd)."""
    changed = QtCore.pyqtSignal()

    def __init__(self, name, lo, hi, value, scale=1, odd=False):
        super().__init__()
        self.name, self.scale, self.odd = name, scale, odd

        self.title = QtWidgets.QLabel(name)
        self.value_label = QtWidgets.QLabel()
        self.value_label.setMinimumWidth(50)
        self.value_label.setAlignment(QtCore.Qt.AlignRight)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        if odd:
            self.slider.setRange((lo - 1) // 2, (hi - 1) // 2)
            self.slider.setValue((value - 1) // 2)
        else:
            self.slider.setRange(lo, hi)
            self.slider.setValue(int(round(value * scale)))
        self.slider.valueChanged.connect(self._on_change)

        top = QtWidgets.QHBoxLayout()
        top.addWidget(self.title)
        top.addStretch()
        top.addWidget(self.value_label)
        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(0, 2, 0, 2)
        lay.addLayout(top)
        lay.addWidget(self.slider)
        self._refresh_label()

    def value(self):
        v = self.slider.value()
        if self.odd:
            return 2 * v + 1
        return v / self.scale if self.scale != 1 else v

    def _refresh_label(self):
        v = self.value()
        self.value_label.setText(f"{v:.2f}" if isinstance(v, float) else str(v))

    def _on_change(self):
        self._refresh_label()
        self.changed.emit()


class ImageView(QtWidgets.QLabel):
    """Label that keeps its pixmap scaled to the available space."""
    def __init__(self, title):
        super().__init__()
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumSize(200, 150)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.setStyleSheet("background:#202020; color:#aaa;")
        self.setText(title)
        self._pix = None

    def set_bgr(self, img):
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, _ = rgb.shape
        qimg = QtGui.QImage(rgb.data, w, h, 3 * w, QtGui.QImage.Format_RGB888).copy()
        self._pix = QtGui.QPixmap.fromImage(qimg)
        self._rescale()

    def _rescale(self):
        if self._pix is not None:
            self.setPixmap(self._pix.scaled(self.size(), QtCore.Qt.KeepAspectRatio,
                                            QtCore.Qt.SmoothTransformation))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._rescale()


# ----------------------------------------------------------------------
# Main window
# ----------------------------------------------------------------------
class CalibrationWindow(QtWidgets.QMainWindow):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle("Damage detection calibration")
        self.resize(1500, 800)

        self.image = None

        # Build detectors with defaults — their attribute values drive the sliders below
        self.edge_detector       = EdgeDetector()
        self.brightness_detector = BrightnessDetector()

        # Read check_edges_damage method signature defaults once
        _ced_sig = inspect.signature(EdgeDetector.check_edges_damage).parameters
        _ced_min_height_ratio = _ced_sig["min_height_ratio"].default  # e.g. 0.6
        _ced_max_deviation    = _ced_sig["max_deviation"].default     # e.g. 3

        ed = self.edge_detector
        bd = self.brightness_detector

        # Debounce: dragging a slider doesn't queue dozens of runs
        self.timer = QtCore.QTimer(singleShot=True, interval=120)
        self.timer.timeout.connect(self.update_result)

        # ---- parameter sliders ----
        # Initial values come directly from the class instances / method signature,
        # so changing a default in EdgeDetector or BrightnessDetector is enough —
        # no need to touch this file.
        self.sliders = {
            # EdgeDetector instance attribute defaults
            "threshold":           ParamSlider("threshold (Sobel)",       0,   255,  ed.threshold,           ),
            "ksize":               ParamSlider("ksize (Sobel, odd)",       1,     7,  ed.ksize,               odd=True),
            "close_height":        ParamSlider("close_height (odd)",       1,   101,  ed.close_height,        odd=True),
            "column_ratio":        ParamSlider("column_ratio (×100)",      1,   100,  ed.column_ratio,        scale=100),
            "min_distance":        ParamSlider("min_distance",             1,   100,  ed.min_distance,        ),
            "min_num_of_coloumns": ParamSlider("min_num_of_coloumns",      1,    20,  ed.min_num_of_coloumns, ),
            # check_edges_damage method signature defaults
            "min_height_ratio":    ParamSlider("min_height_ratio (×100)", 10,   100,  _ced_min_height_ratio,  scale=100),
            "max_deviation":       ParamSlider("max_deviation (px)",       0,    30,  _ced_max_deviation,     ),
            # BrightnessDetector instance attribute defaults
            "min_area":            ParamSlider("min_area (px²)",           1,   500,  bd.min_area,            ),
            "blur":                ParamSlider("blur_kernel (odd)",         1,    31,  bd.blur_kernel[0],      odd=True),
        }

        groups = {
            "EdgeDetector": [
                "threshold", "ksize", "close_height",
                "column_ratio", "min_distance", "min_num_of_coloumns",
            ],
            "check_edges_damage": ["min_height_ratio", "max_deviation"],
            "BrightnessDetector": ["min_area", "blur"],
        }

        left = QtWidgets.QVBoxLayout()
        for gname, keys in groups.items():
            box = QtWidgets.QGroupBox(gname)
            bl  = QtWidgets.QVBoxLayout(box)
            for k in keys:
                self.sliders[k].changed.connect(self.schedule_update)
                bl.addWidget(self.sliders[k])
            left.addWidget(box)

        btn_open = QtWidgets.QPushButton("Open image…")
        btn_open.clicked.connect(self.open_image)
        btn_copy = QtWidgets.QPushButton("Copy parameters to clipboard")
        btn_copy.clicked.connect(self.copy_params)
        left.addWidget(btn_open)
        left.addWidget(btn_copy)
        left.addStretch()

        left_w = QtWidgets.QWidget()
        left_w.setLayout(left)
        left_w.setFixedWidth(340)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(left_w)
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(360)

        # ---- images + stats panel ----
        self.view_orig  = ImageView("Original")
        self.view_debug = ImageView("Debug")
        imgs = QtWidgets.QHBoxLayout()
        imgs.addWidget(self.view_orig)
        imgs.addWidget(self.view_debug)

        self.stats = QtWidgets.QPlainTextEdit()
        self.stats.setReadOnly(True)
        self.stats.setMaximumHeight(190)
        self.stats.setStyleSheet("font-family: Consolas, monospace; font-size: 11px;")

        right = QtWidgets.QVBoxLayout()
        right.addLayout(imgs, stretch=1)
        right.addWidget(self.stats)

        central = QtWidgets.QWidget()
        root    = QtWidgets.QHBoxLayout(central)
        root.addWidget(scroll)
        root.addLayout(right, stretch=1)
        self.setCentralWidget(central)

        self.load_image(image_path)

    # ---- file handling ----
    def open_image(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open image", "", "Images (*.png *.jpg *.jpeg *.bmp *.jfif)")
        if path:
            self.load_image(path)

    def load_image(self, path):
        img = cv2.imread(path)
        if img is None:
            self.statusBar().showMessage(f"Could not read: {path}")
            return
        self.image = img
        self.view_orig.set_bgr(img)
        self.update_result()

    # ---- param application ----
    def schedule_update(self):
        """Called on every slider move; deferred so rapid drags cost one run."""
        self.timer.start()

    def _read_sliders(self):
        return {k: s.value() for k, s in self.sliders.items()}

    def apply_params(self):
        """Push all slider values into the detector objects."""
        v  = self._read_sliders()
        ed = self.edge_detector
        bd = self.brightness_detector

        # EdgeDetector properties
        ed.threshold           = int(v["threshold"])
        ed.ksize               = int(v["ksize"])
        ed.close_height        = int(v["close_height"])
        ed.column_ratio        = float(v["column_ratio"])
        ed.min_distance        = int(v["min_distance"])
        ed.min_num_of_coloumns = int(v["min_num_of_coloumns"])

        # BrightnessDetector properties
        k = int(v["blur"])
        bd.min_area    = int(v["min_area"])
        bd.blur_kernel = (k, k)

        return v

    # ---- pipeline execution ----
    def update_result(self):
        if self.image is None:
            return
        v = self.apply_params()
        try:
            t0 = time.perf_counter()
            debug, s = run_pipeline(
                self.image,
                self.edge_detector,
                self.brightness_detector,
                float(v["min_height_ratio"]),
                float(v["max_deviation"]),
            )
            dt = (time.perf_counter() - t0) * 1000
        except Exception as ex:
            import traceback
            self.statusBar().showMessage(f"Error — {type(ex).__name__}: {ex}")
            self.stats.setPlainText(traceback.format_exc())
            return

        self.view_debug.set_bgr(debug)
        self.statusBar().showMessage(f"Pipeline: {dt:.1f} ms")

        lines = [
            f"Regions: {s['regions']}    Total area: {s['total_area']} px",
            f"Brightness anomaly: {s['brightness_area']:.0f} px    "
            f"Edge damage: {s['edge_damage']} px",
            f"Total damage:  {s['total_damage']:.0f} px   →   {s['pct']:.2f}%",
            "",
        ]
        for r in s["edges"]:
            dmg = "DAMAGED" if r["is_damaged"] else "ok     "
            lines.append(
                f"edge x={r['edge_center']:4d}  cov={r['coverage']:.2f}  "
                f"maxdev={r['max_deviation']:.1f}  curved={r['curved_pixels']:4d}  {dmg}"
            )
        self.stats.setPlainText("\n".join(lines))

    # ---- clipboard export ----
    def copy_params(self):
        v = self._read_sliders()
        text = (
            f"EdgeDetector(\n"
            f"    threshold={int(v['threshold'])},\n"
            f"    ksize={int(v['ksize'])},\n"
            f"    close_height={int(v['close_height'])},\n"
            f"    column_ratio={v['column_ratio']:.4f},\n"
            f"    min_distance={int(v['min_distance'])},\n"
            f"    min_num_of_coloumns={int(v['min_num_of_coloumns'])},\n"
            f")\n"
            f"BrightnessDetector(\n"
            f"    min_area={int(v['min_area'])},\n"
            f"    blur_kernel=({int(v['blur'])}, {int(v['blur'])}),\n"
            f")\n"
            f"check_edges_damage(\n"
            f"    min_height_ratio={v['min_height_ratio']:.4f},\n"
            f"    max_deviation={v['max_deviation']},\n"
            f")"
        )
        QtWidgets.QApplication.clipboard().setText(text)
        self.statusBar().showMessage("Parameters copied to clipboard", 3000)


if __name__ == "__main__":
    app  = QtWidgets.QApplication(sys.argv)
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IMAGE
    win  = CalibrationWindow(path)
    win.show()
    sys.exit(app.exec_())
