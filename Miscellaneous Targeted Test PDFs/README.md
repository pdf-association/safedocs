# Miscellaneous Targeted Test PDFs

## [FontinsideType3insideType3.pdf](FontinsideType3insideType3.pdf)

This PDF file contains one of the 14 standard PDF Type 1 fonts (non-embedded Helvetica) referenced from inside a Type 3 font which is itself referenced from inside a different Type 3 font. It is a targeted test case for applications which supposedly report all fonts in a PDF file (such as Poppler and Xpdf `pdffonts` CLI utilities). Correct output should be a list of 3 fonts (2 x Type 3 and 1 x Type 1 Helvetica). Note that Type 3 glyph descriptions are **NOT** required to clip to their widths so if the the string of Helvetica charcters is extended, those extra glyphs may or may not be displayed and this is **NOT an error** (officially stated as "implementation dependent"). 


## [PatternTextInsideText.pdf](PatternTextInsideText.pdf)

This PDF file contains a font object inside a shading pattern that is used as a fill for glyphs from a different font. Both fonts are from the 14 standard PDF Type 1 fonts and are non-embedded. It is a targeted test case for applications which supposedly report all fonts in a PDF file (such as Poppler and Xpdf `pdffonts` CLI utilities). Correct output should be a list of 2 x Type 1 fonts.


## [PDF-NoPageContents.pdf](PDF-NoPageContents.pdf)

This is a valid single page PDF that is an optimal empty page expressed via a missing `/Contents` key. The page object `/Contents` key is *optional* in all PDF specifications, and this PDF file can be used to ensure implementations correctly support this corner case. Correct rendered output is an empty page. No syntax or error messages should be generated.


___
*This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Contract No. HR001119C0079. Any opinions, findings and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the Defense Advanced Research Projects Agency (DARPA). Approved for public release.*
