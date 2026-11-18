import cv2
import numpy as np

class EdgeDetector:

    def __init__(self, threshold=50):
        self.threshold = threshold

    def _vertical_edges(self, image):
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

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

        return binary_edges,gray

  
    def _preprocess_vertical_edges(self, image, min_distance=10):

        edges, gray = self._vertical_edges(image)

        height, width = edges.shape

        # Count edge pixels in each column
        column_scores = np.count_nonzero(edges, axis=0)

        edge_threshold = height * 0.5

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

        # Calculate average X position of each edge
        edge_centers = []

        for group in grouped_edges:

            ys, xs = np.where(edges[:, group] > 0)

            actual_xs = np.array(group)[xs]

            average_x = int(np.mean(actual_xs))

            edge_centers.append(average_x)

        return edges, gray, grouped_edges, edge_centers

    def get_vertical_regions(self, image, min_distance=10):

        edges, gray, grouped_edges, edge_centers = \
            self._preprocess_vertical_edges(image, min_distance)

        height, width = edges.shape

        boundaries = [0] + edge_centers + [width]

        regions = []

        for i in range(len(boundaries) - 1):

            start_x = boundaries[i]
            end_x = boundaries[i + 1]

            if end_x > start_x:
                regions.append((start_x, end_x))

        return regions

    def check_edges_damage(self, image, min_distance=10,
                       min_height_ratio=0.9, max_deviation=3):

        edges, _, grouped_edges, _ = \
            self._preprocess_vertical_edges(image, min_distance)

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

            # Fit a straight line
            coefficients = np.polyfit(ys, x_positions, 1)

            predicted_x = np.polyval(coefficients, ys)

            # Calculate deviation of average edge positions
            deviations = np.abs(x_positions - predicted_x)

            max_error = np.max(deviations)

            # Count curved pixels
            curved_pixels = 0

            for i, row in enumerate(ys):

                xs = np.where(component[row])[0]
                actual_xs = np.array(group)[xs]

                pixel_deviations = np.abs(
                    actual_xs - predicted_x[i]
                )

                curved_pixels += np.count_nonzero(
                    pixel_deviations > max_deviation
                )

            total_damage += height - len(ys) + curved_pixels
            # Determine edge condition
            is_continuous = coverage >= min_height_ratio
            is_straight = max_error <= max_deviation

            results.append({
                "edge_center": int(np.mean(group)),
                "coverage": coverage,
                "max_deviation": max_error,
                "curved_pixels": curved_pixels,
                "is_continuous": is_continuous,
                "is_straight": is_straight,
                "is_damaged": not (is_continuous and is_straight)
            })

        return results, total_damage  ;''' that's the total damage for one snapshot
                                        to be accumulated with the rest of damages in the other snapshots
        '''