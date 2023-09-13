from drone_types import Ring,RingColor

def get_xyz_red_ring(frame):
    pass

def get_xyz_yellow_ring(frame):
    pass

#call contour and edge detector
def get_xyz_rings(frame,rings_sequence):
    red = Ring(height=250,x=35,distance=350,color=RingColor.RED) 
    yellow = Ring(height=250,x=35,distance=350,color=RingColor.YELLOW) 
    return [red,yellow]
    

