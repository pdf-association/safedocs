# PDF Dialects

This corpus of hand-crafted targeted PDF test files aims to evaluate the correct handling of PDF "dialects" according to ISO 32000 (the core PDF specification). This including subtleties between parsing rules for the PDF file body and PDF content streams.

The files in this corpus include:

## Dictionaries in content streams

### [Dialect-ContentStreams.pdf](Dialect-ContentStreams.pdf)

This test case should <span style="color:green">**PASS**</span>. It tests the parsing of direct (inline) PDF dictionaries in all areas of PDF content streams where the presence of a PDF dictionary (as denoted by `<<` and `>>` tokens) is syntactically valid. This includes marked content property list operands, inline image dictionary custom keys and between the PDF compatibility operators, `BX` and `EX` (Table 33, ISO 32000-2:2020). Within a compatibility section, *"[u]nrecognised operators (along with their operands) shall be ignored without error until the balancing EX operator is encountered"*.

### [Dialect-ContentStreamsViaResourceNames.pdf](Dialect-ContentStreamsViaResourceNames.pdf)

This test case should <span style="color:green">**PASS**</span> and is an extension of [Dialect-ContentStreams.pdf](Dialect-ContentStreams.pdf). It tests the parsing of direct (inline) PDF dictionaries in PDF content streams where a PDF dictionary is syntactically valid and when the value of a private dictionary key (i.e. a key not defined in the PDF specification) is specified using a named resource, as defined in a **Resources**  sub-dictionary. Note that the **Properties** sub-dictionary *only applies* to marked-content operators, so additional custom keys in **Resources** are required to declare the named resources. In this case, the named resource is an indirect reference to the very same page content stream, which is syntactically valid.

### [Dialect-ContentStreamsWithIndirectRefs.pdf](Dialect-ContentStreamsWithIndirectRefs.pdf)

This test case should <span style="color:red">**FAIL**</span> because indirect references are **never** permitted in PDF content streams. Clause 7.8.2 Content streams explicitly states: *"Indirect objects and object references shall not be permitted at all"*. It is also a variant of [Dialect-ContentStreams.pdf](Dialect-ContentStreams.pdf) however it is invalid according to ISO 32000.

The precise error message and results from this negative test case are entirely implementation dependent and beyond the scope of the PDF file format specification. Most likely a syntax error message might be expected.

## Stream vs dictionary

Clause 7.3.8 in ISO 32000-2:2020 states "_A stream shall consist of a dictionary followed by zero or more bytes bracketed between the keywords **stream** (followed by newline) and **endstream**_". Thus every PDF stream object is only recognizable as a stream due to the presence of the `stream` keyword occurring after the dictionary close token `>>` in place of the `endobj` keyword that would identify a dictionary.
- _What do parsers do when expecting a stream, but get just a dictionary? Is this the same as a stream with zero bytes?_
- _What do parsers do when expecting a (pure) dictionary but actually get a stream? Do they ignore the stream or flag an error?_
- _Do parsers read beyond the dictionary close token `>>` to disambiguate if the object is a stream or dictionary?_
- _Do parsers use the referencing context to determine if an object should be a stream vs dictionary, or do they rely on the correctness of input?_

These questions and the test files are of most interest to parser developers; to end users for assessing syntax preflight processors (_they should report all such errors!_) and help users of binary forensic tools identify which tokens terminate parsing conditions.

### Stream is just a dictionary  

The lack of `stream` and `endstream` keywords could arguably be interpreted as the semantic equivalent of a zero-length stream which can be syntactically (and semantically) valid depending on the type of stream (e.g. zero length content or Metadata streams are both valid), rather than a syntax error which is what the PDF specification implies. The test case [Dialect-StreamIsDict.pdf](Dialect-StreamIsDict.pdf) tests this with valid stream dictionaries with `/Length 0` but missing the officially required `stream` and `endstream` keywords. There is no visible content in this PDF - correct output is a blank page.

At the time of writing, only Xpdf 4.03 and the Adobe Acrobat DC Professional preflight "Syntax check" feature recognize these issues, but still process the PDF (or so it appears).

### Dictionary is a really a stream

According to the PDF specification this should also be a syntax error, but since stream dictionaries are always required, parsers may accept this construct anyway and silently ignore the `stream` and `endstream` keyword and stream content. The test case [Dialect-DictIsStream.pdf](Dialect-DictIsStream.pdf) tests this by adding the `stream` and `endstream` keywords to various dictionaries that are not stream objects. The dictionaries also have the entry `/Length 0` added to validly represent the stream.  Parsers that terminate on just the dictionary close token `>>` will not notice this malformation. The page content of this test PDF is Helvetica text "**Dict is Stream**".

This PDF causes a number of PDF processor issues and some very confusing error messages!

___
*This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Contract No. HR001119C0079. Any opinions, findings and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the Defense Advanced Research Projects Agency (DARPA). Approved for public release.*
