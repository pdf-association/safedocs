# safedocs
Artifacts from the DARPA-funded SafeDocs research program

## Compacted Syntax
The compacted PDF syntax test file and associated matrix is for testing PDF lexical analyzers to ensure they comply with some of the finer points of the PDF standard and to ensure interoperability between implementations. The focus is on non-whitespace token delimiters for different adjacent PDF objects.

## Miscellaneous Targeted Test PDFs
This folder contains miscellaneous PDF files which have been hand-coded for targeted testing of PDF processors. The `*-raw.pdf` files have been hand-written in a text editor and have then been repaired using `mutool clean` to correct stream lengths, xref offsets, etc. to create the non-`-raw` equivalent PDFs. Test with the PDF files that do **NOT** have `-raw` in their filenames as these are 100% valid PDFs. The README file in this folder explains each targeted test case.

___
*This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Contract No. HR001119C0079. Any opinions, findings and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the Defense Advanced Research Projects Agency (DARPA). Approved for public release.*
