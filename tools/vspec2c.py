#!/usr/bin/python3

#
# (C) 2016 Jaguar Land Rover
#
# All files and artifacts in this repository are licensed under the
# provisions of the license provided by the LICENSE file in this repository.
#
#
# Concert vspec file to C header and source file.
#

import sys
import os
import vspec
import getopt
import pprint
import fileinput
#
# C Header file template code.
#
vss_hdr_template = """
//
// Auto generated code by vspec2c.py
// See github.com/GENIVI/vehicle_signal_specification for details/
//

#include <stdint.h>
#include <float.h>

typedef enum _vss_signal_type_e {
    VSS_INT8 = 0,
    VSS_UINT8 = 1,
    VSS_INT16 = 2,
    VSS_UINT16 = 3,
    VSS_INT32 = 4,
    VSS_UINT32 = 5,
    VSS_DOUBLE = 6,
    VSS_FLOAT = 7,
    VSS_BOOLEAN = 8,
    VSS_STRING = 9,
    VSS_STREAM = 10,
    VSS_NA = 11,
} vss_signal_type_e;

typedef enum _vss_element_type_e {
    VSS_ATTRIBUTE = 0,
    VSS_BRANCH = 1,
    VSS_SENSOR = 2,
    VSS_ACTUATOR = 3,
    VSS_RBRANCH = 4,
    VSS_ELEMENT = 5,
} vss_element_type_e;

typedef struct _vss_signal_t {
    int index;
    int parent_index;
    const char *name;
    const char *uuid;
    vss_element_type_e element_type;
    vss_signal_type_e data_type;
    const char *unit_type;

    union  {
        int64_t i;
        double d;
    } min_val;

    union {
        int64_t i;
        double d;
    } max_val;

    const char *description;
    const char **enum_values;
    const char *sensor;
    const char *actuator;
} vss_signal_t;


// Return a signal struct pointer based on signal index.
extern vss_signal_t* vss_signal_by_index(int index);

// Return a signal struct pointer based on full signal path
extern vss_signal_t* vss_signal_by_name(char* path);

// Return the parent of a signal. Return 0 if signal is root.
extern vss_signal_t* vss_get_parent(vss_signal_t* signal);

// Populate the full path name to the given signal.
// The name will be stored in 'result'.
// No more than 'result_max_len' bytes will be copied.
// The copied name will always be null terminated.
// 'result' is returned.
// In case of error, an empty string is copiec into result.
char* vss_get_signal_path(vss_signal_t* sig, char* result, int result_max_len);

extern vss_signal_t vss_signal[];

:MACRO_DEFINITION_BLOCK:
"""

#
# C Source file template code.
#
vss_src_template = """
//
// Auto generated code by vspec2c.py
// See github.com/GENIVI/vehicle_signal_specification for details/
//

#include ":HEADER_FILE_NAME:"

vss_signal_t* vss_signal_by_index(int index)
{
}

vss_signal_t* vss_signal_by_name(char* path)
{
}

vss_signal_t* vss_get_parent(vss_signal_t* signal)
{
}

vss_signal_t vss_signal[] = {
:VSS_SIGNAL_ARRAY:
};
"""

def usage():
    print("Usage:", sys.argv[0], "[-I include-dir] ... [-i prefix:id-file] vspec-file c-header-file c-source-file")
    print("  -I include-dir       Add include directory to search for included vspec")
    print("                       files. Can be used multiple timees.")
    print()
    print("  -i prefix:uuid-file  File to use for storing generated UUIDs for signals with")
    print("                       a given path prefix. Can be used multiple times to store")
    print("                       UUIDs for signal sub-trees in different files.")
    print()
    print(" vspec-file            The vehicle specification file to parse.")
    print(" c-header-file         The file to output the C header file to.")
    print(" c-source-file         The file to output the C source file to.")
    sys.exit(255)


type_map =  {
    "int8": "VSS_INT8",
    "uint8": "VSS_UINT8",
    "int16": "VSS_INT16",
    "uint16": "VSS_UINT16",
    "int32": "VSS_INT32",
    "uint32": "VSS_UINT32",
    "int64": "VSS_INT64",
    "uint64": "VSS_UINT64",
    "float": "VSS_FLOAT",
    "double": "VSS_DOUBLE",
    "bool": "VSS_BOOLEAN",
    "boolean": "VSS_BOOLEAN",
    "string": "VSS_STRING",
    "stream": "VSS_STREAM",
    "na": "VSS_NA"
}

element_map = {
    "attribute": "VSS_ATTRIBUTE",
    "branch": "VSS_BRANCH",
    "sensor": "VSS_SENSOR",
    "actuator": "VSS_ACTUATOR",
    "rbranch": "VSS_RBRANCH",
    "element": "VSS_ELEMENT"
}

