# Unicode passwords

## Background

This folder contains PDF test files and documentation related to investigations into the correct handling of Unicode passwords in PDF (i.e. Unicode 3.2 with SASLprep/stringprep RFC algorithms) and Unicode in PDF content (supporting much later versions of Unicode). PDF Unicode password support is required to maintain backwards compatibility with legacy PDF files created under previous PDF specifications and hence has been 'held back' to Unicode 3.2. Confusion and bugs in Unicode password handling creates a potential for interoperability issues and malformed PDF files.

For clarity the terms "Unicode-for-passwords" and "Unicode-for-content" are used to disambiguate the context of which kind of Unicode is being described.

This research investigates:
* disambiguation of Unicode-for-passwords and Unicode-for-content according to the latest PDF 2.0 ISO standard [ISO 32000-2:2020](https://www.iso.org/standard/75839.html)
* the impact of correct and incorrect Unicode password normalization algorithms on interoperability
* creation of a corpus of PDF test files to assist PDF developers and those evaluating PDF software in understanding correct behaviour
* the behavior of several PDF processors in supporting Unicode-based passwords


## A very brief description / hypothesis

* Textual content in PDF files can contain Unicode representing recent updates to Unicode.
  - a well-known example is the [new Japanese Reiwa Era character introduced in Unicode 12.1](http://blog.unicode.org/2019/05/unicode-12-1-en.html) which was released on May 7, 2019
  - this includes both rendered textual content (defined in PDF content streams using font dictionaries having `ToUnicode` CMaps) and user interface elements (such as the names of bookmarks or layers) defined by PDF UTF-8 or UTF-16BE string objects
* Encrypted PDF files can use Unicode passwords
* For backwards compatibility, PDF Unicode passwords must comply with Unicode 3.2
* Password data entry user interface requirements are **not** described in the PDF file format specification.
* Some languages require [complex text layout](https://en.wikipedia.org/wiki/Complex_text_layout) (sometimes referred to as advanced text shaping) and/or have multiple ways a user might type the same resultant Unicode text.
* Thus Unicode passwords need to be "[normalized](https://en.wikipedia.org/wiki/Unicode_equivalence#Normalization)" prior to being used to encrypt/decrypt a PDF.
* The use of an incorrect Unicode password normalization algorithm will result in either:
  - an invalidly encrypted PDF file that cannot be decrypted by other (correct) implementations
  - a failure to decrypt a (valid) PDF file created by a correct implementation


## Unicode normalization algorithms

Many developers and users forget that [Unicode is constantly a moving target](https://www.unicode.org/history/publicationdates.html). As a result of ongoing improvements and expansion of the Unicode specification, Unicode normalization algorithms have also evolved, with older RFCs now marked as "obsolete" by IETF. This causes confusion for PDF developers where these older algorithms are still actively referenced in the latest PDF specifications, but third-party libraries or a lack of understanding of Unicode by developers sees more modern algorithms being used incorrectly.

Here are the timelines as defined in the IETF RFC documents of the two Unicode normalization algorithms referenced by PDF:

<div align="center">
First published December 2002:

[RFC 3454 Preparation of Internationalized Strings ("stringprep")](https://datatracker.ietf.org/doc/html/rfc3454) + [errata](https://www.rfc-editor.org/errata_search.php?rfc=3454&rec_status=0)

obsoleted May 2015 and replaced by:
[RFC 7564 PRECIS Framework: Preparation, Enforcement, and Comparison of Internationalized Strings in Application Protocols](https://datatracker.ietf.org/doc/html/rfc7564) + [errata](https://www.rfc-editor.org/errata_search.php?rfc=7564&rec_status=0)

obsoleted October 2017 and replaced by:
[RFC 8264 PRECIS Framework: Preparation, Enforcement, and Comparison of Internationalized Strings in Application Protocols](https://datatracker.ietf.org/doc/html/rfc8264) + [errata](https://www.rfc-editor.org/errata_search.php?rfc=8264&rec_status=0)
</div>

and

<div align="center">
First published February 2005:

[RFC 4013 SASLprep: Stringprep Profile for User Names and Passwords](https://datatracker.ietf.org/doc/html/rfc4013) + [errata](https://www.rfc-editor.org/errata_search.php?rfc=4013&rec_status=0)

obsoleted August 2015 and replaced by:
[RFC 7613 Preparation, Enforcement, and Comparison of Internationalized Strings Representing Usernames and Passwords](https://datatracker.ietf.org/doc/html/rfc7613)

obsoleted October 2017 and replaced by:
[RFC 8265 Preparation, Enforcement, and Comparison of Internationalized Strings Representing Usernames and Passwords](https://datatracker.ietf.org/doc/html/rfc8265) + [errata](https://www.rfc-editor.org/errata_search.php?rfc=8265&rec_status=0)
</div>


## Test case descriptions

 * [Baseline](baseline/baseline.md)
 * [Corrigendum #4](corrigendum4/corrigendum4.md)
 * [Corrigendum #5](corrigendum5/corrigendum5.md)

___
*This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Contract No. HR001119C0079. Any opinions, findings and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the Defense Advanced Research Projects Agency (DARPA). Approved for public release.*
