import cv2

from core.edge_detector import EdgeDetector
from core.brightness_calc import BrightnessDetector


def main():

    # 1. Read test image
    image = cv2.imread("test_data/cropped_container2_2.jpg")

    debug_image=image

    if image is None:
        raise ValueError("Could not read the test image")

    # 2. Create detector instances
    edge_detector = EdgeDetector(threshold=50)

    brightness_detector = BrightnessDetector(
        thresh=100,
        std_thresh=20
    )

    # 3. Get vertical regions
    edge_detector.image=image
    regions = edge_detector.get_vertical_regions()

    # 4. Initialize damage counters for this snapshot
    total_anomaly_area = 0
    total_snapshot_area = 0

    # 5. Process each region
    brightness_detector.image = image

    for region in regions:

        # Assign region boundaries
        brightness_detector.bounds = region

        # Calculate region area
        start_x, end_x = region
        region_area = image.shape[0] * (end_x - start_x)

        total_snapshot_area += region_area

        # Check for holes and tears
        if brightness_detector.Holes_and_Tears():

            # Calculate anomaly area
            anomaly_area = brightness_detector.calculate_damage_area(debug_image=debug_image)

            total_anomaly_area += anomaly_area

        # classify region as Crest or Trough // necessary but later
        classification = brightness_detector.Crest_or_Trough()
        #//////////////////////////
        center_x = (start_x + end_x) // 2
        label = "1" if classification == "Crest" else "0"

        # Measure rendered text width so the label is truly centred
        # between the two boundary lines regardless of region width.
        (text_w, _), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
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

    # 6. Check vertical edge damage
    
    edge_results, edge_damage, debug_image = edge_detector.check_edges_damage(debug_image=debug_image)

    # 7. Add edge damage to the anomaly area
    total_anomaly_area += edge_damage

    # 8. Calculate snapshot damage percentage
    damage_percentage = (
        (total_anomaly_area / total_snapshot_area) * 100
        if total_snapshot_area > 0 else 0
    )

    # 9. Display results
    print("\n========== SNAPSHOT RESULTS ==========")

    print(f"Number of regions: {len(regions)}")
    print(f"Total snapshot area: {total_snapshot_area} pixels")
    print(f"Brightness anomaly area: {total_anomaly_area - edge_damage} pixels")
    print(f"Edge damage: {edge_damage} pixels")
    print(f"Total damaged area: {total_anomaly_area} pixels")
    print(f"Damage percentage: {damage_percentage:.2f}%")

    print("\nEdge details:")
    cv2.imwrite('debug/debug_image.png',debug_image)
    for result in edge_results:
        print(result)


if __name__ == "__main__":
    main()