def emit_signal(signal_name, vspec_data):
    try:
        index = vspec_data['_index_'];
        parent_index = vspec_data['_parent_index_'];
        uuid = vspec_data['uuid'];
        elem_type = element_map[vspec_data['type'].lower()];
    except KeyError as e:
        print("Missing in vspec element key: {}".format(e))
        print("Path: {}".format(vspec_data['_signal_path_']))
        exit(255)

    data_type = 'VSS_NA'
    unit = ''
    min = 'INT64_MIN' # not defined.
    max = 'INT64_MIN' # not defined.
    desc = ''
    enum = '{ 0 }'
    sensor = ''
    actuator = ''


    if 'datatype' in vspec_data:
        try:
            data_type = type_map[vspec_data['datatype'].lower()];
        except KeyError as e:
            print("Illegal data type: {}".format(e))
            print("Signal: {}".format(vspec_data['_signal_path_']))
            print("Try: int8 uint8 int16 uint16 int32 uint32 int64 uint64")
            print("     float double string boolean stream")
            exit(255)

    if 'unit' in vspec_data:
        unit = vspec_data['unit']

    if 'min' in vspec_data:
        if not elem_type in [ "int8", "uint8", "int16", "uint16", "int32" , "uint32", "double", "float"]:
            min = vspec_data['min']
        else:
            print("Signal {}: Ignoring specified min value for type {}".format(vspec_data['_signal_path_'], data_type))


    if 'max' in vspec_data:
        if not elem_type in [ "int8", "uint8", "int16", "uint16", "int32" , "uint32", "double", "float"]:
            max = vspec_data['max']
        else:
            print("Signal {}: Ignoring specified max value for type {}".format(vspec_data['_signal_path_'], data_type))


    if 'description' in vspec_data:
        desc = vspec_data['description']

    if 'enum' in vspec_data:
        enum = '{'
        for enum_elem in vspec_data['enum']:
            enum += '"{}", '.format(enum_elem)
        enum += '}'

    if 'sensor' in vspec_data:
        sensor = vspec_data['sensor']

    actuator = ''
    if 'actuator' in vspec_data:
        actuator = vspec_data['actuator']

    return f'    {{ {index}, {parent_index}, "{signal_name}", "{uuid}", {elem_type}, {data_type}, "{unit}", {min}, {max}, "{desc}", (const char*[]) {enum}, "{sensor}", "{actuator}" }},\n'




def add_signal_index(vspec_data,  index = 0, parent_index = -1):
    for k,v in vspec_data.items():
        v['_index_'] = index;
        index += 1
        v['_parent_index_'] = parent_index;

        if (v['type'] == 'branch'):
            index = add_signal_index(v['children'], index, v['_index_'])

    return index

def add_signal_path(vspec_data, parent_signal = ""):
    for k, v in vspec_data.items():
        if (len(parent_signal) > 0):
            signal_path = parent_signal + "_" + k
        else:
            signal_path = k

        v['_signal_path_'] = signal_path

        if (v['type'] == 'branch'):
            add_signal_path(v['children'], signal_path)

def generate_source(vspec_data):
    sig_decl = ''
    for k,v in vspec_data.items():

        sig_decl += emit_signal(k, v)

        if (v['type'] == 'branch'):
            sig_decl += generate_source(v['children'])

    return sig_decl


def generate_header(vspec_data):
    macro = ''
    for k,v in vspec_data.items():
        macro += '#define VSS_{}() vss_get_signal_by_index({})\n'.format(v['_signal_path_'],v['_index_'])
        if (v['type'] == 'branch'):
            macro += generate_header(v['children'])

    return macro


if __name__ == "__main__":
    #
    # Check that we have the correct arguments
    #
    opts, args= getopt.getopt(sys.argv[1:], "I:i:")

    # Always search current directory for include_file
    include_dirs = ["."]
    for o, a in opts:
        if o == "-I":
            include_dirs.append(a)
        elif o == "-i":
            id_spec = a.split(":")
            if len(id_spec) != 2:
                print("ERROR: -i needs a 'prefix:id_file' argument.")
                usage()

            [prefix, file_name] = id_spec
            vspec.db_mgr.create_signal_uuid_db(prefix, file_name)
        else:
            usage()

    if len(args) != 3:
        usage()

    try:
        tree = vspec.load(args[0], include_dirs)
    except vspec.VSpecError as e:
        print("Error: {}".format(e))
        exit(255)



    add_signal_index(tree)
    add_signal_path(tree)

    # Generate header file
    macro = generate_header(tree)
    with open (args[1], "w") as hdr_out:
        hdr_out.write(vss_hdr_template.replace(':MACRO_DEFINITION_BLOCK:', macro))

    # Generate source file
    sig_decl = generate_source(tree)
    with open (args[2], "w") as src_out:
        src_out.write(vss_src_template.
                      replace(':VSS_SIGNAL_ARRAY:', sig_decl).
                      replace(':HEADER_FILE_NAME:', os.path.basename(args[1])))