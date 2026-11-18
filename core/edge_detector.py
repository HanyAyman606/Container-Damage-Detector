import cv2
import numpy as np

class EdgeDetector:

    def __init__(self, threshold=50):
        self.threshold = threshold
        self._image=None
    

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self,value):
        self._image=value

    def _vertical_edges(self):
        # Convert to grayscale
        gray = cv2.cvtColor(self._image, cv2.COLOR_BGR2GRAY)

        # Apply Sobel in X direction
        sobel_x = cv2.Sobel(
            gray, cv2.CV_64F, 1, 0, ksize=3
        )

        # Convert to absolute values
        edges = cv2.convertScaleAbs(sobel_x)

        # Apply threshold
        _, binary_edges = cv2.threshold(
            edges, self.threshold, 255, cv2.THRESH_BINARY
        )
        #////////////////////////////////////////////////
        #saving the result of sobel filter for troubleshoot purpose
        cv2.imwrite("debug/edges.png", binary_edges)
        #///////////////////////////////////////////////

        return binary_edges,gray

  
    def _preprocess_vertical_edges(self, min_distance=10):

        edges, gray = self._vertical_edges()

        height, width = edges.shape

        # Close vertical gaps within each column before scoring.
        # A tall, 1-pixel-wide kernel bridges illumination-caused breaks
        # inside a real edge column without spreading it left or right.
        close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, close_kernel)

        # Count edge pixels in each column
        column_scores = np.count_nonzero(edges, axis=0)

        # Lowered from 0.5 to 0.25: after gap-closing, real edge columns
        # score much higher, so a 25%-of-height bar is sufficient.
        edge_threshold = height * 0.25

        edge_positions = np.where(
            column_scores >= edge_threshold
        )[0]

        # Group neighboring edge columns
        grouped_edges = []

        for x in edge_positions:

            if not grouped_edges or x - grouped_edges[-1][-1] > min_distance:
                grouped_edges.append([x])
            else:
                grouped_edges[-1].append(x)

        # Discard single-column groups: they are almost always weak
        # secondary Sobel responses at corrugation shoulders, not true edges.
        grouped_edges = [g for g in grouped_edges if len(g) >= 2]

        # Calculate average X position of each edge
        edge_centers = []

        for group in grouped_edges:

            ys, xs = np.where(edges[:, group] > 0)

            actual_xs = np.array(group)[xs]

            average_x = int(np.mean(actual_xs))

            edge_centers.append(average_x)

        return edges, gray, grouped_edges, edge_centers

    def get_vertical_regions(self, min_distance=10):

        edges, gray, grouped_edges, edge_centers = \
            self._preprocess_vertical_edges(min_distance)

        height, width = edges.shape

        boundaries = [0] + edge_centers + [width]

        regions = []

        for i in range(len(boundaries) - 1):

            start_x = boundaries[i]
            end_x = boundaries[i + 1]

            if end_x > start_x:
                regions.append((start_x, end_x))

        return regions

    def check_edges_damage(self, min_distance=10,
                       min_height_ratio=0.6, max_deviation=3, debug_image=None):
        if debug_image is None:
            debug_image=self._image
        edges, _, grouped_edges, _ = \
            self._preprocess_vertical_edges(min_distance)

        height, width = edges.shape

        results = []

        total_damage = 0
        total_curved_pixels = 0

        for group in grouped_edges:

            # Extract edge pixels belonging to this group
            component = edges[:, group] > 0

            # Find rows containing edge pixels
            ys = np.where(np.any(component, axis=1))[0]

            # Calculate vertical coverage
            coverage = len(ys) / height

            
            

            # Skip line fitting if there are insufficient points
            if len(ys) < 2:
                continue

            # Calculate average X position in each row
            x_positions = []

            for row in ys:

                xs = np.where(component[row])[0]
                actual_xs = np.array(group)[xs]

                x_positions.append(np.mean(actual_xs))

            x_positions = np.array(x_positions)

            # Fit a straight line through the edge's average x-positions
            coefficients = np.polyfit(ys, x_positions, 1)
            predicted_x = np.polyval(coefficients, ys)

            # Deviation from the FITTED line measures local wobble,
            # but a globally tilted or bent edge keeps all residuals small
            # because polyfit tilts WITH the bend.  Instead, also measure
            # deviation from a true vertical anchored at the top of the edge
            # (x = constant = x_positions[0]).  The larger of the two gives
            # a reliable signal for both local kinks and global bends.
            vertical_ref  = np.full_like(predicted_x, x_positions[0])
            deviations    = np.maximum(
                np.abs(x_positions - predicted_x),   # local wobble
                np.abs(x_positions - vertical_ref),  # global drift from top
            )

            max_error = np.max(deviations)

            # Determine edge condition
            is_continuous = coverage >= min_height_ratio
            is_straight = max_error <= max_deviation
            if not is_continuous:
                line_color = (255, 0, 255)  # Magenta: short/incomplete edge
            else:
                line_color = (0, 255, 0)    # Green: sufficient vertical coverage

            # Draw the predicted reference line first so edge points appear on top
            p1 = (int(predicted_x[0]), int(ys[0]))
            p2 = (int(predicted_x[-1]), int(ys[-1]))
            cv2.line(
                debug_image,
                p1,
                p2,
                line_color,
                2
            )

            # Count curved rows and draw edge points
            curved_pixels = 0

            for i, row in enumerate(ys):

                # Use combined deviation (local kink or global drift)
                row_deviation = deviations[i]

                if row_deviation > max_deviation:
                    curved_pixels += 1   # one damaged row, not one per pixel

                    # Draw damaged / curved row in yellow
                    cv2.circle(
                        debug_image,
                        (int(x_positions[i]), int(row)),
                        2,
                        (0, 255, 255),
                        -1
                    )
                else:
                    # Draw normal / straight edge row in red
                    cv2.circle(
                        debug_image,
                        (int(x_positions[i]), int(row)),
                        2,
                        (0, 0, 255),
                        -1
                    )

            total_damage += height - len(ys) + curved_pixels

            results.append({
                "edge_center": int(np.mean(group)),
                "coverage": coverage,
                "max_deviation": max_error,
                "curved_pixels": curved_pixels,
                "is_continuous": is_continuous,
                "is_straight": is_straight,
                "is_damaged": not (is_continuous and is_straight)
            })

        return results, total_damage, debug_image  ;''' that's the total damage for one snapshot
                                        to be accumulated with the rest of damages in the other snapshots
        '''