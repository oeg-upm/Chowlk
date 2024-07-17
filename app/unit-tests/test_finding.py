import time
import sys
import os
import rdflib
import tempfile
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_ontologies():

    tests_path = os.path.dirname(os.path.abspath(__file__))
    inputs_path = os.path.join(tests_path, "inputs")
    outputs_path = os.path.join(tests_path, "outputs")
    converter_path = os.path.join(tests_path, "..\..\converter.py")

    for filename in os.listdir(inputs_path):
        input_filepath = os.path.join(inputs_path, filename)
        output_filepath = os.path.join(outputs_path, filename[:-3] + "ttl")
        log_filepath = os.path.join(outputs_path, filename[:-4] + "_log.txt")
        print("\nGenerating ontology (output) " + filename + "\n")
        command = r'python ' + converter_path + ' ' + input_filepath + \
            ' ' + output_filepath + r' --type ontology --format ttl > ' + \
            log_filepath
        os.system(command)


def test():
    all_test_passed = True
    tests_path = os.path.dirname(os.path.abspath(__file__))
    desired_outputs_path = os.path.join(tests_path, "desired_outputs")
    outputs_path = os.path.join(tests_path, "outputs")
    outputs_tests = os.listdir(outputs_path)

    for filename in os.listdir(desired_outputs_path):
        if filename in outputs_tests:
            # A test is performed per ontology and log generated (both in the same test)
            if filename[-4:] == ".ttl":
                #print("Performing test " + filename + ". Result: ")
                output_filepath = os.path.join(outputs_path, filename)
                desired_output_filepath = os.path.join(desired_outputs_path, filename)
                if compare_ontologies2(filename, output_filepath, desired_output_filepath):
                    output_log_filepath = os.path.join(outputs_path, filename[:-4] + "_log.txt")
                    desired_output_log_filepath = os.path.join(desired_outputs_path, filename[:-4] + "_log.txt")
                    if not compare_logs(output_log_filepath, desired_output_log_filepath):
                        
                        all_test_passed = False
                        print("Test " + filename + " failed. Logs are not equal\n")
                    else:
                        print("Test " + filename + " passed\n")
                else:
                    all_test_passed = False
        else:
            print("Test " + filename + " failed. The output has not been generated correctly.\n")
            all_test_passed = False
    return all_test_passed

def compare_ontologies2(filename, o1, o2):
    file1 = open(o1, 'r')
    file_read1 = file1.read()
    file1.close()
    file2 = open(o2, 'r')
    file_read2 = file2.read()
    file2.close()
    try:
        g1 = rdflib.Graph()
        g1.parse(data=file_read1, format="turtle")
        g2 = rdflib.Graph()
        g2.parse(data=file_read2, format="turtle")
        turtle_output_file1 = tempfile.NamedTemporaryFile()
        turtle_output_file2 = tempfile.NamedTemporaryFile()
        g1.serialize(destination=turtle_output_file1, format="turtle")
        g2.serialize(destination=turtle_output_file2, format="turtle")

        turtle_output_file1.seek(0)
        turtle_output_file2.seek(0)

        turtle_string1 = turtle_output_file1.read().decode("utf-8")
        turtle_string1 = turtle_string1.replace('#/', '#')
        turtle_string1 = turtle_string1.replace('##', '#')
        turtle_string2 = turtle_output_file2.read().decode("utf-8")

        try:
            g3 = rdflib.Graph()
            g3.parse(data=turtle_string1, format="turtle")
            turtle_output_file3 = tempfile.NamedTemporaryFile()
            g3.serialize(destination=turtle_output_file3, format="turtle")
            turtle_output_file3.seek(0)

            turtle_string3 = turtle_output_file3.read().decode("utf-8")
        
        except:
            turtle_string3 = turtle_string1
    
    except:
        turtle_string3 = file_read1
        turtle_string2 = file_read2
    
    is_equal = turtle_string3 == turtle_string2

    if not is_equal:
        print('Test ' + filename + ' failed. Files are not equal\n')

    return is_equal

def compare_ontologies3(o1, o2):
    file1 = open(o1, 'r')
    file_read1 = file1.read()
    file1.close()
    file2 = open(o2, 'r')
    file_read2 = file2.read()
    file2.close()
    g1 = rdflib.Graph()
    g1.parse(data=file_read1, format="turtle")
    turtle_output_file1 = tempfile.NamedTemporaryFile()
    g1.serialize(destination=turtle_output_file1, format="turtle")

    turtle_output_file1.seek(0)

    turtle_string1 = turtle_output_file1.read().decode("utf-8")

    if turtle_string1 != file_read2:
        print('Test failed. Files are not equal\n')

    return turtle_string1 == file_read2

def compare_ontologies(o1, o2):
    # We want to compare two fields in order to find
    # the first line where they are not equals
    file1 = open(o1, 'r')
    linesFile1 = file1.readlines()
    file2 = open(o2, 'r')
    linesFile2 = file2.readlines()
    equals = True
    # The files can have different length
    # For that reason it is neccesary to find the minimun length
    minimun_length = len(linesFile1)
    if minimun_length > len(linesFile2):
        minimun_length = len(linesFile2)

    for i in range(minimun_length):
        if linesFile1[i] != linesFile2[i]:
            print("Test failed. Files are not equal in line " + str(i+1) + "\n")
            equals = False
            break

    # If they have different lengths and until minimum_length
    # are equal, it is neccesary to indicate that one is greater
    # than the other
    if equals and len(linesFile1) != len(linesFile2):
        print("Test failed. One file is greater than the other. The minimun lenght is " +
              str(i+1) + ". Until that line they are equals\n")
        equals = False 

    file1.close()
    file2.close()
    return equals

def compare_logs(l1, l2):
    file1 = open(l1, 'r')
    file2 = open(l2, 'r')
    passed = file1.read() == file2.read()
    file1.close()
    file2.close()
    return passed

#Funtion to remove all the files in the repository output
def empty_repository():
    tests_path = os.path.dirname(os.path.abspath(__file__))
    outputs_path = os.path.join(tests_path, "outputs")
    os.makedirs(outputs_path, exist_ok=True)
    for f in os.listdir(outputs_path):
        os.remove(os.path.join(outputs_path, f))
    return

if __name__ == "__main__":
    inicio = time.time()
    empty_repository()
    generate_ontologies()
    if test():
        print("\n All tests passed")
    fin = time.time()
    print('\n Time: ')
    print(fin-inicio)