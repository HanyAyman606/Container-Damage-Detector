import cv2

from core.edge_detector import EdgeDetector
from core.brightness_calc import BrightnessDetector


def main():

    # 1. Read test image
    image = cv2.imread("images/test.jpg")

    if image is None:
        raise ValueError("Could not read the test image")

    # 2. Create detector instances
    edge_detector = EdgeDetector(threshold=50)

    brightness_detector = BrightnessDetector(
        thresh=100,
        std_thresh=20
    )

    # 3. Get vertical regions
    regions = edge_detector.get_vertical_regions(image)

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
            anomaly_area = brightness_detector.calculate_damage_area()

            total_anomaly_area += anomaly_area

        # classify region as Crest or Trough // necessary but later
        classification = brightness_detector.Crest_or_Trough()

        print(f"Region: {region}")
        print(f"Classification: {classification}")

    # 6. Check vertical edge damage
    edge_results, edge_damage = edge_detector.check_edges_damage(image)

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

    for result in edge_results:
        print(result)


if __name__ == "__main__":
    main()
