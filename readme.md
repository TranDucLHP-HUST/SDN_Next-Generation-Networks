#This project is a controller of SDN (Software-define network) with opendaylight and mininet
##Setup:
- virtual box 
- Opendaylight 0.4.2 
- Mininet 
- python 3
##File 
- config.py: file save the config of controller 
- put_data: create a request add flow and put it 
- main.py: user interface 
- delete_flow.py: delete flow cache in controller 
- setup.txt: the packages which need to installed
##Run 
- First, install packages: pip install -r setup.txt 
- Edit file config.py for your config  
- Run file main.py to open the user interface
- run file delete_flow.py before you create a new topology in mininet 