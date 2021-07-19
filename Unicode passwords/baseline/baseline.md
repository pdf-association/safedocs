# Base file


## Test documents

Test files:
    - `unicode-test.pdf`
    - `unicode-test-actualtext.pdf`

The base file `unicode-test.pdf` is an unencrypted PDF 2.0 file containing the Unicode 12.1 'SQUARE ERA NAME REIWA' (U+32FF) codepoint as part of the **ToUnicode** for one of the glyphs used.

The base file `unicode-test-actualtext.pdf` is an unencrypted PDF 2.0 file containing the Unicode 12.1 'SQUARE ERA NAME REIWA' (U+32FF) codepoint as part of an **ActualText** entry for a piece of text content that "spells out" U+32FF using two glyphs.


## Test procedure

The files contain two lines of text. Copying and pasting the CJK text on the first line should produce "令和" (i.e. U+4EE4 followed by U+548C). On the other hand, copying and pasting the CJK text on the second line should produce "㋿" (i.e. U+32FF).
