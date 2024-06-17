def find_prefixes(diagram_model):

    classes = diagram_model.get_classes()
    arrows = diagram_model.get_arrows()
    datatype_properties = diagram_model.get_datatype_properties()
    individuals = diagram_model.get_individuals()
    property_values = diagram_model.get_property_values()
    metadata = diagram_model.get_metadata()

    prefixes = []

    prefixes = find_prefixes_elements(prefixes, classes)

    prefixes = find_prefixes_elements(prefixes, arrows)

    prefixes = find_prefixes_elements(prefixes, individuals)

    prefixes = find_prefixes_datatype_properties(prefixes, datatype_properties)

    #Prefix in data values defined in an instance
    prefixes = find_prefixes_data_values(prefixes, property_values)

    prefixes = find_prefixes_metadata(prefixes, metadata)

    return prefixes

# Find the prefixes that are used in datatype properties, as the range (datatype) of a datatype propertie
# or as the object of an owl:hasValue instance whose subject is a datatype property
def find_prefixes_datatype_properties(prefixes, attribute_blocks):
    for id, attribute_block in attribute_blocks.items():
        for attribute in attribute_block["attributes"]:
            prefix = attribute["prefix"]
            if prefix not in prefixes:
                prefixes.append(prefix)

            #Prefix of the datatypes
            if attribute["datatype"] and not attribute["hasValue"]:
                prefix = attribute['prefix_datatype']
                if prefix not in prefixes:
                    prefixes.append(prefix)

            #Prefix of the data values defined inside a owl:hasValue statement
            if attribute["datatype"] and attribute["hasValue"]:
                if attribute["prefix_datatype"] == "xsd":
                    prefix = attribute['prefix_datatype']
                else:
                    prefix = attribute['prefix_datatype'].split('^^')[1]
                if prefix not in prefixes:
                    prefixes.append(prefix)

    return prefixes

# Find the prefixes that are used in the ontology metadata
def find_prefixes_metadata(prefixes, metadata):
    for prefix_uri in metadata.items():
        # Skip the annotation properties defined through an URI
        if prefix_uri[0][0]!='<':
            prefix = prefix_uri[0].split(':')[0]
            if prefix not in prefixes:
                prefixes.append(prefix)
    
    return prefixes

# Fin the prefixes that are used in data values
def find_prefixes_data_values(prefixes, values):
    for id, value in values.items():
        if value["type"] is not None and ":" in value["type"]:
            prefix = value["type"].split(':')[0]
            if prefix not in prefixes:
                    prefixes.append(prefix)
    
    return prefixes


# Find the prefixes that are used in concepts, individuals and object properties
def find_prefixes_elements(prefixes, elements):
    for id, element in elements.items():
        if "prefix" in element:
            prefix = element["prefix"]
            if prefix not in prefixes:
                prefixes.append(prefix)

    return prefixes