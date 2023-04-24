#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright 2023 PDF Association, Inc. https://www.pdfa.org
#
# This material is based upon work supported by the Defense Advanced
# Research Projects Agency (DARPA) under Contract No. HR001119C0079.
# Any opinions, findings and conclusions or recommendations expressed
# in this material are those of the author(s) and do not necessarily
# reflect the views of the Defense Advanced Research Projects Agency
# (DARPA). Approved for public release.
#
# SPDX-License-Identifier: Apache-2.0
# Author: Peter Wyatt, PDF Association
#
# A HIGHLY inefficient way of working out the layout of a PDF using Linux grep and QPDF.
# There is NO PDF PARSER USED HERE!!
# Avoid using on large PDFs or PDFs with many objects! Script will exit if it sees
# object number `MAX_MARKERS` or greater. Only works with valid PDFs that work with QPDF and
# that are not encrypted with a User Password.
#
# Creates a CSV output suitable for cutting & pasting to create a Sankey diagram at 
# https://observablehq.com/@pdf/visualizing-pdfs-with-sankey-diagrams
#
# Due to very flexible PDF EOL rules, do NOT use ^ (start-of-line) in regexes! 
# PDF Whitespace (Table 1) regex: [\\000\\011\\012\\014\\015\\040] - this is NOT the same as [[:blank:]]!!
#

import subprocess
import os
import argparse
import pprint
import string
import re
import copy
from sys import platform

pp = pprint.PrettyPrinter(indent=2, compact=False, width=180)

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--csv',   help='Output CSV filename (always overwritten)', dest="csvfile", )
parser.add_argument('-d', '--debug', help="Verbose debugging output of internal Python data", action='store_true', default=False, dest="debugmode")
parser.add_argument('-k', '--keep',  help="Keep all data markers in debug output", action='store_true', default=False, dest="dont_delete")
parser.add_argument('-f', '--force', help="Force processing by ignoring possible data issues", action='store_true', default=False, dest="force")
parser.add_argument('-p', '--pdf',   help='Input PDF filename', dest="pdffile")
args = parser.parse_args()

# Constants
MAX_MARKERS = 500       # Maximum number of markers before we assume things are too complex/big for D3 Sankey and exit.  See -f/--force
LINEARIZE_RANGE = 10    # How many markers after a Linearization marker should there be "startxref" / "%%EOF"
BUFFER_SIZE = 24        # Byte buffer used to guessimate what type each indirect object is (number of bytes after "X Y obj")
TIMEOUT_SECS = 10       # QPDF subprocess run timeout (seconds)

if (args.pdffile is None):
    parser.print_help()
    exit(-1)

if ('linux' not in platform):
    print('ERROR: only works under Linux! Needs grep and qpdf.\n')
    parser.print_help()
    exit(-1)

pdf = args.pdffile              # input PDF filename
print(pdf +": ", end='')
size = os.path.getsize(pdf)     # phsyical file size (bytes)
in_pdf = open(pdf, "rb")

data = []                       # Data dictionary for Sankey D3 diagram 
cavity_count = 1                # Need to uniquely label each cavity for Sankey nodes 

def work_out_object_type(c1, c2):
    # Work out the object type based on first 2 characters: c1, c2
    t = '??'
    if (c1 == '['):
        t = 'array'
    elif (c1 == '/'):
        t = 'name'
    elif (c1 == '('): 
        t = 'literal-string'
    elif ((c1 == '<') and (c2 == '<')):
        t = 'dict'
    elif ((c1 == 'n') and (c2 == 'u')): # null
        t = 'null'
    elif (((c1 == 't') and (c2 == 'r')) or ((c1 == 'f') and (c2 == 'a'))): # true / false
        t = 'bool'
    elif (c1 == '<') and ((c2 in string.hexdigits) or (c2 == '>')):
        t = 'hex-string'
    elif (((c1 in string.digits) and ((c2 in string.digits) or (c2 == chr(0)) or (c2 == '.'))) or ((c1 == '.') and (c2 in string.digits))):
        t = 'number'
    return t


