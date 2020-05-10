

def get_corners(x, y, width, height):

    p1 = (x, y)
    p2 = (x, y+height)
    p3 = (x+width, y)
    p4 = (x+width, y+height)

    return p1, p2, p3, p4

def get_corners_rect_child(child_element):

    geometry = child_element[0]
    x, y = float(geometry.attrib["x"]), float(geometry.attrib["y"])
    width, height = float(geometry.attrib["width"]), float(geometry.attrib["height"])
    p1, p2, p3, p4 = get_corners(x, y, width, height)

    return p1, p2, p3, p4