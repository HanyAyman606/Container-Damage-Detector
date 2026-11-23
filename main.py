import cv2 as cv
import sys

from core.edge_detector import EdgeDetector
from core.brightness_calc import BrightnessDetector

video_path = sys.argv[1] if len(sys.argv) > 1 else 0

flag=True

def main():
    cap=cv.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()

    while True:
        ret,frame=cap.read()
        if not ret:
            print("End of video or cannot read frame.")
            break

        edge_obj=EdgeDetector()
        bright_obj=BrightnessDetector()
        edge_obj.image=frame
        bright_obj.image=frame

        total_container_dmg=0
        total_area=0

        if flag:
            snap_dmg=pipeline(edge_obj,bright_obj)
            total_container_dmg+=snap_dmg
            h,w,_=frame.shape
            total_area+=w*h
    

def pipeline(edge_obj,bright_obj):
    regions=edge_obj.get_vertical_regions()
    results,edges_damage,debug_img=edge_obj.check_edges_damage()
    total_anomaly_area=0
    max_region_brightness=0
    index_max=0
    for index,region in enumerate(regions):
        bright_obj.bounds=region

        anomaly_area, majority_brightness, debug_img = bright_obj.calculate_damage_area(debug_img)
        total_anomaly_area+=anomaly_area
        if majority_brightness>max_region_brightness:
            max_region_brightness= majority_brightness
            index_max=index
    Crest_or_Trough=[]
    for i,region in enumerate(regions):
        if (i-index_max)%2==0:
            classification='1'
        else:
            classification='0'
        Crest_or_Trough.append(classification)
        
        (text_w, _), _ = cv.getTextSize(
            classification,
            cv.FONT_HERSHEY_SIMPLEX,
            0.6,
            2
        )
        start_x,end_x=region
        center_x=(end_x-start_x)//2
        cv.putText(
            debug_img,
            classification,
            (center_x - text_w // 2, 30),
            cv.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 0, 0),
            2
        )


    total_img_damage=edges_damage + anomaly_area
    print(f"edges data:\n{results}\nimage damage= {total_img_damage}\n")
    #cv.imwrite("debug_image",debug_img)
    return total_img_damage

if __name__ == "__main__":
    main()