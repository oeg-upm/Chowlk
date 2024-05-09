from app.source.chowlk.resources.utils import base_directive_prefix

# Function to construct an anonymous individual. 
# It is neccesary to write all the triples where this anonymous individual is the subject.
def anonymous_individual(anonymous_individual, anonymous_individuals, arrows, individuals, values):
    text = '[ '

    # Iterate all the arrows whose source is the anonymous individual
    for relation_id in anonymous_individual['relations']:
        
        # Get the arrow
        arrow = arrows[relation_id]
        # Get the arrow type
        arrow_type = arrow['type']

        # Does the arrow represent an object property?
        if arrow_type == 'owl:ObjectProperty':

            # Does the target of the arrow represent a named individual?
            if 'target' in arrow and arrow['target'] in individuals:
                individual = individuals[arrow['target']]
                predicate = f'{base_directive_prefix(arrow["prefix"])}{arrow["uri"]}'
                object = f'{base_directive_prefix(individual["prefix"])}{individual["uri"]}'
                text += f'{predicate} {object} ;\n'
        
        # Does the arrow represent a datatype property?
        elif arrow_type == 'owl:DatatypeProperty':
            
            # Does the target represent a data value?
            if 'target' in arrow and arrow['target'] in values:
                predicate = f'{base_directive_prefix(arrow["prefix"])}{arrow["uri"]}'
                object = parse_data_value(values[arrow['target']])
                text += f'{predicate} {object} ;\n'
            

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