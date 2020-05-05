def get_ttl_template(filename, namespaces):

    file = open(filename, 'w')
    onto_prefix = list(namespaces.keys())[0]
    onto_uri = namespaces[onto_prefix]
    for prefix, uri in namespaces.items():
        file.write("@prefix " + prefix + ": <" + uri + "#> .\n")

    file.write("@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
               "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
               "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
               "@prefix xml: <http://www.w3.org/XML/1998/namespace> .\n"
               "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
               "@prefix dc: <http://purl.org/dc/elements/1.1> .\n"
               "@prefix dcterms: <http://purl.org/dc/terms/> .\n")
    file.write("@base <" + onto_uri + "#> .\n\n")

    return file, onto_prefix, onto_uri

def write_ontology_metadata(file, metadata, onto_uri):

    file.write("<" + onto_uri + "#> rdf:type owl:Ontology")
    for key, value in metadata.items():
        key = key.lower()
        value = "\"" + value + "\""
        if key == "version":
            metadata_uri = "owl:versionInfo"
        elif key == "author":
            metadata_uri = "dc:creator"
        elif key == "title":
            metadata_uri = "dc:title"
        else:
            continue
        file.write(" ;\n")
        file.write("\t\t\t" + metadata_uri + " " + value)
    file.write(" .\n\n")

    return file