

def find_missing_source_target(property_restrictions, object_properties, sources_targets):

    """ Function to find the source and target of floating edges, for now it only works for
    edges that support the relation between two other edges, it can be extended for other cases"""

    # Under this scope restrictions are all relations that indicate relationships
    # between other object properties
    for restriction in property_restrictions:

        child = restriction["xml_object"]

        geom_property = child[0]
        for elem in geom_property:
            if elem.attrib["as"] == "sourcePoint":
                x_source, y_source = float(elem.attrib["x"]), float(elem.attrib["y"])
            elif elem.attrib["as"] == "targetPoint":
                x_target, y_target = float(elem.attrib["x"]), float(elem.attrib["y"])

        # Iteration to look for other edges as possibles sources
        for property in object_properties:
            child2 = property["xml_object"]
            #for child2 in root:
            # We are considering the simple scenario in which the supporting or
            # reference edges have source and target, however this is not always the situation
            #source_child2 = child2.attrib["source"]
            #target_child2 = child2.attrib["target"]
            source_child2 = property["source"]
            target_child2 = property["target"]

            # Look for the source object and extract its geometry
            for shape in sources_targets:
                #for child3 in root:
                child3 = shape["xml_object"]
                if source_child2 == shape["id"]:
                    s_shape_x, s_shape_y = child3[0].attrib["x"], child3[0].attrib["y"]
                    s_shape_width, s_shape_height = child3[0].attrib["width"], child3[0].attrib["height"]
                    break
            # Now compute the geometry of the initial source point of the edge
            exitX = child2.attrib["style"].split("exitX=")[1].split(";")[0]
            exitY = child2.attrib["style"].split("exitY=")[1].split(";")[0]
            x_source_ref = float(s_shape_x) + float(s_shape_width) * float(exitX)
            y_source_ref = float(s_shape_y) + float(s_shape_height) * float(exitY)
            source_point_ref = [x_source_ref, y_source_ref]

            # Look for the target object and extract its geometry
            for shape in sources_targets:
                #for child3 in root:
                if target_child2 == shape["id"]:
                    t_shape_x, t_shape_y = child3[0].attrib["x"], child3[0].attrib["y"]
                    t_shape_width, t_shape_height = child3[0].attrib["width"], child3[0].attrib["height"]
                    break
            # Now compute the geometry of the initial source point of the edge
            entryX = child2.attrib["style"].split("entryX=")[1].split(";")[0]
            entryY = child2.attrib["style"].split("entryY=")[1].split(";")[0]
            x_target_ref = float(t_shape_x) + float(t_shape_width) * float(entryX)
            y_target_ref = float(t_shape_y) + float(t_shape_height) * float(entryY)
            target_point_ref = [x_target_ref, y_target_ref]

            # We have to determine how many inflexion points it have, however sometimes it is
            # not indicated explicitly and have to be derived from the associated shapes.
            # Try to iter over the mxGeom elements, if they exist
            elem = [i for i in child2[0] if i.attrib["as"] == "points"]
            # if you found an element with the attribute "points", Eureka!
            if len(elem) != 0:
                #for elem in child2[0]:
                #if elem.attrib["as"] == "points":
                elem = elem[0]
                points_ref = []
                for mxPoint in elem:
                    point = [float(mxPoint.attrib["x"]), float(mxPoint.attrib["y"])]
                    points_ref.append(point)
                points_ref.insert(0, source_point_ref)
                points_ref.append(target_point_ref)

                # At this point you already have all the points for a candidate line
                # We are going to evaluate each segment of the candidate line
                for index in range(len(points_ref) - 1):
                    point_A = points_ref[index]
                    point_B = points_ref[index + 1]

                    if point_A[0] > point_B[0]:
                        min_x, max_x = point_B[0], point_A[0]
                    else:
                        min_x, max_x = point_A[0], point_B[0]

                    if point_A[1] > point_B[1]:
                        min_y, max_y = point_B[1], point_A[1]
                    else:
                        min_y, max_y = point_A[1], point_B[1]

                    if restriction["source"] is None:
                        if x_source > min_x - 5 and x_source < max_x + 5:
                            x_within_limit = True
                        else:
                            x_within_limit = False
                        if y_source > min_y - 5 and y_source < max_y + 5:
                            y_within_limit = True
                        else:
                            y_within_limit = False
                        if x_within_limit and y_within_limit:
                            restriction["source"] = property["id"]
                            break
                    if restriction["target"] is None:
                        if x_target > min_x - 5 and x_target < max_x + 5:
                            x_within_limit = True
                        else:
                            x_within_limit = False
                        if y_target > min_y - 5 and y_target < max_y + 5:
                            y_within_limit = True
                        else:
                            y_within_limit = False
                        if x_within_limit and y_within_limit:
                            restriction["target"] = property["id"]
                            break

                if restriction["source"] is not None and restriction["target"] is not None:
                    break

            else:
                # Sometimes we have straight lines and the process is simple to evaluate
                if x_source_ref == x_target_ref or y_source_ref == y_target_ref:

                    point_A = [x_source_ref, y_source_ref]
                    point_B = [x_target_ref, y_target_ref]

                    if point_A[0] > point_B[0]:
                        min_x, max_x = point_B[0], point_A[0]
                    else:
                        min_x, max_x = point_A[0], point_B[0]

                    if point_A[1] > point_B[1]:
                        min_y, max_y = point_B[1], point_A[1]
                    else:
                        min_y, max_y = point_A[1], point_B[1]

                    if restriction["source"] is None:
                        if x_source > min_x - 5 and x_source < max_x + 5:
                            x_within_limit = True
                        else:
                            x_within_limit = False
                        if y_source > min_y - 5 and y_source < max_y + 5:
                            y_within_limit = True
                        else:
                            y_within_limit = False
                        if x_within_limit and y_within_limit:
                            restriction["source"] = property["id"]
                            break
                    if restriction["target"] is None:
                        if x_target > min_x - 5 and x_target < max_x + 5:
                            x_within_limit = True
                        else:
                            x_within_limit = False
                        if y_target > min_y - 5 and y_target < max_y + 5:
                            y_within_limit = True
                        else:
                            y_within_limit = False
                        if x_within_limit and y_within_limit:
                            restriction["target"] = property["id"]
                            break
