# Corrigendum #4 tests


NOTE: This file is encoded in UTF-8, but uses some relatively obscure Unicode codepoints which may or may not display properly.


## Test documents

Test files:

 - **A**: `unicode-test-U2F874-correct.pdf`
 - **B**: `unicode-test-U2F874-wrong.pdf`


These two test files test the implementation's Unicode normalisation target by checking how the CJK compatibility characters in [Corrigendum #4](https://www.unicode.org/versions/corrigendum4.html) are processed. Since Unicode 3.2 predates Corrigendum #4, the corrections should _not_ be applied when normalising PDF passwords.


Document **A** was encrypted with 'Password当!' (i.e. `Password<U+2F874>!`) as the password, with the correct normalisation applied according to Unicode 3.2. Document **B** was encrypted with the same password, but deliberately normalised against a more recent version of Unicode.

The encrypted documents are based on `unicode-test.pdf` from the `baseline/` directory.


## Test procedure


This test consists of four cases:

 1. Attempt to decrypt Document **A** using the password 'Password当!' (i.e. `Password<U+2F874>!`). Expected result: **Y**.
 2. Attempt to decrypt Document **A** using the password 'Password弳!' (i.e. `Password<U+5F33>!`). Expected result: **Y**.
 3. Attempt to decrypt Document **B** using the password 'Password当!' (i.e. `Password<U+2F874>!`). Expected result: **N**.
 4. Attempt to decrypt Document **B** using the password 'Password当!' (i.e. `Password<U+5F53>!`). Expected result: **Y**.

(**Y**: successful decryption, **N**: decryption failure)


## Test observations

We have identified the following behaviour patterns in PDF tools that support Unicode-based passwords.


### Pattern YYNY

This is the expected result; indicating that the password string is normalised against Unicode 3.2 (without applying Corrigendum #4).


### Pattern NYYY

This suggests that Unicode normalisation is applied, but against the wrong version of the Unicode standard.


### Pattern NYNY

This suggests that no Unicode normalisation is applied at all.


### Other

The passwords strings for tests 2 and 4 are already normalised (regardless of Unicode version). If those tests fail, the tool in question probably does not support Unicode-based passwords, or the password strings were not properly passed to the target application.
