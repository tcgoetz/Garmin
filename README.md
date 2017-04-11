# Garmin
Tools for manipulating Garmin files (csv, fit).

Libraries:
* Garmin - GarminXlsxWriter writes Excel XLSX files suing data extracted from Garmin files

* Fit - parses FIT files, mostly focused on monitoring FIT files for now

Scripts:
* garmin_connect_csv_to_xlsx - turns a directory of CSV files exported from Garmin Connect Reports pages into an XLSX file with the
  addition of some derived stats. More info: http://blog.tom-goetz.org/2017/03/export-all-of-your-garmin-connect-data.html

* garmin_connect_fit_to_xlsx - turns a directory of monitoring FIT files, exported from the Garmin Connect daily view (export original),
  into a Excel XLSX file with worksheets for the file device headers, monitoring info headers, monitoring data, derived hourly stats,
  derived daily stats, and derived overall stats.
  
  
