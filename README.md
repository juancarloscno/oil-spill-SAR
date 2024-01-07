# Oil Spill Detection Project with Sentinel-1 SAR

This project aimed to develop an algorithm to segment oil spills in the ocean using Synthetic Radar Aperture (SAR) technology. I developed this project as part of my thesis project as an environmental engineer at the University of Guayaquil.

## Project Structure
------------
```
├── data
│   ├── proccesed       <- This folder contains the proccesed data, ready to analye and create plots
│   ├── unproccesed     <- This folder contains the raw data, grouped by source (e.g. ./mklab)
├── notebooks           <- Jupyter notebooks. Naming convention is a number (for ordering) and a short '-' delimited desripcion, e.g. '1.0-inspect_oil_dataset.ipynb'
├── figures             <- Temporary folder to save figures created in jupyter notebooks
├── scripts
├── ├── dataset         <- Script to download datasets used in the project
├── ├── docker          <- Script to build and run docker containers
├── ├── enroot          <- Script to build and run enroot containers
├── ├── snap            <- Script to build the source code of Sentinel Application Platform. This script can be used in docker or enroot containers.
├── src
│   ├── features
│   ├── mapping
│   ├── models
│   ├── plotting
│   ├── utils           <- Utilitary scripts. See inside for more information.
├── ...
