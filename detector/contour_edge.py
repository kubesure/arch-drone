from drone_types import Ring,RingColor
#from drone_types import Ring
import config_loader
from detector import contour_v1
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
    contour_detector = contour_v1.ContourDector(config)
    edge_detector = edge.EdgeDector(config)
    cords = []
    for ring in rings_sequence:
        ring_data = contour_detector.get_colored_rings(frame)  
     
        if ring == RingColor.RED:
            red_cords = edge_detector.get_x_y_z(ring_data.red_mask)
            red_ring = get_ring_cords(red_cords,RingColor.RED)
            if red_ring is not None:
                cords.append(red_ring)

        if ring == RingColor.YELLOW:
            yellow_cords = edge_detector.get_x_y_z(ring_data.yellow_mask)   
            yellow_ring = get_ring_cords(yellow_cords,RingColor.YELLOW)
            if yellow_ring is not None:
                cords.append(yellow_ring)
    return cords
    

