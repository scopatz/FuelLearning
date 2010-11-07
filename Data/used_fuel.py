import os
import sys
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
    'discharge_k': tb.Float64Col(pos=1),
    'mass':        tb.Float64Col(pos=2),
    }

nbuf = len(UsedFuel)
i2t = bp.isos2track()

for i in xrange(len(i2t)):
    UsedFuel[bp.isoname.zzaaam_2_LLAAAM(i2t[i])] = tb.Float64Col(pos=nbuf + i)

# Init the LWR object, only need one!
lwrd = bp.LWRDefaults()
lwrd.batches = 1
lwr = bp.LightWaterReactor1G(lwr_data, lwrd, "LWR")

# Init the storage object, we only need one
stor = bp.Storage("Storage")
t_now = time.time()  # Use the same time 'now' value for all runs.

############################
### Fuel Cycle Functions ###
############################

# All of the fuel cycle function take the following inputs
#   * x: U-235 enrichment mass fraction
#   * BUt: target burnup in MWd / kgIHM
# and return the following
#   * BUd: discharge burnup in MWd / kgIHM
#   * mass: mass of output mass stream
#   * isovec: output isotopic mass stream multiplied by mass

# Optionally, we might also take a discharge time value 
#   * t: time that assembly was permenatly discharged from the reactor, sec from epoch

def fuel_cycle_only_burn(x, BUt, t=t_now):
    # Re-initialize the LWR 
    leu = bp.MassStream({922350: x, 922380: 1.0 - x}, 1.0, "LEU")
    lwr.TargetBU = BUt
    lwr.IsosIn = leu

    # Find the discharge fluence & isotopics
    # This is a subsititute for doCalc()
    lwr.foldMassWeights()
    fp = lwr.FluenceAtBU(BUt)
    lwr.fd = fp.f
    lwr.Fd = fp.F
    lwr.BUd = BUt
    lwr.k = lwr.batchAveK(BUt)
    lwr.calcOutIso()

    lwr_out = lwr.IsosOut

    return lwr.k, lwr_out.mass, lwr_out.multByMass()

def fuel_cycle_burn_and_store(x, BUt, t=t_now):
    # Re-initialize the LWR 
    leu = bp.MassStream({922350: x, 922380: 1.0 - x}, 1.0, "LEU")
    lwr.TargetBU = BUt
    lwr.IsosIn = leu

    # Find the discharge fluence & isotopics
    # This is a subsititute for doCalc()
    lwr.foldMassWeights()
    fp = lwr.FluenceAtBU(BUt)
    lwr.fd = fp.f
    lwr.Fd = fp.F
    lwr.BUd = BUt
    lwr.k = lwr.batchAveK(BUt)
    lwr.calcOutIso()

    lwr_out = lwr.IsosOut

    # The time since discharge
    td = t_now - t

    # Storage / Decay calculation
    stor_out = stor.doCalc(lwr_out, td)

    return lwr.k, stor_out.mass, stor_out.multByMass()

fuel_cycles = {
    0: fuel_cycle_only_burn, 
    1: fuel_cycle_burn_and_store, 
    }

###########################
### HDF5 File functions ###
###########################

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

def calc_used_fuel_row(rx_group, n, fuel_cycle):
    # Calculate the mass stream given the fuel cycle and assembly info
    ffi_row = rx_group.fresh_fuel_info[n]
    k, mass, isovec = fuel_cycle(ffi_row['enrichment'], ffi_row['burnup'], ffi_row['discharge_date'])

    # Get used fuel row
    rx_uf_table = rx_group.used_fuel
    uf_row = rx_uf_table.row

    # Set row values
    uf_row['assembly_id'] = ffi_row['assembly_id']
    uf_row['discharge_k'] = k
    uf_row['mass'] = mass
    for i in xrange(len(i2t)):
        uf_row[bp.isoname.zzaaam_2_LLAAAM(i2t[i])] = isovec[i2t[i]]

    if n < len(rx_uf_table):
        for row in rx_uf_table.iterrows(n, n+1, 1):
            for colname in rx_uf_table.colnames:
                row[colname] = uf_row[colname]
            row.update()
    elif n == len(rx_uf_table):
        uf_row.append()
    else:
        temp_row = [''] + [-1.0]*(2+len(i2t))
        temp_rows = [temp_row] * (n - len(rx_uf_table))
        rx_uf_table.append(temp_rows)
        uf_row.append()        

    rx_uf_table.flush()

def calc_used_fuel_rows(hdf5_file, rx_list=None, slice=(0,-1, 1), fc_flag=0):
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
        rx_num = len(rx_group.fresh_fuel_info)

        sys.stdout.write(rx)
        sys.stdout.flush()

        # Determine slice for this reactor
        if len(slice) == 1:
            rx_slice = [slice[0], -1, 1]
        elif len(slice) == 2:
            rx_slice = [slice[0], slice[1], 1]
        elif len(slice) == 3:
            rx_slice = [slice[0], slice[1], slice[2]]

        if rx_slice[0] < 0:
            rx_slice[0] = len(rx_group.fresh_fuel_info) + rx_slice[0]

        if rx_slice[1] < 0:
            rx_slice[1] = len(rx_group.fresh_fuel_info) + rx_slice[1] + 1

        # Run the calculations for the specified rows!
        t1 = time.time()
        for n in xrange(*rx_slice):
            calc_used_fuel_row(rx_group, n, fuel_cycles[fc_flag])

            if n%100 == 0:
                t2 = time.time()
                sys.stdout.write( '\r{0}... n = {1}/{2}; rate = {3:.3f} n/s'.format(rx, n, rx_num, 100.0/(t2 - t1)) )
                sys.stdout.flush()
                t1 = t2

        t2 = time.time()
        sys.stdout.write( '\r{0}... n = {1}/{2}; rate = {3:.3f} n/s\n'.format(rx, n+1, rx_num, 100.0/(t2 - t1)) )
        sys.stdout.flush()

    # Close the HDF5 file
    if opened_here:
        hdf5_file.close()



if __name__ == "__main__":
    make_used_fuel_tables("test.h5")
