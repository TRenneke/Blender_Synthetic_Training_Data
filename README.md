# Blender_Synthetic_Training_Data
Tools to generate synthetic trainings data with Blender

This toolchain is currently in an experimental phase. Be weary!
There will be compatibility breaking changes in the Future!

# Usage
## Dataset Generation
* In blender copy the dataset_generation dir to your blender addon dir.
* Enable the addon
* Under Scene click on "Load Randomisation file" and select the "example_randomisation.yaml"
* Under Output -> Output set the output path to your desired dataset image dir
* Click on "Setup Compositing" to setup compositing and enable crypto_matte rendering
* Add some Cubes to your scene name them Cube.xxx
* Click on Create Dataset
## Dataset Conversion

* python3 .\dataset_conversion\generate_tight_bbs.py --dataset .\datasets\example\
* to convert your dataset
* python3 .\datasets\viewDataset.py --dataset .\datasets\example\
* to view your dataset