# Find PDF header magic (might not be at physical file offset 0!)
cmd = ['grep', '-P', '--text', '--color=none', '--byte-offset', '--only-matching', '%PDF-[0-9]+\.[0-9]+', pdf ]
result = subprocess.run(cmd, capture_output=True, text=True)
if (result.returncode != 0) or (len(result.stdout.strip()) == 0):
    print('"%PDF-x.y" header could not be found! Not a PDF file...')
    exit(-1)
result = result.stdout.splitlines()
if (len(result) > 1):
    print('\n\nWARNING: More than one "%PDF-x.y" header was found! Huh???')
result = result[0].split(':')
sof = int(result[0])
if (sof > 0):
    data.append({ 'category':'PDF file', 'name':'Cavity ' + str(cavity_count), 'offset':0, 'size':sof, 'color':'red' })
    cavity_count = cavity_count + 1 
data.append({ 'category':'PDF file', 'name':result[1], 'offset':sof, 'size':len(result[1])+1, 'color':'lightblue' })

# PDF conventional body indirect object marker "X Y obj"
cmd = ['grep', '-P', '--text', '--color=none', '--byte-offset', '--only-matching', '[0-9]+[\\000[:blank:]]+[0-9]+[\\000[:blank:]]+obj', pdf ]
result = subprocess.run(cmd, capture_output=True, text=True).stdout
result = result.splitlines()
num_obj_keywords = len(result)
if (num_obj_keywords < 5):
    # Likely non-SPACEs are between "X", "Y" and "obj" so grep fails. e.g. ProgressOnFileObservatory_PDFDays2022_JPL_20220909.pdf
    # @todo - read the PDF file into a bytearray and manually do this search... yuck!
    print('ERROR: could not find sufficient "X Y obj" markers (%d found)!' % num_obj_keywords)
    exit(-1)
for s in result:
    d = s.split(':')
    data.append({ 'category':'PDF file', 'name':d[1], 'offset':int(d[0])})

# Primitive PDF object type classification markers.
# Want the first 2 non-whitespace bytes following "obj" to determine type of object.
# Linux grep cannot span mulitple lines correctly with PDF's mix of EOLs and whitespace (even pcregrep can't do this).
# Best approach is to re-use the byte-offsets from "X Y obj" above, skip over N x whitespace (EOLs, NUL, SPACE, etc) 
# to locate the first 2 non-whitespace bytes in a small buffer.
for s in result:
    d = s.split(':')
    in_pdf.seek(int(d[0]) + len(d[1]) + 1)   # start reading immediately after "X Y obj"
    b = bytearray(in_pdf.read(BUFFER_SIZE))
    i = 0
    while ((i < (BUFFER_SIZE - 2)) and (b[i] in [0, 9, 10, 12, 13, 32])): # PDF whitespace bytes (Table 1)
        i = i + 1
    c1 = chr(b[i + 0])
    c2 = chr(b[i + 1])
    t = work_out_object_type(c1, c2)
    data.append({ 'category':'Marker', 'name':t, 'type': t, 'offset':int(d[0]) })

# Object stream marker
cmd = ['grep', '-P', '--text', '--color=none', '--byte-offset', '--only-matching', '/ObjStm', pdf ]
result = subprocess.run(cmd, capture_output=True, text=True).stdout
result = result.splitlines()
for s in result:
    d = s.split(':')
    data.append({ 'category':'Marker', 'name':'ObjStm', 'type':'Object stream', 'offset':int(d[0]) })

# Cross-reference stream marker
cmd = ['grep', '-P', '--text', '--color=none', '--byte-offset', '--only-matching', '/XRef', pdf ]
result = subprocess.run(cmd, capture_output=True, text=True).stdout
result = result.splitlines()
for s in result:
    d = s.split(':')
    data.append({ 'category':'Marker', 'name':'XRef', 'type':'XRef stream', 'offset':int(d[0]) })

