import cv2
import numpy as np
import time

from core.edge_detector import EdgeDetector
from core.brightness_calc import BrightnessDetector


def main():
    start_time = time.perf_counter()
    # 1. Read test image
    image = cv2.imread("test_data/cropped_container2_2.jpg")

    if image is None:
        raise ValueError("Could not read the test image")

    debug_image = image.copy()

    # 2. Create detector instances
    edge_detector = EdgeDetector(threshold=50)

    brightness_detector = BrightnessDetector()

    # 3. Get vertical regions
    edge_detector.image = image
    regions = edge_detector.get_vertical_regions()

    # 4. Initialize damage counters for this snapshot
    total_anomaly_area = 0
    total_snapshot_area = 0

    # Store the brightness reference for every region
    region_brightness = []

    # 5. Process each region
    brightness_detector.image = image

    for region in regions:

        # Assign region boundaries
        brightness_detector.bounds = region

        # Calculate region area
        start_x, end_x = region
        region_area = image.shape[0] * (end_x - start_x)

        total_snapshot_area += region_area

        # Calculate anomaly area and majority brightness
        anomaly_area, majority_brightness = (
            brightness_detector.calculate_damage_area(
                debug_image=debug_image
            )
        )

        region_brightness.append(majority_brightness)
        
        total_anomaly_area += anomaly_area

        print(f"Region: {region}")
        print(f"Majority brightness: {majority_brightness:.2f}")

    # 6. Classify regions using the brightest region as the Crest reference
    if region_brightness:

        crest_index = int(np.argmax(region_brightness))

        print(f"\nCrest reference region: {regions[crest_index]}")

        for i, region in enumerate(regions):

            if (i - crest_index) % 2 == 0:
                classification = "Crest"
            else:
                classification = "Trough"

            # Draw classification label
            start_x, end_x = region
            center_x = (start_x + end_x) // 2

            label = "1" if classification == "Crest" else "0"

            (text_w, _), _ = cv2.getTextSize(
                label,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                2
            )

            cv2.putText(
                debug_image,
                label,
                (center_x - text_w // 2, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2
            )

            print(f"Region: {region}")
            print(f"Classification: {classification}")

    # 7. Check vertical edge damage
    edge_results, edge_damage, debug_image = (
        edge_detector.check_edges_damage(debug_image=debug_image)
    )

    # 8. Add edge damage to the anomaly area
    total_anomaly_area += edge_damage

    # 9. Calculate snapshot damage percentage
    damage_percentage = (
        (total_anomaly_area / total_snapshot_area) * 100
        if total_snapshot_area > 0 else 0
    )

    # 10. Display results
    print("\n========== SNAPSHOT RESULTS ==========")

    print(f"Number of regions: {len(regions)}")
    print(f"Total snapshot area: {total_snapshot_area} pixels")
    print(f"Brightness anomaly area: {total_anomaly_area - edge_damage} pixels")
    print(f"Edge damage: {edge_damage} pixels")
    print(f"Total damaged area: {total_anomaly_area} pixels")
    print(f"Damage percentage: {damage_percentage:.2f}%")

    print("\nEdge details:")
    for result in edge_results:
        print(result)

    # Save debug image
    cv2.imwrite("debug/debug_image1.png", debug_image)

    end_time = time.perf_counter()

    execution_time = end_time - start_time

    print(f"\nTotal execution time: {execution_time:.4f} seconds")
    print(f"FPS: {1 / execution_time:.2f}")
if __name__ == "__main__":
    main()