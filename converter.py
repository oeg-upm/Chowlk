import argparse

from app.source.chowlk.services.transformations import transform_ontology
from app.source.chowlk.resources.utils import read_drawio_xml
from app.source.chowlk.resources.generate_xml_errors import generate_xml_error
import time


def main(diagram_path, output_path, xml_error_path, format):
    #inicio = time.time()

    root = read_drawio_xml(diagram_path)
    ontology_turtle, ontology_xml, namespaces, errors, warnings = transform_ontology(root)

    file = open(output_path, mode="w")

    if format == "ttl":
        file.write(ontology_turtle)
    elif format == "xml":
        file.write(ontology_xml)

    file.close()

    if (xml_error_path != 'None'):
        xml_error_file, xml_error_generated = generate_xml_error(diagram_path, errors, None)

        try:
            xml_error_file, xml_error_generated = generate_xml_error(diagram_path, errors, None)

            if xml_error_generated:

                try:
                    file = open(xml_error_path, mode="w", encoding = "utf-8")
                except:
                    print('Invalid "xml_error_path"')

                file.write(xml_error_file)
                file.close()
                print('The xml file with the errors has been generated')

            else:
                print('There is no errors. The xml file with the errors has not been generated')

        except:
            print('Something wrong happened trying to generate the xml file with the errors')

    #fin = time.time()
    #print(fin-inicio)

    print_errors(errors)
    print_warnings(warnings)
    

def print_errors(errors):
    
    for error_type in errors:
        error = errors[error_type]
        if isinstance(error, list):
            for content in error:
                if "message" in content:
                    print("\nError " + error_type + ": " + content.pop("message"))
                else:
                    print("\nError " + error_type + ": ")
                for type in content:
                    print("\t" + type +": " + content[type])
        else:
            print("\nError " + error_type + ": " + error.pop("message"))
            for type in error:
                    print("\t" + type +": " + error[type])

def print_warnings(warnings):
    for warning_type in warnings:
        warning = warnings[warning_type]
        if isinstance(warning, list):
            for content in warning:
                if "message" in content:
                    print("\nWarning " + warning_type + ": " + content.pop("message"))
                else:
                    print("\nWarning " + warning_type + ": ")
                for type in content:
                    print("\t" + type +": " + content[type])
        else:
            print("\nWarning " + warning_type + ": " + warning.pop("message"))
            for type in warning:
                    print("\t" + type +": " + warning[type])

    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert an xml conceptualization into an ontology.")
    parser.add_argument("diagram_path", type=str, help="the path where the diagram is located")
    parser.add_argument("output_path", type=str, help="the desired location for the generated ontology")
    parser.add_argument("--xml_error_path", type=str, default="None", help="the desired location for the xml file with the marked errors found in the diagram")
    parser.add_argument("--type", type=str, default="ontology", help="ontology or rdf data")
    parser.add_argument("--format", type=str, default="ttl", help="file format: ttl or xml")
    args = parser.parse_args()

    main(args.diagram_path, args.output_path, args.xml_error_path, args.format)
