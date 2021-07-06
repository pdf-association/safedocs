# Corrigendum #5 tests


NOTE: This file is encoded in UTF-8, but includes Unicode codepoint sequences that may behave unpredictably.


## Test documents

Test files:

 - **A**: `unicode-corrigendum5-fixed.pdf`
 - **B**: `unicode-corrigendum5-unicode32-once.pdf`
 - **C**: `unicode-corrigendum5-unicode32-twice.pdf`

These two test files test the implementation's Unicode normalisation target by checking how one of the problematic sequences in [PR #29](https://www.unicode.org/review/pr-29.html#Problem_Sequences) is handled.  Prior to [Corrigendum #5](https://www.unicode.org/versions/corrigendum5.html), there was an issue with normalisation idempotency when applied to certain contrived inputs. While these inputs are extremely unlikely to appear in real-world data, they still represent a consistency problem with the specification.

The crucial difference between Corrigendum #5 and other corrigenda (like [Corrigendum #4](https://www.unicode.org/versions/corrigendum4.html)) is that Corrigendum #5 corrects an error in a Unicode algorithm, rather than the Unicode Character Database (UCD). Therefore, merely using a UCD version with data from Unicode 3.2 is not sufficient to emulate past behaviour.

Document **A** was encrypted with the password 'ᄀ̀ᅡ̣' (i.e. `<U+1100><U+0300><U+1161><U+0323>`), without normalisation. This is the behaviour one would expect with a recent version of Unicode. Document **B** was encrypted with the password '가̣̀' (i.e. `<U+AC00><U+0300><U+0323>`), without further normalisation. This the previous password with legacy NF(K)C normalisation applied once. Document **C** was encrypted with the password '가̣̀' (i.e. `<U+AC00><U+0323><U+0300>`). This password is already in normal NF(K)C normal form. The original password normalises to this value when legacy NF(K)C normalisation is applied twice. The second password also normalises to this value in both Unicode 3.2 and in recent Unicode versions.


Note 1: According to [PR #29](https://www.unicode.org/review/pr-29.html#Problem_Sequences), application behaviour was already inconsistent before Corrigendum #5 was applied. Therefore, not all of the tests we describe here have an expected result, reflecting the lack of consensus.

Note 2: For the purposes of these tests, there is no difference between Unicode NFKC and NFC normalisation.


## Test procedure

 1. Attempt to decrypt document **A** with the password 'ᄀ̀ᅡ̣' (i.e. `<U+1100><U+0300><U+1161><U+0323>`). This may or may not succeed.
 2. Attempt to decrypt document **B** with the password 'ᄀ̀ᅡ̣' (i.e. `<U+1100><U+0300><U+1161><U+0323>`). This may or may not succeed.
 3. Attempt to decrypt document **C** with the password 'ᄀ̀ᅡ̣' (i.e. `<U+1100><U+0300><U+1161><U+0323>`). Expected result: **N**.
 4. Attempt to decrypt document **B** with the password '가̣̀' (i.e. `<U+AC00><U+0300><U+0323>`). Expected result: **N**.
 5. Attempt to decrypt document **C** with the password '가̣̀' (i.e. `<U+AC00><U+0300><U+0323>`). Expected result: **Y**.
 6. Attempt to decrypt document **C** with the password '가̣̀' (i.e. `<U+AC00><U+0323><U+0300>`). Expected result: **Y**.

(**Y**: successful decryption, **N**: decryption failure)


## Test observations

We have identified the following behaviour patterns in PDF tools that support Unicode-based passwords.


### Pattern NYNNYY (not observed yet)

This indicates that the application follows the letter of the Unicode 3.2 normalisation algorithm, before the fix from Corrigendum #5 was applied.


### Pattern YNNNYY

This indicates that the application applies the fixed version of the normalisation algorithm from Corrigendum #5.


### Pattern YNNYNY

This suggests that Unicode normalisation is not applied at all.


### Pattern YNNYYY

This suggests that the application tries both normalised and non-normalised inputs, against a recent version of Unicode.
