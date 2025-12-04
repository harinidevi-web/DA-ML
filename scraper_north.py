from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
import cv2
import csv
import os
import numpy as np

def generate_tile_centers(lat_start, lat_end, lon_start, lon_end, step=0.01):
    tile_centers = []
    lat = lat_start
    while lat <= lat_end:
        lon = lon_start
        while lon <= lon_end:
            tile_centers.append((round(lat, 4), round(lon, 4)))
            lon += step
        lat += step
    return tile_centers

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=800,600")
    return webdriver.Chrome(options=options)

def main():
    lat_start, lat_end = 13.15, 13.25
    lon_start, lon_end = 79.95, 80.40

    step = 0.01
    tile_centers = generate_tile_centers(lat_start, lat_end, lon_start, lon_end, step)
    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    driver = setup_driver()
    csv_file = "traffic_data.csv"
    is_new = not os.path.exists(csv_file)

    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        if is_new:
            writer.writerow(["Timestamp", "Latitude", "Longitude", "RedPixels", "OrangePixels", "GreenPixels"])

        for index, (lat, lon) in enumerate(tile_centers):
            print(f"[{index+1}/{len(tile_centers)}] {lat}, {lon}")
            url = f"https://www.google.com/maps/@{lat},{lon},14z/data=!5m1!1e1"
            driver.get(url)
            time.sleep(6)

            # Get screenshot as bytes and convert to OpenCV format
            screenshot_bytes = driver.get_screenshot_as_png()
            img_array = np.frombuffer(screenshot_bytes, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            red = cv2.inRange(hsv, (0, 100, 100), (10, 255, 255))
            orange = cv2.inRange(hsv, (11, 100, 100), (25, 255, 255))
            green = cv2.inRange(hsv, (40, 50, 50), (90, 255, 255))
            r, o, g = cv2.countNonZero(red), cv2.countNonZero(orange), cv2.countNonZero(green)

            writer.writerow([timestamp, lat, lon, r, o, g])

    driver.quit()
    print(f"\n✅ North Chennai scraping done at {timestamp}")

if __name__ == "__main__":
    main()
