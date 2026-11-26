import cv2 as cv
import numpy as np


class EdgeTracker:

    def __init__(
        self,
        max_distance=30,
        confirmation_frames=3,
        max_missing_frames=3,
        collective_threshold=5,
        process_noise=1e-2,
        measurement_noise=1e-1,
        velocity_threshold=2.0,
        velocity_smoothing=0.3,
        default_velocity_var=1.0,
        min_velocity_var=0.05,
        min_tracks_for_container=2,
        reverse_direction=False,
        new_edge_ratio=0.1
    ):

        self.max_distance = max_distance
        self.confirmation_frames = confirmation_frames
        self.max_missing_frames = max_missing_frames
        self.collective_threshold = collective_threshold

        self.process_noise = process_noise
        self.measurement_noise = measurement_noise

        # Max allowed difference (px/frame) between an edge's velocity
        # and the container velocity before it is flagged as inconsistent
        self.velocity_threshold = velocity_threshold

        # Exponential smoothing factor for the container velocity (0..1).
        # Higher = reacts faster, lower = smoother.
        self.velocity_smoothing = velocity_smoothing

        # Velocity variance used when the container velocity is unknown
        self.default_velocity_var = default_velocity_var

        # Lower bound on the seeded velocity variance (never be 100% sure)
        self.min_velocity_var = min_velocity_var

        # Minimum number of reliable tracks needed to estimate the
        # container velocity
        self.min_tracks_for_container = min_tracks_for_container

        # Truck direction of movement
        self.reverse_direction = reverse_direction

        # New edges may only appear within this fraction of the width,
        # measured from the side the truck enters from:
        #   reverse_direction=False -> x <= ratio * width
        #   reverse_direction=True  -> x >= (1 - ratio) * width
        self.new_edge_ratio = new_edge_ratio

        self._tracks = []
        self.next_id = 0

        self.frame_count = 0

        # Shared container motion estimate
        self.container_velocity = 0.0
        self.container_velocity_var = default_velocity_var
        self.has_container_velocity = False

    # --------------------------------------------------
    # Kalman Filter initialization
    # --------------------------------------------------

    def _create_kalman(self, initial_x, initial_velocity=0.0, velocity_var=1.0):

        kalman = cv.KalmanFilter(2, 1)

        # State: [x, velocity]
        kalman.transitionMatrix = np.array(
            [
                [1, 1],
                [0, 1]
            ],
            dtype=np.float32
        )

        # Measurement: x only
        kalman.measurementMatrix = np.array(
            [
                [1, 0]
            ],
            dtype=np.float32
        )

        kalman.processNoiseCov = np.eye(
            2,
            dtype=np.float32
        ) * self.process_noise

        kalman.measurementNoiseCov = np.array(
            [[self.measurement_noise]],
            dtype=np.float32
        )

        # Position variance = 1, velocity variance = how sure we are
        # about the seeded velocity
        kalman.errorCovPost = np.array(
            [
                [1.0, 0.0],
                [0.0, velocity_var]
            ],
            dtype=np.float32
        )

        kalman.statePost = np.array(
            [
                [initial_x],
                [initial_velocity]
            ],
            dtype=np.float32
        )

        return kalman

    # --------------------------------------------------
    # Create a new track
    # --------------------------------------------------

    def _create_track(self, x):

        # Seed velocity from the container if we know it
        if self.has_container_velocity:
            initial_velocity = self.container_velocity
            velocity_var = self.container_velocity_var
        else:
            initial_velocity = 0.0
            velocity_var = self.default_velocity_var

        track = {
            "id": self.next_id,

            "kalman": self._create_kalman(
                x,
                initial_velocity=initial_velocity,
                velocity_var=velocity_var
            ),

            "initial_x": float(x),
            "current_x": float(x),
            "predicted_x": float(x),

            "velocity": float(initial_velocity),
            "displacement": 0.0,

            "age": 1,
            "hits": 1,
            "consecutive_hits": 1,
            "misses": 0,

            "state": "tentative",

            "previous_x": float(x),

            "history": [float(x)],

            "collective_error": 0.0,
            "movement_valid": True,

            "velocity_error": 0.0,
            "velocity_valid": True
        }

        self._tracks.append(track)

        self.next_id += 1

    # --------------------------------------------------
    # Entry zone check for new edges
    # --------------------------------------------------

    def _is_in_entry_zone(self, x, width):

        limit = self.new_edge_ratio * width

        if self.reverse_direction:
            return x >= width - limit

        return x <= limit

    # --------------------------------------------------
    # Predict all existing tracks
    # --------------------------------------------------

    def _predict_tracks(self):

        for track in self._tracks:

            prediction = track["kalman"].predict()

            predicted_x = float(prediction[0, 0])

            track["predicted_x"] = predicted_x

            track["age"] += 1

    # --------------------------------------------------
    # Associate detections with predicted tracks
    # --------------------------------------------------

    def _associate_detections(self, detected_edges):

        # Sorted in the truck's direction of travel
        detected_edges = sorted(
            (float(x) for x in detected_edges), reverse=self.reverse_direction
        )

        candidates = []

        for track_index, track in enumerate(self._tracks):

            for detection_index, detection in enumerate(detected_edges):

                distance = abs(
                    track["predicted_x"] - detection
                )

                if distance <= self.max_distance:

                    candidates.append(
                        (distance, track_index, detection_index)
                    )

        # Closest matches first
        for i in range(len(candidates)):
            for j in range(i + 1, len(candidates)):

                if candidates[j][0] < candidates[i][0]:
                    temp = candidates[i]
                    candidates[i] = candidates[j]
                    candidates[j] = temp

        matched_tracks = set()
        matched_detections = set()

        matches = []

        for distance, track_index, detection_index in candidates:

            if track_index in matched_tracks:
                continue

            if detection_index in matched_detections:
                continue

            matched_tracks.add(track_index)
            matched_detections.add(detection_index)

            matches.append(
                (track_index, detection_index)
            )

        unmatched_tracks = [
            i for i in range(len(self._tracks))
            if i not in matched_tracks
        ]

        unmatched_detections = [
            i for i in range(len(detected_edges))
            if i not in matched_detections
        ]

        return (
            matches,
            unmatched_tracks,
            unmatched_detections,
            detected_edges
        )

    # --------------------------------------------------
    # Validate collective movement (raw frame-to-frame motion)
    # --------------------------------------------------

    def _validate_collective_movement(self, matches, detections):

        movements = []

        for track_index, detection_index in matches:

            track = self._tracks[track_index]

            movement = (
                detections[detection_index] - track["previous_x"]
            )

            movements.append(
                (track_index, movement)
            )

        if len(movements) < 2:

            for track_index, _ in movements:
                self._tracks[track_index]["collective_error"] = 0.0
                self._tracks[track_index]["movement_valid"] = True

            return

        # Median displacement of all matched edges
        median_movement = np.median(
            [movement for _, movement in movements]
        )

        for track_index, movement in movements:

            error = abs(movement - median_movement)

            track = self._tracks[track_index]

            track["collective_error"] = float(error)

            track["movement_valid"] = (
                error <= self.collective_threshold
            )

    # --------------------------------------------------
    # Update matched tracks
    # --------------------------------------------------

    def _update_tracks(self, matches, detections):

        for track_index, detection_index in matches:

            track = self._tracks[track_index]

            detection = detections[detection_index]

            measurement = np.array(
                [[detection]],
                dtype=np.float32
            )

            corrected = track["kalman"].correct(
                measurement
            )

            track["previous_x"] = track["current_x"]

            track["current_x"] = float(corrected[0, 0])

            track["velocity"] = float(corrected[1, 0])

            track["displacement"] = (
                track["current_x"] - track["initial_x"]
            )

            track["hits"] += 1
            track["consecutive_hits"] += 1
            track["misses"] = 0

            track["history"].append(track["current_x"])

            # Confirm only after enough successful detections
            if track["consecutive_hits"] >= self.confirmation_frames:

                track["state"] = "confirmed"

            else:

                track["state"] = "tentative"

    # --------------------------------------------------
    # Compare edge velocities and estimate container velocity
    # --------------------------------------------------

    def _update_container_velocity(self, matches):

        # Only tracks matched THIS frame have fresh velocities
        matched_tracks = [
            self._tracks[track_index]
            for track_index, _ in matches
        ]

        confirmed = [
            track for track in matched_tracks
            if track["state"] == "confirmed"
        ]

        # Reliable = confirmed and moving consistently with the others
        reliable = [
            track for track in confirmed
            if track["movement_valid"]
        ]

        if len(reliable) < self.min_tracks_for_container:

            # Not enough edges to compare against each other
            for track in confirmed:
                track["velocity_error"] = 0.0
                track["velocity_valid"] = True

            return

        velocities = np.array(
            [track["velocity"] for track in reliable],
            dtype=np.float64
        )

        # Median is robust against a few bad edges
        median_velocity = float(np.median(velocities))

        # Robust spread estimate (MAD scaled to a standard deviation)
        mad = float(np.median(np.abs(velocities - median_velocity)))
        sigma = 1.4826 * mad

        measured_var = float(
            np.clip(
                sigma ** 2,
                self.min_velocity_var,
                self.default_velocity_var
            )
        )

        # Smooth the container velocity over time
        if not self.has_container_velocity:

            self.container_velocity = median_velocity
            self.has_container_velocity = True

        else:

            alpha = self.velocity_smoothing

            self.container_velocity = (
                alpha * median_velocity
                + (1.0 - alpha) * self.container_velocity
            )

        self.container_velocity_var = measured_var

        # Compare every confirmed edge's velocity to the group median
        for track in confirmed:

            error = abs(track["velocity"] - median_velocity)

            track["velocity_error"] = float(error)

            track["velocity_valid"] = (
                error <= self.velocity_threshold
            )

    # --------------------------------------------------
    # Manage missing tracks and new detections
    # --------------------------------------------------

    def _manage_track_lifecycle(
        self,
        unmatched_tracks,
        unmatched_detections,
        detections,
        width
    ):

        # Number of tracks BEFORE any deletion, to compare with detections
        num_tracks = len(self._tracks)

        # Handle missing tracks
        for track_index in unmatched_tracks:

            track = self._tracks[track_index]

            track["misses"] += 1
            track["consecutive_hits"] = 0

            if track["misses"] > self.max_missing_frames:

                track["state"] = "deleted"

            else:

                track["state"] = "lost"

        # Remove deleted tracks
        self._tracks = [
            track for track in self._tracks
            if track["state"] != "deleted"
        ]

        # New edges: only when there are more detections than tracks
        excess = len(detections) - num_tracks

        if excess <= 0:
            return

        # `detections` is sorted in the truck's direction of travel, so the
        # first `excess` detections are the ones on the entry side.
        unmatched_set = set(unmatched_detections)

        for detection_index in range(excess):

            if detection_index not in unmatched_set:
                continue    # already matched to an existing track

            x = detections[detection_index]

            if self._is_in_entry_zone(x, width):

                self._create_track(x)    # starts as "tentative"

    # --------------------------------------------------
    # Main update function
    # --------------------------------------------------

    def update(self, detected_edges, width):

        self.frame_count += 1

        # 1. Predict existing tracks
        self._predict_tracks()

        # 2. Associate detections
        (
            matches,
            unmatched_tracks,
            unmatched_detections,
            detections
        ) = self._associate_detections(detected_edges)

        # 3. Validate collective movement
        self._validate_collective_movement(
            matches,
            detections
        )

        # 4. Correct Kalman Filters
        self._update_tracks(
            matches,
            detections
        )

        # 5. Compare edge velocities, update container velocity
        self._update_container_velocity(matches)

        # 6. Manage new and missing tracks
        self._manage_track_lifecycle(
            unmatched_tracks,
            unmatched_detections,
            detections,
            width
        )

        return self.get_confirmed_edges()

    # --------------------------------------------------
    # Get confirmed edges
    # --------------------------------------------------

    def get_confirmed_edges(self):

        return [
            {
                "id": track["id"],
                "x": track["current_x"],
                "velocity": track["velocity"],
                "displacement": track["displacement"],
                "state": track["state"],
                "collective_error": track["collective_error"],
                "velocity_error": track["velocity_error"],
                "velocity_valid": track["velocity_valid"]
            }
            for track in self._tracks
            if track["state"] == "confirmed"
        ]

    # --------------------------------------------------
    # Get all tracks
    # --------------------------------------------------
    @property
    def tracks(self):

        return tuple(self._tracks)

    # --------------------------------------------------
    # Get displacements
    # --------------------------------------------------
    @property
    def displacements(self):

        return {
            track["id"]: track["displacement"]
            for track in self._tracks
            if track["state"] == "confirmed"
        }