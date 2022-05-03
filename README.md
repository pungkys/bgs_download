# bgs_download
Download data from BGS FTP, create event catalogue, and pre-process earthquake signal

1. bgs_catalogue 
Creating event catalogue from nordic files provided by BGS ftp 

Input:
- nordic file 
ftp://seiswav.bgs.ac.uk/events
- station information
Stn-info.txt, stn-info-add_v2.csv

Output:
- event data catalogue 
Ex: data_example/Catalog_v2.csv

To run execute "run_create_catalogue.py", other important modules:

a. read_from_nordic.py : code to read nordic file 
b. search_station_info.py : code to read and take station information 
c. store.py : code to store all information to dataframe

2. bgs_download
Downloading continuous seismic traces according to the event catalogue and store it to local computer

3. bgs_processing
Pre-processing earthquake signals 
- cut signal into desirable segments
- plotting traces and seismic windows
- reading arrival times from event catalogue, or calculate arrival times based on taupe
- calculate peak ground acceleration, peak ground velocity, maximum magnitude of wood-anderson
- spectra calculation of signal and noise
- signal-to-noise ratio calculation

Example of processing pipelines available in the Trial1.ipynb
Input: 
- station inventory 
- earthquake catalogue
- continuous traces