# "stream" keyword - need to explicitly differentiate from "endstream"
cmd = ['grep', '-P', '--text', '--color=none', '--byte-offset', '--only-matching', '(^stream)|([^d]\Kstream)', pdf ]
result = subprocess.run(cmd, capture_output=True, text=True).stdout
result = result.splitlines()
num_stream = len(result)
for s in result:
    d = s.split(':')
    data.append({ 'category':'Marker', 'name':'stream', 'type':'stream', 'offset':int(d[0])})

# "endstream" keyword
cmd = ['grep', '-P', '--text', '--color=none', '--byte-offset', '--only-matching', 'endstream', pdf ]
result = subprocess.run(cmd, capture_output=True, text=True).stdout
result = result.splitlines()
if (num_stream != len(result)):
    print('ERROR: "endstream" marker (%d) mismatch with "stream" (%d)!' % (len(result), num_stream))
    exit(-1)
if ((num_stream > num_obj_keywords) or (len(result) > num_obj_keywords)):
    print('ERROR: "endstream" (%d) / "stream" (%d) markers did not correlate with number of objects (%d)!' % (len(result), num_stream, num_obj_keywords))
    exit(-1)
for s in result:
    d = s.split(':')
    data.append({ 'category':'Marker', 'name':'endstream', 'type':'stream', 'offset':int(d[0]) })

# "endobj" keyword
cmd = ['grep', '-P', '--text', '--color=none', '--byte-offset', '--only-matching', 'endobj', pdf ]
result = subprocess.run(cmd, capture_output=True, text=True).stdout
result = result.splitlines()
if (len(result) != num_obj_keywords):
    print('ERROR: "endobj" marker mismatch (%d found, %d expected)!' % (len(result), num_obj_keywords))
    exit(-1)
for s in result:
    d = s.split(':')
    data.append({ 'category':'Marker', 'name':'endobj', 'offset':int(d[0])})

# "xref" keyword
cmd = ['grep', '-P', '--text', '--color=none', '--byte-offset', '--only-matching', '[^t]\Kxref', pdf ]
result = subprocess.run(cmd, capture_output=True, text=True).stdout
result = result.splitlines()
for s in result:
    d = s.split(':')
    data.append({ 'category':'PDF file', 'name':'xref', 'offset':int(d[0]), 'color':'lightblue' })

# "trailer" keyword
cmd = ['grep', '-P', '--text', '--color=none', '--byte-offset', '--only-matching', 'trailer', pdf ]
result = subprocess.run(cmd, capture_output=True, text=True).stdout
result = result.splitlines()
for s in result:
    d = s.split(':')
    data.append({ 'category':'PDF file', 'name':'trailer', 'offset':int(d[0]), 'color':'lightblue' })

# "startxref" keyword
cmd = ['grep', '-P', '--text', '--color=none', '--byte-offset', '--only-matching', 'startxref', pdf ]
result = subprocess.run(cmd, capture_output=True, text=True).stdout
result = result.splitlines()
num_startxrefs = len(result)
for s in result:
    d = s.split(':')
    data.append({ 'category':'PDF file', 'name':'startxref', 'offset':int(d[0]), 'color':'lightblue' })

# Linearization dictionary 
cmd = ['grep', '-P', '--text', '--color=none', '--byte-offset', '--only-matching', '/Linearized', pdf ]
result = subprocess.run(cmd, capture_output=True, text=True).stdout
result = result.splitlines()
if (len(result) > 1):
    print('ERROR: more than 1 /Linearized dictionary found! Huh???')
    exit(-1)
is_linearized = False
for s in result:
    d = s.split(':')
    data.append({ 'category':'Marker', 'name':'Linearized', 'offset':int(d[0]), 'color':'MediumPurple'})
    is_linearized = True

# PDF "%%EOF" marker
cmd = ['grep', '-P', '--text', '--color=none', '--byte-offset', '--only-matching', '%%EOF', pdf ]
result = subprocess.run(cmd, capture_output=True, text=True).stdout
result = result.splitlines()
num_eofs = len(result)
for s in result:
    d = s.split(':')
    data.append({ 'category':'PDF file', 'name':'%%EOF', 'size':len('%%EOF')+1, 'offset':int(d[0]), 'color':'lightblue'})

