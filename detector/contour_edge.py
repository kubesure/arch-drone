from drone_types import Ring,RingColor
#from drone_types import Ring
import config_loader
from detector import contour
from detector import edge

def get_ring_cords(cords,RingColor):
        if cords is not None:
            x,y,z,area = cords
            Ring(height=y,x=x,distance=z,area=area,color=RingColor) 
        else: 
            None     

#call contour and edge detector
def get_xyz_rings(frame,rings_sequence):
 
    config = config_loader.get_configurations()
    contour_detector = contour.ContourDector(config)
    edge_detector = edge.EdgeDector(config)
    cords = []
    for ring in rings_sequence:
        red, yellow = contour_detector.get_color_frame(frame)  
     
        if ring == RingColor.RED:
            red_cords = edge_detector.get_x_y_z(red)
            red_ring = get_ring_cords(red_cords)
            if get_ring_cords(red_cords) is not None:
                cords.append(red_ring)

        if ring == RingColor.YELLOW:
            yellow_cords = edge_detector.get_x_y_z(yellow)   
            yellow_ring = get_ring_cords(yellow_cords)
            if get_ring_cords(red_cords) is not None:
                cords.append(yellow_ring)
    return cords
    

