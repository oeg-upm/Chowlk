

def get_corners(x, y, width, height):

    p1 = (x, y)
    p2 = (x, y+height)
    p3 = (x+width, y)
    p4 = (x+width, y+height)

    return p1, p2, p3, p4


def get_corners_rect_child(child_element):

    geometry = child_element[0]
    x = float(geometry.attrib["x"]) if "x" in geometry.attrib else 0
    y = float(geometry.attrib["y"]) if "y" in geometry.attrib else 0
    width, height = float(geometry.attrib["width"]), float(geometry.attrib["height"])
    p1, p2, p3, p4 = get_corners(x, y, width, height)

    return p1, p2, p3, p4


def proximity_to_shape(point, xml_shape, thr):

    p1, _, _, p4 = get_corners_rect_child(xml_shape)

    if abs(p1[0] - point[0]) <= thr and p1[1] <= point[1] <= p4[1]:
        near = True
    elif abs(p1[1] - point[1]) <= thr and p1[0] <= point[0] <= p4[0]:
        near = True
    elif abs(p4[0] - point[0]) <= thr and p1[1] <= point[1] <= p4[1]:
        near = True
    elif abs(p4[1] - point[1]) <= thr and p1[0] <= point[0] <= p4[0]:
        near = True
    else:
        near = False

    return near