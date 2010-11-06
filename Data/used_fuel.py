import os
import time
import tables as tb

import BriPy as bp

from facility_info import get_reactor_id_map

# Load isos2track
data_dir = os.getenv("BRIGHT_DATA")
lwr_data = data_dir + "/LWR.h5"
bp.load_isos2track_hdf5(lwr_data)

# We are going to capture the output, so don't write it out automatically.
bp.write_text(False)
bp.write_hdf5(False)

# Generate a used fuel table description
UsedFuel = {
    'assembly_id': tb.StringCol(itemsize=15, pos=0), 
    'burnup':      tb.Float64Col(pos=1),
    'mass':        tb.Float64Col(pos=2),
    }

nbuf = len(UsedFuel)
i2t = bp.isos2track()

for i in range(len(i2t)):
    UsedFuel[bp.isoname.zzaaam_2_LLAAAM(i2t[i])] = tb.Float64Col(pos=nbuf + i)


def make_used_fuel_tables(hdf5_file, rx_list=None):
    # Open the HDF5 file
    opened_here = False
    if isinstance(hdf5_file, basestring):
        opened_here = True
        hdf5_file = tb.openFile(hdf5_file, 'a')

    h5r = hdf5_file.root

    # Grab reactor list if not specified
    if rx_list == None:
        rx_id_map = get_reactor_id_map(hdf5_file)
        rx_list = sorted(rx_id_map.values())

    # Make new used fuel tables
    for rx in rx_list:
        rx_group = getattr(h5r, rx)
        # Remove pre-existing table
        if hasattr(rx_group, 'used_fuel'):
            hdf5_file.removeNode(rx_group, 'used_fuel')

        hdf5_file.createTable(rx_group, 'used_fuel', UsedFuel,
            title="Used Fuel for {0}".format(rx), 
            expectedrows=len(rx_group.fresh_fuel_info),
            )

    # Close the HDF5 file
    if opened_here:
        hdf5_file.close()


def calc_used_fuel_rows(hdf5_file, rx_list=None, slice=(0,-1, 1)):
    # Open the HDF5 file
    opened_here = False
    if isinstance(hdf5_file, basestring):
        opened_here = True
        hdf5_file = tb.openFile(hdf5_file, 'a')

    h5r = hdf5_file.root

    # Grab reactor list if not specified
    if rx_list == None:
        rx_id_map = get_reactor_id_map(hdf5_file)
        rx_list = sorted(rx_id_map.values())

    # Make new used fuel tables
    for rx in rx_list:
        rx_group = getattr(h5r, rx)

        # Determine slice for this reactor
        if len(slice) == 1:
            rx_slice = [slice[0], -1, 1]
        elif len(slice) == 2:
            rx_slice = [slice[0], slice[1], 1]
        elif len(slice) == 3:
            rx_slice = [slice[0], slice[1], slice[2]]

        if rx_slice[1] < 0:
            rx_slice[1] = len(rx_group.fresh_fuel_info) + rx_slice[1]

        for n in xrange(*rx_slice):
            print n

    # Close the HDF5 file
    if opened_here:
        hdf5_file.close()



if __name__ == "__main__":
    make_used_fuel_tables("test.h5")
