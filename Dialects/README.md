# PDF Dialects

This corpus of hand-crafted targeted PDF test files aims to evaluate the correct handling of PDF "dialects" according to ISO 32000 (the core PDF specification). This including subtlities between parsing rules for the PDF file body and PDF content streams.

The files in this corpus include:

## [Dialect-ContentStreams.pdf](Dialect-ContentStreams.pdf)

This test case should <span style="color:green">**PASS**</span>. It tests the parsing of direct (inline) PDF dictionaries in all areas of PDF content streams where the presence of a PDF dictionary (as denoted by `<<` and `>>` tokens) is syntactically valid. This includes marked content property list operands, inline image dictionary custom keys and between the PDF compatibility operators, `BX` and `EX` (Table 33, ISO 32000-2:2020). Within a compatibility section, *"[u]nrecognised operators (along with their operands) shall be ignored without error until the balancing EX operator is encountered"*.


## [Dialect-ContentStreamsViaResourceNames.pdf](Dialect-ContentStreamsViaResourceNames.pdf)

This test case should <span style="color:green">**PASS**</span> and is an extension of [Dialect-ContentStreams.pdf](Dialect-ContentStreams.pdf). It tests the parsing of direct (inline) PDF dictionaries in PDF content streams where a PDF dictionary is syntactically valid and when the value of a private dictionary key (i.e. a key not defined in the PDF specification) is specified using a named resource, as defined in a **Resources**  sub-dictionary. Note that the **Properties** sub-dictionary *only applies* to marked-content operators, so additional custom keys in **Resources** are required to declare the named resources. In this case, the named resource is an indirect reference to the very same page content stream, which is syntactically valid.


## [Dialect-ContentStreamsWithIndirectRefs.pdf](Dialect-ContentStreamsWithIndirectRefs.pdf)

This test case should <span style="color:red">**FAIL**</span> because indirect references are **never** permitted in PDF content streams. Clause 7.8.2 Content streams explicitly states: *"Indirect objects and object references shall not be permitted at all"*. It is also a variant of [Dialect-ContentStreams.pdf](Dialect-ContentStreams.pdf) however it is invalid according to ISO 32000.

The precise error message and results from this negative test case are entirely implementation dependent and beyond the scope of the PDF file format specification. Most likely a syntax error message might be expected. 


___
*This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Contract No. HR001119C0079. Any opinions, findings and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the Defense Advanced Research Projects Agency (DARPA). Approved for public release.*