# Close the input PDF file
in_pdf.close()

# Sort everything by file byte offset. For each object, "X Y obj" will come first, then a type marker (dict, array, etc), 
# then either XRef or ObjStm (keys in the stream extent dict), then "stream" then "endstream" (if a stream) then "endobj"
data = sorted(data, key=lambda d: d['offset'])

# Work out if the file ended correctly with a "%%EOF"
missing_last_eof = False
if (data[-1]['name'] != '%%EOF'):
    missing_last_eof = True

# Check physical file size in case of junk post-amble byte cavity
if (size > (data[-1]['offset'] + len(data[-1]['name']) + 2)):
    data.append({'category': 'PDF file', 
                 'name': 'Cavity ' + str(cavity_count),  
                 'offset': data[-1]['offset'] + len('%%EOF') + 1, 
                 'size': (size - data[-1]['offset'] - len('%%EOF') - 1),
                 'color': 'red'})
    cavity_count = cavity_count + 1

if (args.debugmode):
    print("\n\nRaw sorted data (%d):" % len(data))
    pp.pprint(data)

if (len(data) > MAX_MARKERS) and not args.force:
    print('Over %d markers were in the PDF file - this is too large for a Sankey diagram!' % MAX_MARKERS)
    exit(-1)

if (num_startxrefs != num_eofs) and not args.force:
    # @todo - work out how to determine end of Linearization section
    print('LOGIC ERROR: number of "%%EOF" (%) did not match number of "startxref" keywords - possibly hybrid reference??' % ( num_eofs, num_startxrefs) )
    exit(-2)

