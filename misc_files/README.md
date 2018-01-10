###How to Git.txt

User guide for Git

---

###load_csv_into_me.xlsm

Usage:

1. Place in the same directory as the server-generated CSV files
2. Open the .xlsm workbook in Excel, enable macros
3. Press Alt-F8, then run the macro. This loads the CSV files with the
correct encoding and delimiter settings
4. When saving, make sure you save as CSV. The saved CSV will retain
the correct encoding settings.
5. You can only save one sheet at a time.
6. Run-time error 1004 means one of the currently open sheets in your
workbook shares its name with one of the files the macro is trying
to load. Close the sheet or rename the incoming file.
7. I wrote the macro so it's safe.
