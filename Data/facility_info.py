import csv
import tables as tb
import metasci as ms
import time

time_format = "%m/%d/%y %H:%M:%S"

def get_type_map(map_file):
    with open(map_file, 'r') as f:
        type_map = dict([line.split()[:2] for line in f])
    return type_map

def get_reactor_id_map(hdf5_file):
    # Open the HDF5 file
    opened_here = False
    if isinstance(hdf5_file, basestring):
        opened_here = True
        hdf5_file = tb.openFile(hdf5_file, 'r')

    rx_id = dict([ (row['reactor_id'], row['name']) for row in hdf5_file.root.facility_info ])

    # Close the HDF5 file
    if opened_here:
        hdf5_file.close()

    return rx_id
    

class FacilityInfo(tb.IsDescription):
    name         = tb.StringCol(itemsize=25, pos=0)
    full_name    = tb.StringCol(itemsize=25, pos=1)
    reactor_id   = tb.UInt16Col(pos=2)
    reactor_type = tb.StringCol(itemsize=3,  pos=3)
    utility_name = tb.StringCol(itemsize=50, pos=4)
    lic_exp_date = tb.Time64Col(pos=5)
    pos_exp_date = tb.Time64Col(pos=6)
    address      = tb.StringCol(itemsize=100, pos=7)
    city         = tb.StringCol(itemsize=20,  pos=8)
    state        = tb.StringCol(itemsize=2,   pos=9)
    zip          = tb.StringCol(itemsize=10,  pos=10)


def facility_info(hdf5_file, csv_file="raw/tblFacility.csv", map_file="raw/facility_type_map.txt"):
    # Get a mapping between reactor id and PWR/BWR
    rx_type = get_type_map(map_file)

    # Open the HDF5 file
    opened_here = False
    if isinstance(hdf5_file, basestring):
        opened_here = True
        hdf5_file = tb.openFile(hdf5_file, 'a')

    # Clean and Init the new facility info table
    h5r = hdf5_file.root
    if hasattr(h5r, "facility_info"):
        hdf5_file.removeNode(h5r, "facility_info")
    fac_table = hdf5_file.createTable(h5r, "facility_info", FacilityInfo)

    # Read in the facility information and write it to the HDF5 file
    fac_file = csv.reader(open(csv_file, 'rb'))
    row = fac_table.row

    for ffrow in fac_file:
        row['name'] = ms.natural_naming(ffrow[1])
        row['full_name'] = ffrow[1]

        row['reactor_id'] = int(ffrow[0])
        row['reactor_type'] = rx_type[ffrow[0]]
        row['utility_name'] = ffrow[2]

        try:
            led = time.mktime( time.strptime(ffrow[3], time_format) )
        except ValueError:
            led = 0.0
        row['lic_exp_date'] = led

        try:
            ped = time.mktime( time.strptime(ffrow[4], time_format) )
        except ValueError:
            ped = 0.0
        row['pos_exp_date'] = ped

        row['address'] = ffrow[5]
        row['city'] = ffrow[6]
        row['state'] = ffrow[7]
        row['zip'] = ffrow[8]

        row.append()
    
    fac_table.flush()

    # Close the HDF5 file
    if opened_here:
        hdf5_file.close()

if __name__ == "__main__":
    #print get_type_map("raw/facility_type_map.txt")
    #facility_info("test.h5")
    print get_reactor_id_map("test.h5")
