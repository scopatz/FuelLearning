#! /usr/bin/env python
from optparse import OptionParser

from facility_info import facility_info
from used_fuel import make_used_fuel_tables, calc_used_fuel_rows
from fresh_fuel_info import make_reactor_groups, make_fresh_fuel_info

def main():
    usage = "usage: %prog [options] [filename]"
    parser = OptionParser(usage=usage)
    parser.add_option("-r", 
                  dest="reactor_list", default=None,
                  help="Specify which reactors to do the following actions for. " + \
                       "A list of whitespace spearated values. " + \
                       "If not given, all reactors are included.")
    parser.add_option("-s",
                  dest="slice", default=None,
                  help="Specify the rows for which to do the following calculation. " + \
                       "Uses a list or tuple to specify the slice: " + \
                       "e.g. '[1, -1, 100]' or '(50, 100)'.")
    parser.add_option("-f", "--facility-info",
                  action="store_true", dest="fac_info", default=False,
                  help="Generate the facility info table.")
    parser.add_option("-g", "--reactor-groups",
                  action="store_true", dest="reactor_groups", default=False,
                  help="Clean & replace the reactor groups from the file.")
    parser.add_option("-a", "--fresh-fuel-info",
                  action="store_true", dest="fresh_fuel_info", default=False,
                  help="Generate the fresh fuel info tables from raw assembly data.")
    parser.add_option("-u", "--used-fuel",
                  action="store_true", dest="used_fuel", default=False,
                  help="Generates new used fuel tables. Erases current data.")
    parser.add_option("-c", "--calc-used-fuel",
                  action="store_true", dest="calc_used_fuel", default=False,
                  help="Determine used fuel via a burnup calculation.")
    options, args = parser.parse_args()

    # set the filename
    if 0 < len(args):
        filename = args[0]
    else:
        filename = 'fuel_data.h5'

    # Set the reactor list
    if options.reactor_list == None:
        rx_list = None
    else:
        rx_list = options.reactor_list.split()

    # Set the row slice
    if options.slice == None:
        slice = (0, -1, 1)
    else:
        slice = eval(options.slice) 

    # Add the facility info table
    if options.fac_info:
        facility_info(filename)

    # Clean and replace reactor groups in heirarchy
    if options.reactor_groups:
        make_reactor_groups(filename)

    # Make fresh fuel tables
    if options.fresh_fuel_info:
        make_fresh_fuel_info(filename)

    # Make used fuel tables
    if options.used_fuel:
        make_used_fuel_tables(filename, rx_list)

    # Calculate used fuel rows
    if options.calc_used_fuel:
        calc_used_fuel_rows(filename, rx_list, slice)

if __name__ == "__main__":
    main()
