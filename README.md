# carla-V2X-dataset-generator
Create dataset from carla with an infrastructure and vehicles transiting. 

## Requirements
To run the scripts, it is required to have CARLA (version 0.9.12 or higher) running either on your local machine or on a server. 
Running CARLA on Linux requires a workarround to indicate the GPU to use : `./CarlaUE4.sh -prefernvidia` .

### Package required
Scripts are written and tested with python 3.8. Pip version 20.3 or higher is required. 

To check pip version :
`pip3 -V`

To update the pip version:
`pip3 install --upgrade pip`

The list of package used:

- [ ] carla
- [ ] tqdm
- [ ] numpy

## Scripts 
Script to run...