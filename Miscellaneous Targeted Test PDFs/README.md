# Miscellaneous Targeted Test PDFs

A miscellaneous collection of hand-coded targeted PDF files for testing specific corner cases of the PDF specification where various PDF implementations (CLI and GUI) fail to work correctly, or not at all. This results in demonstrable parser differentials, unreliable results and significant differences for users.

## Fonts

Whether it be for long-term archival or record keeping reasons, professional printing, content extraction or reuse, or text search, many PDF workflows and use cases require an accurate understanding of fonts in a PDF.  

### [FontinsideType3insideType3.pdf](FontinsideType3insideType3.pdf)

This targeted PDF file contains one of the 14 standard PDF Type 1 fonts (non-embedded Helvetica) referenced from inside a Type 3 font which is itself then referenced from inside a different Type 3 font. It is a targeted test case for applications which supposedly report all fonts in a PDF file (such as Poppler and Xpdf `pdffonts` CLI utilities and File Properties dialogs in many interactive PDF viewers). Correct output should be a list of 3 fonts (2 x Type 3 (FType3A and FType3B) and 1 x Type 1 Helvetica). Note that Type 3 glyph descriptions are **NOT** required to clip to their widths so if the string of Helvetica characters is extended, those extra glyphs may or may not be displayed and this is **NOT an error** (officially stated in ISO 32000 as "_implementation dependent_").

![Image](FontinsideType3insideType3.png)

### [PatternTextInsideText.pdf](PatternTextInsideText.pdf)

This targeted PDF file contains a font object referenced from inside a Shading Pattern that is then used as a fill for glyphs from a different font. Both fonts are from the 14 standard PDF Type 1 fonts and are non-embedded. It is a targeted test case for applications which supposedly report all fonts in a PDF file (such as Poppler and Xpdf `pdffonts` CLI utilities and `File | Properties` dialogs in many interactive PDF viewers).

Correct output should be a list of 2 x Type 1 fonts (Helvetica (_san serif, large blue stroked outline_) and Times-Italic (_serif, smaller red text_)). An example of a correct list of fonts for this PDF is shown in the left portion of the following image - the right portion incorrectly lists just a single font:

![Image](PatternTextInsideText.png)

### [ContentStreamCycleType3insideType3.pdf](ContentStreamCycleType3insideType3.pdf)

This is a <span style="color:red;font-weight:bold;">negative test case</span> where a Type 3 glyph description stream (`CharProc`) references another Type 3 glyph description stream which then references one of the 14 standard PDF Type 1 fonts (non-embedded Helvetica) which is filled using a pattern that references back to the first Type 3 font and the same glyph description stream, thus creating an "infinite recursion" when rendering. This PDF file is only syntactically valid (i.e. at a lexical and token level), but semantically invalid because of the cycle between the Type 3 glyph description streams.

![Image](ContentStreamCycleType3insideType3.png)

The main goal of this test file is to test for vulnerabilities such as crashes, deadlock or OOM in PDF implementations. Because this PDF is invalid, precise behavior of PDF implementations is undefined, as it is outside the scope of ISO 32000 and all legacy PDF specifications.

A recent PDF errata ([Issue #111](https://github.com/pdf-association/pdf-issues/issues/111)) acknowledges this issue with additional text to warn implementations - see [https://pdf-issues.pdfa.org/32000-2-2020/clause09.html#H9.6.4](https://pdf-issues.pdfa.org/32000-2-2020/clause09.html#H9.6.4).  

### [ContentStreamNoCycleType3insideType3.pdf](ContentStreamNoCycleType3insideType3.pdf)

This **valid** test case is almost identical to [ContentStreamCycleType3insideType3.pdf](ContentStreamCycleType3insideType3.pdf) above, however a single indirect reference of the Font resource to the Type 3 font that causes the "infinite loop" (`6 0 R`) is altered to refer to one of the 14 standard PDF Type 1 fonts (non-embedded Helvetica, `11 0 R`). Thus it is no longer an invalid PDF. The test case then becomes a rendering (_and performance!_) test case for matrix mathematics involving nested page, text, font and pattern spaces, as well as behavior related to filling and stroking, and colored and uncolored Type 3 glyphs. 

This **valid** test case can also be used to confirm that all fonts are being accurately reported: correct output should be a list of 2 x Type 3 fonts and 1 x Type 1 font (Helvetica).

![Image](ContentStreamNoCycleType3insideType3.png)

# Page Object

## [PDF-NoPageContents.pdf](PDF-NoPageContents.pdf)

This is a valid single page PDF that is an optimal empty page expressed via a missing `/Contents` key. The page object `/Contents` key is *optional* in all PDF specifications, and this PDF file can be used to ensure implementations correctly support this corner case. Correct rendered output is an empty page. No syntax or error messages should be generated.

___
*This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Contract No. HR001119C0079. Any opinions, findings and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the Defense Advanced Research Projects Agency (DARPA). Approved for public release.*
