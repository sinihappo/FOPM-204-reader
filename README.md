# FOPM-204-reader
Python program to read FS.com FOPM-204 memory

To run, simply:

`./fopm-reader.py /dev/ttyUSB0`

and if you want to create a CSV file as well:

`./fopm-reader.py -c foo.csv /dev/ttyUSB0`

or XLSX files:

`./fopm-reader.py -X foo.xls /dev/ttyUSB0`

For XLSX export to work, you need XlsxWriter package at here: https://github.com/jmcnamara/XlsxWriter.git or here: https://github.com/sinihappo/XlsxWriter.git
