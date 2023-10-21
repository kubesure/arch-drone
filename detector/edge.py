import cv2
import constants


class EdgeDetector:
    def __init__(self):
        pass

    def convert_circle_cm(self, x_pixel, y_pixel, r_pixel, scaling_factor):
        x_cm = x_pixel * scaling_factor
        y_cm = y_pixel * scaling_factor
        r_cm = r_pixel * scaling_factor
        return x_cm, y_cm, r_cm

    def get_x_y_z(self, frame):
        # area_red_cms = math.pi * (constants.diameter_red_cms / 2) ** 2
        # area_red_pixel = area_red_cms * constants.k1 ** 2
        known_radius_red_cm = 28

        bilateral_filtered_image = cv2.bilateralFilter(frame, 5, 175, 175)
        edge_detected_image = cv2.Canny(bilateral_filtered_image, 75, 200)

        contours, _ = cv2.findContours(edge_detected_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            # eliminate small contours
            if area > 600:
                # print(f"area_red_pixel: {area_red_pixel} area {area}")
                (x, y), radius_pixel = cv2.minEnclosingCircle(contour)
                scaling_factor = known_radius_red_cm / radius_pixel
                # Calculate pixel radius to cms radius can be used to
                # Eliminate anything not red and yellow rings in radius
                scale_cm_per_pixel = known_radius_red_cm / radius_pixel
                actual_radius_cm = radius_pixel * scale_cm_per_pixel

                # Diameter in pixel required for distance
                d_image_in_pixel = 2 * radius_pixel
                # Calculate distance
                z = (constants.fx * constants.diameter_red_cms) / d_image_in_pixel
                x_cm, y_cm, _ = self.convert_circle_cm(x, y, radius_pixel, scaling_factor)
                print(
                    f"radius {actual_radius_cm} d_image {d_image_in_pixel} "
                    f"x: {x_cm} height: {y_cm} distance: {z} area: {area}")
                # draw ring contour
                cv2.drawContours(frame, [contour], -1, (255, 0, 0), 2)
                center_color = (0, 0, 0)
                center_radius = 3
                # draw center black circle
                cv2.circle(frame, (int(x), int(y)), center_radius, center_color, -1)
                return x, y, z, area
