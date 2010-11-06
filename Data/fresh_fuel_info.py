import csv
import time
import tables as tb

from facility_info import get_reactor_id_map

time_format = "%m/%d/%y %H:%M:%S"

def make_reactor_groups(hdf5_file):
    # Open the HDF5 file
    opened_here = False
    if isinstance(hdf5_file, basestring):
        opened_here = True
        hdf5_file = tb.openFile(hdf5_file, 'a')

    h5r = hdf5_file.root
    rx_id_map = get_reactor_id_map(hdf5_file)

    # Make the reactor groups
    for rx_id in rx_id_map.keys():
        # Remove pre-existing group
        if hasattr(h5r, rx_id_map[rx_id]):
            hdf5_file.removeNode(h5r, rx_id_map[rx_id], recursive=True)

        hdf5_file.createGroup(h5r, rx_id_map[rx_id])

    # Close the HDF5 file
    if opened_here:
        hdf5_file.close()


class FreshFuelInfo(tb.IsDescription):
    assembly_id     = tb.StringCol(itemsize=15, pos=0)
    mass            = tb.Float64Col(pos=1)
    enrichment      = tb.Float64Col(pos=2)
    burnup          = tb.Float64Col(pos=3)
    assembly_type   = tb.StringCol(itemsize=10, pos=4)
    assembly_status = tb.StringCol(itemsize=5,  pos=5)
    storage_id      = tb.StringCol(itemsize=5,  pos=6)
    discharge_cycle = tb.StringCol(itemsize=3,  pos=7)
    discharge_date  = tb.Time64Col(pos=8)


def make_fresh_fuel_info(hdf5_file, csv_file='raw/tblFuelFresh.csv'):
    # Open the HDF5 file
    opened_here = False
    if isinstance(hdf5_file, basestring):
        opened_here = True
        hdf5_file = tb.openFile(hdf5_file, 'a')

    h5r = hdf5_file.root
    rx_id_map = get_reactor_id_map(hdf5_file)

    # Make new fresh fuel tables
    for rx_id in rx_id_map.keys():
        rx_group = getattr(h5r, rx_id_map[rx_id])
        # Remove pre-existing table
        if hasattr(rx_group, 'fresh_fuel_info'):
            hdf5_file.removeNode(rx_group, 'fresh_fuel_info')

        hdf5_file.createTable(rx_group, 'fresh_fuel_info', FreshFuelInfo)

    # Read in the assembly data and write it to the HDF5 file
    fresh_fuel_file = csv.reader(open(csv_file, 'rb'))

    for ffrow in fresh_fuel_file:
        # Find the right group, table, and row
        rx_group = getattr(h5r, rx_id_map[int(ffrow[0])])
        rx_table = rx_group.fresh_fuel_info
        rx_row = rx_table.row

        # Prepare the data
        rx_row['assembly_id'] = ffrow[2]
        rx_row['mass']        = float(ffrow[3])
        rx_row['enrichment']  = float(ffrow[4]) / 100.0 
        rx_row['burnup']      = float(ffrow[5]) / 1000.0 

        rx_row['assembly_type']   = ffrow[6]
        rx_row['assembly_status'] = ffrow[7]
        rx_row['storage_id']      = ffrow[9]

        rx_row['discharge_cycle'] = ffrow[10]
        try:
            dd = time.mktime( time.strptime(ffrow[11], time_format) )
        except ValueError:
            dd = 0.0
        rx_row['discharge_date'] = dd

        # Append this row
        rx_row.append()
        rx_table.flush()

    # Close the HDF5 file
    if opened_here:
        hdf5_file.close()


if __name__ == "__main__":
    make_reactor_groups("test.h5")
    make_fresh_fuel_info("test.h5")
