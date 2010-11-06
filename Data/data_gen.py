#! /usr/bin/env python
from optparse import OptionParser

from facility_info import facility_info

def main():
    usage = "usage: %prog [options] [filename]"
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--facility-info",
                  action="store_true", dest="FacInfo", default=False,
                  help="Generate the facility info table.")
    options, args = parser.parse_args()

    # set the filename
    if 0 < len(args):
        filename = args[0]
    else:
        filename = 'fuel_data.h5'

    # Add the facility info table
    if options.FacInfo:
        facility_info(filename)

if __name__ == "__main__":
    main()
