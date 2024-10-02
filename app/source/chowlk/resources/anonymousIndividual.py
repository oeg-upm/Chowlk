from app.source.chowlk.resources.utils import base_directive_prefix, check_values_type

# Function to construct an anonymous individual. 
# It is neccesary to write all the triples where this anonymous individual is the subject.
# This is a recursive function that cannot terminate if the user has created a loop in the diagram. Therefore, it is neccesary
# to check if each anonymous individual (blank box) has been reached before.
def get_anonymous_individual(anonymous_individual, anonymous_individuals, arrows, individuals, values, diagram_model, reached):
    text = '[ '

    # Iterate all the arrows whose source is the anonymous individual
    for relation_id in anonymous_individual['relations']:
        
        # Get the arrow
        arrow = arrows[relation_id]
        # Get the arrow type
        arrow_type = arrow['type']
        # Get the target of the arrow
        target = arrow['target'] if 'target' in arrow else None

        if target in reached:
            raise Exception("Infinite loop")


        # Does the arrow represent an object property?
        if arrow_type == 'owl:ObjectProperty': 
            target = arrow['target'] if 'target' in arrow else None

            # Does the target of the arrow represent a named individual?
            if target in individuals:
                individual = individuals[arrow['target']]
                predicate = f'{base_directive_prefix(arrow["prefix"])}{arrow["uri"]}'
                object = f'{base_directive_prefix(individual["prefix"])}{individual["uri"]}'
                text += f'{predicate} {object} ;\n'
            
            # Does the target of the arrow represent an anonymous individual?
            elif target in anonymous_individuals:
                reached.append(target)
                predicate = f'{base_directive_prefix(arrow["prefix"])}{arrow["uri"]}'
                object = get_anonymous_individual(anonymous_individuals[target], anonymous_individuals, arrows, individuals, values, diagram_model, reached)
                text += f'{predicate} {object} ;\n'
        
        elif arrow_type == 'owl:sameAs' or arrow_type == 'owl:differentFrom':
            target = arrow['target'] if 'target' in arrow else None

            # Does the target of the arrow represent a named individual?
            if target in individuals:
                individual = individuals[arrow['target']]
                object = f'{base_directive_prefix(individual["prefix"])}{individual["uri"]}'
                text += f'{arrow_type} {object} ;\n'
            
            # Does the target of the arrow represent an anonymous individual?
            elif target in anonymous_individuals:
                reached.append(target)
                object = get_anonymous_individual(anonymous_individuals[target], anonymous_individuals, arrows, individuals, values, diagram_model, reached)
                text += f'{arrow_type} {object} ;\n'
        
        # Does the arrow represent a datatype property?
        elif arrow_type == 'owl:DatatypeProperty':
            
            # Does the target represent a data value?
            if 'target' in arrow and arrow['target'] in values:
                predicate = f'{base_directive_prefix(arrow["prefix"])}{arrow["uri"]}'
                object = parse_data_value(values[arrow['target']])
                text += f'{predicate} {object} ;\n'
        
        # Does the arrow represent an annotation property?
        elif arrow_type == 'owl:AnnotationProperty':
            text += write_annotation_triple(relation_id, arrow, individuals, diagram_model.get_uri_references(), values, diagram_model)
        
        else:
            diagram_model.generate_error("An arrow whose source source is an anonymous individual is not an object property or datatype property", relation_id, arrow_type, "Individual")
            

    text += '] '

    return text

def parse_data_value(data_value):

    # Has the user specify a datatype?
    if data_value["type"] is not None:

        # Has the user specify a custom dataype?
        if ":" in data_value["type"]:
            object = "\"" + data_value["value"] + "\"" + "^^" + data_value["type"]
        
        else:
            # For default the datatype is xsd
            object = "\"" + data_value["value"] + "\"" + "^^xsd:" + data_value["type"]

    # Has the user specify a language? (i.e. the data value is a literal)
    elif data_value["lang"] is not None:
        object = "\"" + data_value["value"] + "\"" + "@" + data_value["lang"]
    
    else:
        # The data value is a literal
        object = "\"" + data_value["value"] + "\""
    
    return object

# Write triples whose predicate is an annotation property
def write_annotation_triple(relation_id, relation, individuals, uri_references, values, diagram_model):
    target = relation['target']
    object_error = False
    anonymous_individuals = diagram_model.get_anonymous_individuals()

    # Is the object an individual?
    if target in individuals:
        individual = individuals[target]
        target_prefix = base_directive_prefix(individual['prefix'])     
        target_suffix = individual['uri']
    
    # Is the object an URI reference?
    elif target in uri_references:
        target_prefix = ''
        target_suffix = uri_references[target]
    
    # Is the object a data value?
    elif target in values:
        target_suffix, type = check_values_type(values[target])

        """# Is not the object a literal?
        if type != 'xsd:string':
            # The object of an annotation property triple is not an individual, a literal or an URI reference
            object_error = True"""

        target_prefix = ''
    
    # Is the object an anonymous individual?
    elif target in anonymous_individuals:
        target_prefix = ''
        try:
            target_suffix = get_anonymous_individual(anonymous_individuals[target], anonymous_individuals, diagram_model.get_arrows(), individuals, values, diagram_model, [target])
        except:
            diagram_model.generate_error("There is an infinite loop in the diagram between anonymous individuals, involving an owl:AnnotationProperty", target, None, "Individual")
            target_suffix = '""'
    
    else:
        # The object of an annotation property triple is not an individual, a literal or an URI reference
        object_error = True

    annotation_prefix = base_directive_prefix(relation['prefix'])

    if object_error:
        diagram_model.generate_error("The target of an annotation property is not an individual, a literal or an URI reference", relation_id, f'{annotation_prefix}{relation["uri"]}', "Annotation Properties") 
        return ''

    return f'\t{annotation_prefix}{relation["uri"]} {target_prefix}{target_suffix}'