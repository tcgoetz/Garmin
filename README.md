# Notice
I am no longer working on this project. You can achieve all of the same results with the garminDB project. Once you have your data in a DB you can export it to CSV or XLXS using a DB browser. https://github.com/tcgoetz/GarminDB

# Garmin
Tools for manipulating Garmin files (csv, fit) written in Python.

Libraries:
* Garmin - GarminXlsxWriter writes Excel XLSX files suing data extracted from Garmin files

* Fit - parses FIT files, mostly focused on monitoring FIT files for now

Scripts:
* garmin_connect_csv_to_xlsx - turns a directory of CSV files exported from Garmin Connect Reports pages into an XLSX file with the
  addition of some derived stats.
    - More info: http://blog.tom-goetz.org/2017/03/export-all-of-your-garmin-connect-data.html
    - example: ./garmin_connect_csv_to_xlsx.py -s 02/22/2017 -o garmin.xlsx -i 20170314_csv

* garmin_connect_fit_to_xlsx - turns a directory of monitoring FIT files, exported from the Garmin Connect daily view (export original),
  into a Excel XLSX file with worksheets for the file device headers, monitoring info headers, monitoring data, derived hourly stats,
  derived daily stats, and derived overall stats.
    - More info: http://blog.tom-goetz.org/2017/04/turn-garmin-connect-daily-export-files.html
    - example: ./garmin_connect_fit_to_xlsx.py -e -o garmin.xlsx -d 2017_monitoring
  
  