first_obj_in_pdf = -1
cavities = []
object_streams = []
data_size = len(data)
i = 0
# Convert absolute file offsets to sizes, correct types for "X Y obj" and work out stream compressed/uncompressed lengths
while (i < data_size):
    obj_num = -1            # for "X Y obj"
    end_last_marker = -1    # the very end of the marker + 1 - for cavity checking
    d = data[i]

    if (args.debugmode):
        print('%5d: %s' % (i, d))

    if ('%PDF-' in d['name']) or ('Cavity' in d['name']) or (d['name'] in ['trailer', 'startxref', 'xref', '%%EOF']):
        # Work out size (if req'd) and where next object should start (cavity detection)
        end_last_marker = d['offset'] + len(d['name']) + 1
        if ('size' not in d):
            data[i + 0]['size'] = end_last_marker - data[i + 0]['offset']
        i = i + 1                             # Move to next item in data
    elif (' obj' in d['name']):
        # Start of an indirect object: "X Y obj"
        if (first_obj_in_pdf < 0):
            first_obj_in_pdf = i
        obj_num = re.search(r'\d+', d['name']).group(0)
        if (data[i + 1]['type'] == 'dict') and (data[i + 2]['name'] == 'XRef'):
            assert (i + 6) < len(data)
            assert(data[i + 3]['name'] == 'stream')
            assert(data[i + 4]['name'] == 'endstream')
            assert(data[i + 5]['name'] == 'endobj')
            data[i + 0]['name'] = 'XRef stream ' + obj_num
            data[i + 0]['type'] = 'XRef stream' # X Y obj
            data[i + 1]['type'] = 'XRef stream' # dict
            data[i + 2]['type'] = 'XRef stream' # XRef
            data[i + 3]['type'] = 'XRef stream' # stream
            data[i + 4]['type'] = 'XRef stream' # endstream
            data[i + 5]['type'] = 'XRef stream' # endobj            
            # Calculate compressed data length from "stream" and to after "endstream" keywords (i.e. keywords inclusive)
            compressed_data = data[i + 4]['offset'] - data[i + 3]['offset'] + len('endstream') + 1
            data[i + 0]['compressed'] = compressed_data
            # Calculate the decompressed length of the stream data, including "stream" and "endstream" keywords + EOLs
            cmd = ['qpdf', '--show-object='+obj_num, '--filtered-stream-data', pdf ]
            result = subprocess.run(cmd, capture_output=True, timeout=TIMEOUT_SECS).stdout
            uncompressed_data = len(result) + len('stream') + len('endstream') + 2
            # EOLs can cause some mismatches for unfiltered streams
            if (uncompressed_data < compressed_data):
                uncompressed_data = compressed_data
            data[i + 0]['uncompressed'] = uncompressed_data
            # Work out size and where next object should start (cavity detection)
            end_last_marker = data[i + 5]['offset'] + len('endobj') + 1
            data[i + 0]['size'] = end_last_marker - data[i + 0]['offset']
            i = i + 6 # Skip over: dict, XRef, stream, endstream, endobj 
        elif (data[i + 1]['type'] == 'dict') and (data[i + 2]['name'] == 'ObjStm'):
            # @todo Cavities are not checked for in Object Streams
            assert (i + 6) < len(data)
            assert(data[i + 3]['name'] == 'stream')
            assert(data[i + 4]['name'] == 'endstream')
            assert(data[i + 5]['name'] == 'endobj')
            data[i + 0]['name'] = 'Object stream ' + obj_num
            data[i + 0]['type'] = 'Object stream' # X Y obj
            data[i + 1]['type'] = 'Object stream' # dict
            data[i + 2]['type'] = 'Object stream' # ObjStm
            data[i + 3]['type'] = 'Object stream' # stream
            data[i + 4]['type'] = 'Object stream' # endstream
            data[i + 5]['type'] = 'Object stream' # endobj            
            # Calculate compressed data length from "stream" and to after "endstream" keywords (i.e. keywords inclusive)
            compressed_data = data[i + 4]['offset'] - data[i + 3]['offset'] + len('endstream') + 1
            data[i + 0]['compressed'] = compressed_data
            # Work out size and where next object should start (cavity detection)
            end_last_marker = data[i + 5]['offset'] + len('endobj') + 1
            data[i + 0]['size'] = end_last_marker - data[i + 0]['offset']
            # Get the object stream data via QPDF. First get /N and /First entries.
            # Encrypted PDFs will have encrypted object streams so check QPDF return code
            # @todo - add password support
            cmd = ['qpdf', '--show-object='+str(obj_num), pdf ]
            result = subprocess.run(cmd, capture_output=True, timeout=TIMEOUT_SECS, text=True)
            if (result.returncode != 0):
                print('ERROR: ', end='')
                pp.pprint(result)
                exit(-1)
            result = result.stdout.splitlines()
            m = re.search(r'(?<=/N)\s?\d+', result[1])
            n = int(m.group(0))
            m = re.search(r'(?<=/First)\s?\d+', result[1])
            first = int(m.group(0))
            # Calculate the decompressed length of the stream data, including "stream" and "endstream" keywords + EOLs
            cmd = ['qpdf', '--show-object='+obj_num, '--filtered-stream-data', pdf ]
            result = subprocess.run(cmd, capture_output=True, timeout=TIMEOUT_SECS).stdout
            uncompressed_data = len(result) + len('stream') + len('endstream') + 2
            # EOLs can cause some mismatches for unfiltered streams
            if (uncompressed_data < compressed_data):
                uncompressed_data = compressed_data
            data[i + 0]['uncompressed'] = uncompressed_data
            # Use uncompressed data to work out objects in Object stream 
            length = len(result)
            first_line = result[:first].decode('utf-8')
            pairs = [int(s) for s in first_line.split() if s.isdigit()]
            objstm = []
            for j in range(0, (len(pairs) // 2) - 1):
                # PDF string objects can have non-UTF-8 byte sequences so do as 2 chars rather than a string
                c1 = chr(result[first + pairs[2*j + 1] + 0])
                c2 = chr(result[first + pairs[2*j + 1] + 1])
                objstm.append({'category': 'Object stream ' + str(obj_num), 
                            'name': str(pairs[2*j]) + ' 0 obj', 
                            'type': work_out_object_type(c1, c2),
                            'offset': first + pairs[2*j + 1], 
                            'size': pairs[2*j + 3] - pairs[2*j+1]})
                if (pairs[2*j] > MAX_MARKERS) and not args.force:
                    print('PDF object %d was in a compressed object stream - this is too large for a Sankey diagram!' % MAX_MARKERS)
                    exit(-1)
            c1 = chr(result[first + pairs[-1] + 0])
            c2 = chr(result[first + pairs[-1] + 1])
            objstm.append({'category': 'Object stream ' + str(obj_num), 
                            'name': str(pairs[-2]) + ' 0 obj', 
                            'offset': first + pairs[-1], 
                            'type': work_out_object_type(c1, c2),
                            'size': length - first - pairs[-1]})
            if (args.debugmode):
                print("\n\nObject stream %s (%d):" % (obj_num, len(objstm)))
                pp.pprint(objstm)
            object_streams.append(objstm)            
            i = i + 6 # Skip over: dict, XRef, stream, endstream, endobj 
        elif (data[i + 1]['type'] == 'dict') and (data[i + 2]['name'] == 'Linearized'):
            # Linearized PDF - set category from 1st object in file to 1st '%%EOF'
            # "X Y obj" / dict / Linearized / endobj
            assert(data[i + 3]['name'] == 'endobj')
            assert(is_linearized)
            assert(first_obj_in_pdf > 0)
            # Recategorize from top of file to end of Linearization dictionary
            for j in range(first_obj_in_pdf, i + 4, 1):
                data[j]['category'] = 'Linearized'
                data[j]['color'] = 'MediumPurple'
            # Recategorize from next object to next '%%EOF'
            if (num_eofs > 1) or (missing_last_eof and (num_eofs == 1)):
                j = i + 4
                while (data[j]['name'] != '%%EOF'):
                    data[j]['category'] = 'Linearized'
                    data[j]['color'] = 'MediumPurple'
                    j = j + 1
                # Also mark "%%EOF" as part of Linearization
                data[j]['category'] = 'Linearized'
                data[j]['color'] = 'MediumPurple'
            # Work out size and where next object should start (cavity detection)
            end_last_marker = data[i + 3]['offset'] + len('endobj') + 1
            data[i + 0]['size'] = end_last_marker - data[i + 0]['offset']
            i = i + 4
        elif (data[i + 1]['type'] == 'dict') and (data[i + 2]['name'] == 'stream'):
            # Normal stream
            assert((i + 5) < len(data))
            assert(data[i + 3]['name'] == 'endstream')
            assert(data[i + 4]['name'] == 'endobj')
            data[i + 0]['type'] = 'stream' # X Y obj
            data[i + 1]['type'] = 'stream' # dict
            data[i + 2]['type'] = 'stream' # stream
            data[i + 3]['type'] = 'stream' # endstream
            data[i + 4]['type'] = 'stream' # endobj            
            # Calculate compressed data length from "stream" and to after "endstream" keywords (i.e. keywords inclusive)
            compressed_data = data[i + 3]['offset'] - data[i + 2]['offset'] + len('endstream') + 1
            data[i + 0]['compressed'] = compressed_data
            # Calculate the decompressed length of the stream data, including "stream" and "endstream" keywords + EOLs
            cmd = ['qpdf', '--show-object='+obj_num, '--filtered-stream-data', pdf ]
            result = subprocess.run(cmd, capture_output=True, timeout=TIMEOUT_SECS).stdout
            uncompressed_data = len(result) + len('stream') + len('endstream') + 2
            # EOLs can cause some mismatches for unfiltered streams
            if (uncompressed_data < compressed_data):
                uncompressed_data = compressed_data
            data[i + 0]['uncompressed'] = uncompressed_data
            # Work out size and where next object should start (cavity detection)
            end_last_marker = data[i + 4]['offset'] + len('endobj') + 1
            data[i + 0]['size'] = end_last_marker - data[i + 0]['offset']
            i = i + 5 # Skip over: dict, stream, endstream, endobj 
        else:
            # just a basic object: number, string, array, etc. Followed by "endobj" marker
            assert(data[i + 2]['name'] == 'endobj')
            data[i + 0]['type'] = data[i + 1]['type']
            # Work out size and where next object should start (cavity detection)
            end_last_marker = data[i + 2]['offset'] + len('endobj') + 1
            data[i + 0]['size'] = end_last_marker - data[i + 0]['offset']
            i = i + 3 # Skip over: type, endobj

        # 'i' has now been updated index to the next core marker (keyword, "X Y obj", etc.)
    else:
        print('LOGIC ERROR: unexpected marker at data[%d]!' % i)
        pp.pprint(d)
        exit(-2)

    # Work out if there is a cavity between marker just checked and new marker (current 'i')
    assert(end_last_marker > 0)
    if (i < data_size):
        if ((data[i]['offset'] - end_last_marker) > 3):
            cavities.append({'category': data[i]['category'], 
                                'name': 'Cavity ' + str(cavity_count), 
                                'offset': end_last_marker + 1, 
                                'size': (data[i]['offset'] - end_last_marker - 1),
                                'color': 'red' })
            cavity_count = cavity_count + 1

# Add inter-object cavities (if any) to the sorted data and sort again by offset
if (len(cavities) > 0):
    if (args.debugmode):
        print("\n\nCavities (%d):" % len(cavities))
        pp.pprint(cavities)
    data = data + cavities
    data = sorted(data, key=lambda d: d['offset'])

# Process for Incremental Updates by looking for "%%EOF" and allowing for Linearization
incremental_update = 0
for d in data:
    if (is_linearized and (incremental_update > 1)):
        if (d['category'] == 'PDF file'):
            d['category'] = 'Incremental Update ' + str(incremental_update - 1)
            d['color'] = 'PaleGreen'
    elif (not is_linearized and (incremental_update > 0)):
        if (d['category'] == 'PDF file'):
            d['category'] = 'Incremental Update ' + str(incremental_update)
            d['color'] = 'PaleGreen'
    if (d['name'] == '%%EOF'):
        incremental_update = incremental_update + 1

if (args.debugmode):
    print("\n\nAfter Incremental Updates:")
    pp.pprint(data)

# Extract Linearization to make it a separate Sankey node
sum_linearization = 0
linearize = []
if is_linearized:
    for d in data:
        if (d['category'] == 'Linearized'):
            linearize.append(copy.deepcopy(d))
            if ('size' in d):
                sum_linearization = sum_linearization + d['size']
            d['category'] = 'Marker'  # 
    # Change the first to be the node grouping. Everything else is a Marker and will be purged 
    data[first_obj_in_pdf]['category'] = 'PDF file'
    data[first_obj_in_pdf]['name']     = 'Linearized'
    data[first_obj_in_pdf]['color']    = 'MediumPurple'
    data[first_obj_in_pdf]['size']     = sum_linearization
    # Append the Linearization
    data = data + linearize
    if (args.debugmode):
        print("\n\nLinearize (%d):" % len(linearize))
        pp.pprint(linearize)
        print("\n\nAfter Linearization:")
        pp.pprint(data)

#####################################################
# CAN NO LONGER SORT by file offset!!!
# ...because we have clustered the Linearization data
#####################################################

# Append object streams after the "PDF File" categories
for ostm in object_streams:
    for o in ostm:
        o['type'] = 'Compressed ' + o['type']
        data.append(o)

# Reverse iterate and delete all markers to compact data 
# Use -k/--keep to keep everything
if (not args.dont_delete):
    for i in range(len(data)-1, -1, -1):
        if data[i]['category'] in ['Marker']:
            del data[i]
    if (args.debugmode):
        print('\n\nPurge done')

# Cluster things by object type...
# Each stream comprises a dictionary (from "X Y obj" up to just before "stream" + "endobj") 
# + compressed stream data (incl. "stream" and "endstream" keywords). And we will also capture
# the uncompressed data size. 
cluster = []
sum_dicts = 0
sum_arrays = 0
sum_numbers = 0
sum_strings = 0
sum_stream_dicts = 0
sum_stream_data_compressed = 0
sum_stream_data_uncompressed = 0
stream_dicts = []
compressed = []
uncompressed = []
cavities = []
overhead = []
for d in data:
    if ('type' in d) and ('size' in d):
        if ('dict' in d['type']):
            cluster.append({'category':d['name'], 'name':'Dictionaries', 'size':d['size'], 'color':'wheat'})
            sum_dicts = sum_dicts + d['size']
        elif ('array' in d['type']):
            cluster.append({'category':d['name'], 'name':'Arrays', 'size':d['size'], 'color':'lightcyan'})
            sum_arrays = sum_arrays + d['size']
        elif ('number' in d['type']):
            cluster.append({'category':d['name'], 'name':'Numbers', 'size':d['size']})
            sum_numbers = sum_numbers + d['size']
        elif ('string' in d['type']):
            cluster.append({'category':d['name'], 'name':'Strings', 'size':d['size']})
            sum_string = sum_strings + d['size']
        elif ('stream' in d['type']):
            if ('compressed' in d) and ('uncompressed' in d):
                dict_size = d['size'] - d['compressed']
                if (dict_size < 0):
                    dict_size = 0
                cluster.append({'category':d['name'], 'name':'Stream dicts', 'size':dict_size, 'color':'wheat'})
                stream_dicts.append({'category':'Stream dict ' + d['name'], 'name':'Dictionaries', 'size':dict_size, 'color':'wheat'})
                sum_stream_dicts = sum_stream_dicts + dict_size
                cluster.append({'category':d['name'], 'name':'Compressed ' + d['name'], 'size':d['compressed'], 'color':'MistyRose'})
                compressed.append({'category':'Compressed ' + d['name'], 'name':'Uncompressed data', 'size':d['uncompressed'], 'color':'MistyRose'})
                sum_stream_data_compressed   = sum_stream_data_compressed   + d['compressed']
                sum_stream_data_uncompressed = sum_stream_data_uncompressed + d['uncompressed']

    if ('Cavity' in d['name']):
        assert('size' in d)
        cavities.append({'category':d['name'], 'name':'Cavities', 'size':d['size'], 'color':'red'})
    
    if (d['name'] in ['startxref', 'trailer', 'xref', '%%EOF']) or ('%PDF-' in d['name']):
        assert('size' in d)
        overhead.append({'category':d['name'], 'name':'Overhead', 'size':d['size'], 'color':'lightblue'})

if (args.debugmode):
    print('\n\nClustering done')

# Summarize clusters
for o in cluster:
    data.append(o)        
for o in compressed:
    data.append(o)
for o in uncompressed:
    data.append(o)
for o in cavities:
    data.append(o)
for o in overhead:
    data.append(o)
if (sum_stream_dicts > 0):
    data.append({'category':'Stream dicts', 'name':'Dictionaries', 'size':sum_stream_dicts, 'color':'wheat'})
if ((sum_dicts > 0) or (sum_stream_dicts > 0)):
    data.append({'category':'Dictionaries', 'name':'Objects', 'size':sum_dicts + sum_stream_dicts, 'color':'wheat'})
if (sum_arrays > 0):
    data.append({'category':'Arrays', 'name':'Objects', 'size':sum_arrays, 'color':'lightcyan'})
if (sum_numbers > 0):
    data.append({'category':'Numbers', 'name':'Objects', 'size':sum_numbers})
if (sum_strings > 0):
    data.append({'category':'Strings', 'name':'Objects', 'size':sum_strings})

# Make the CSV file for Sankey D3 
if (args.csvfile is not None):
    csv = open(args.csvfile, "wt")
    for d in data:
        if (d['category'] != 'Marker') and ('size' in d):
            if (args.debugmode):
                print(d)
            # Sankey CSV: Source, Target, Size (bytes), HTML color-name (optional)
            s = format('%s,%s,%d' % (d['category'].strip(), d['name'].strip(), d['size']))
            if ('color' in d):
                s = s + ',' + d['color'].strip()
            csv.writelines(s+'\n')
    csv.close()
    print('"%s" created.' % args.csvfile)
else:
    print("\n\nData (%d):" % len(data))
    pp.pprint(data)
