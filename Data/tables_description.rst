=====================
Description of Tables
=====================

Here we describe the coulumns in the various tables and list their units.


-------------
Facility Info
-------------

This table gives information on the each of the facilities present.  Here are what the columns mean:

1.  **name**: Natural name of the facility that may be read nicley by a computer
2.  **full_name**: Actual name of the facility, human-readable.
3.  **reactor_id**: An integer that uniquely identifies the reactor.
4.  **reactor_type**: Flag that specifies whether the reactor is a PWR or BWR.
5.  **utility_name**: The name of the utility that owns this facility. 
6.  **lic_exp_date**: The date when the recator operating license for this facility expires.  
    The date is expressed in seconds since epoch (1970).
7.  **pos_exp_date**: The date when the possession-only license expiration date for permanently shutdown 
    reactors expires. The date is expressed in seconds since epoch (1970).
8.  **address**: Contact street address.
9.  **city**: Contact city.
10. **state**: Contact state.
11. **zip**: Contact zip code.

