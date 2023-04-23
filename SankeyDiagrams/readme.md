# Sankey diagrams for PDF layout visualization

A **HIGHLY** inefficient Python script to work out the layout of a PDF using Linux `grep` and QPDF. No PDF parser is being used!

Avoid using on large PDFs or PDFs with many objects (although things can be forced with `--f`). Script will exit if it sees `MAX_MARKERS` or greater. Only works with valid PDFs that work with QPDF and that are not encrypted with a User Password.

The Python script creates a CSV file suitable for cutting & pasting to create a Sankey diagram at https://observablehq.com/@pdf/visualizing-pdfs-with-sankey-diagrams. Some hand-tweaking of the data may also be desireable.


```
usage: sankey-hack.py [-h] [-c CSVFILE] [-d] [-k] [-f] [-p PDFFILE]

options:
  -h, --help            show this help message and exit
  -c CSVFILE, --csv CSVFILE
                        Output CSV filename (always overwritten)
  -d, --debug           Verbose debugging output of internal Python data
  -k, --keep            Keep all data markers in debug output
  -f, --force           Force processing by ignoring possible data issues
  -p PDFFILE, --pdf PDFFILE
                        Input PDF filename
```

* grep-ing PDF files always requires `--text`. A typical grep command looks like this:
```bash
grep -P --text --color=none --byte-offset --only-matching <REGEX> <PDFFILE>
```

* Due to very flexible PDF EOL rules, it is **not** reliable to always use `^` (start-of-line) in regexes!

* Note also the special PDF Whitespace (Table 1) (regex: `[\\000\\011\\012\\014\\015\\040]`) - this is NOT the same as `[[:blank:]]`!!

# Good exemplar files

- Take any PDF and prepend and append junk bytes - this will then show up as red cavities in the Sankey diagram 

- BFO-namespaces.pdf: small, easy to understand, compression not very effective

- Canary-dot-org-PDF.pdf: Linearized with xref stream, a few cavities

- ASUS-Monitor-Invoice.pdf: not too many objects, some small cavities, lots of data streams with decent compression

- MaliciousJavaScript.pdf: incremental update

- ProgressOnFileObservatory_PDFDays2022_JPL_20220909.pdf: PROBLEMATIC!! Syntax is CRs not SPACES so grep doesn't work...

## Linux batch usage example

```bash
$ find . -iname "*.pdf" -exec python3 sankey-hack.py --pdf {} --csv sankey.csv \;
```

---

This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Contract No. HR001119C0079.
Any opinions, findings and conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the Defense Advanced Research Projects Agency (DARPA). Approved for public release.
