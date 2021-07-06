# Base file


## Test documents

Test files:
    - `unicode-test.pdf`

The base file `unicode-test.pdf` is an unencrypted PDF 2.0 file with some **ActualText** containing the Unicode 12.1 'SQUARE ERA NAME REIWA' (U+32FF) codepoint.


## Test procedure

The file contains two lines of text. Copying and pasting the CJK text on the first line should produce "令和" (i.e. U+4EE4 followed by U+458C). On the other hand, copying and pasting the CJK text on the second line should produce "㋿" (i.e. U+32FF).
