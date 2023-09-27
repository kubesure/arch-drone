from drone_types import Ring
from collections import Counter


def find_best(rings) -> (bool, Ring):
    best_ring = Ring
    for r in rings:
        best_ring = Ring(x=34, y=45, z=150, area=0, color=r.ring)
    return True, best_ring


def ring_detected(r: Ring) -> (bool, Ring):
    if r.z == 0 or r.y == 0 or r.y == 0:
        return False, Ring
    return True, r


def get_short_or_longest_distance(rings, longest) -> (bool, Ring):
    print(f"finding short of long ring out of rings {len(rings)}")
    if len(rings) == 0:
        return False, None
    sorted_rings = sorted(rings, key=lambda ring: ring.z, reverse=longest)
    return True, sorted_rings[0]


def get_avg_distance(rings) -> (bool, Ring):
    print(f"Ring for average {len(rings)}")
    rings_to_consider = get_percentage_rings(rings, .50)

    print(f"total rings {len(rings)} rings considered for avg {len(rings_to_consider)}")

    avg_x = int(sum(ring.x for ring in rings_to_consider) / len(rings_to_consider))
    avg_y = int(sum(ring.y for ring in rings_to_consider) / len(rings_to_consider))
    avg_z = int(sum(ring.z for ring in rings_to_consider) / len(rings_to_consider))
    avg_area = int(sum(ring.area for ring in rings_to_consider) / len(rings_to_consider))
    color_counts = Counter(ring.color for ring in rings_to_consider)
    avg_color = color_counts.most_common(1)[0][0]
    average_ring = Ring(x=avg_x, y=avg_y, z=avg_z, area=avg_area, color=avg_color)
    print(f"Returning avg ring {average_ring}")
    return True, average_ring


def get_percentage_rings(rings, percent_to_discard):
    num_to_consider = int(len(rings) * (1 - percent_to_discard))
    rings_to_consider = rings[-num_to_consider:]
    return rings_to_consider
