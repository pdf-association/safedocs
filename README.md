# Safedocs

![GitHub](https://img.shields.io/github/license/pdf-association/safedocs)
&nbsp;&nbsp;&nbsp;
![LinkedIn](https://img.shields.io/static/v1?style=social&label=LinkedIn&logo=linkedin&message=PDF-Association)
&nbsp;&nbsp;&nbsp;
![Twitter Follow](https://img.shields.io/twitter/follow/PDFAssociation?style=social)
&nbsp;&nbsp;&nbsp;
![YouTube Channel Subscribers](https://img.shields.io/youtube/channel/subscribers/UCJL_M0VH2lm65gvGVarUTKQ?style=social)


Artifacts from the [DARPA-funded SafeDocs research program](https://www.pdfa.org/safedocs-darpa-does-pdf/).

## Compacted Syntax
The compacted PDF syntax test file and associated matrix is for testing PDF lexical analyzers to ensure they comply with some of the finer points of the PDF standard and to ensure interoperability between implementations. The focus is on non-whitespace token delimiters for different adjacent PDF objects. Read more [here](https://www.pdfa.org/perfecting-pdf-lexical-analysis/).

## Miscellaneous Targeted Test PDFs
This folder contains miscellaneous PDF files which have been hand-coded for targeted testing of PDF processors. The `*-raw.pdf` files have been hand-written in a text editor and have then been repaired using `mutool clean` to correct stream lengths, xref offsets, etc. to create the non-`-raw` equivalent PDFs. Test with the PDF files that do **NOT** have `-raw` in their filenames as these are 100% valid PDFs. The README file in this folder explains each targeted test case.

## Unicode passwords
This folder contains PDF test files and documentation related to investigations into the correct handling of Unicode passwords in PDF (i.e. Unicode 3.2 with SASLprep/stringprep RFC algorithms) and Unicode in content (supporting much later versions of Unicode). PDF Unicode password support is required to maintain backwards compatibility with legacy PDF files created under previous PDF specifications. Confusion and bugs in Unicode password handling creates a potential for interoperability issues and malformed PDF files.

___
*This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Contract No. HR001119C0079. Any opinions, findings and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the Defense Advanced Research Projects Agency (DARPA). Approved for public release.*
