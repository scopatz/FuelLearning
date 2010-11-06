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


---------------
Fresh Fuel Info
---------------
The fresh fuel info tables specify the intial loading parameters of each assembly for each reactor.  These are 
used to perform burnup and storage calculations.

1.  **assembly_id**:  A unique identfier for each fuel assembly.
2.  **mass**: The mass of the initial core loading in kg of Uranium.
3.  **enrichment**: The initial enrichment of U-235 in the fresh fuel as a mass fraction.
4.  **burnup**: The reported discharge burnup of the assembly in MWd/kgIHM.
5.  **assembly_type**: The assembly type flag.
6.  **assembly_status**: The status code for each assembly.  A blank in this field represents standard fuel, 
    while a code represents failed or nonstandard fuel.
7.  **storage_id**: The pool storage ID or dry storage ID where the assembly is stored.
8.  **discharge_cycle**: The discharge cycle number.
9.  **discharge_date**: The final dischage date of the assmbley, related to discharge_cycle.


---------
Used Fuel
---------
This table describes the fuel assembly after it has been burned in the reactor.

1.  **assembly_id**:  A unique identfier for each fuel assembly.  This matches the id in the fresh fuel info table.
2.  **burnup**: The calculated discharge burnup of the assembly in MWd/kgIHM.
3.  **mass**: The mass of the following used fuel vector in kgUF/kgIHM.  Represents the sum of all following columns.
4.  **isotopics**:  All following isotopic fields represent the mass fraction of this isotope in the spent fuel.
    Therefore these feilds have units of kg{Isotope}/kgIHM.
