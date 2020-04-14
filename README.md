# STALTA_tuner
Interactive configuration for STA/LTA algorithms. Applied to seismology. Based on codes in [ObsPy](https://docs.obspy.org/tutorial/code_snippets/trigger_tutorial.html).

STA/LTA settings can have a major affect on the results from automatic event detection across a network. This program allows you to interactively adjust different STA/LTA parameters to improve your network processing. There are no right answers for tuning your STA/LTA algorithm. Keep adjusting until you find something that represents your data well.

This program allows you to load seismic data and adjust common STA/LTA parameters to see how it will affect triggering on your data.

Check out the [Wiki](https://github.com/jwellik/STALTA_tuner/wiki) for more details :-)

## Installation
Download the [zip file](https://github.com/jwellik/STALTA_tuner/archive/master.zip) or use `git` to clone the entire repository to your working directory (e.g., `/Users/jaywellik/PYTHON/stalta_tuner/`). All scripts will be run from this directory.

STALTA_tuner runs on Python 3.7. The program is interactive and will run in your default browser. It is powered by the [Bokeh server](https://docs.bokeh.org/en/latest/docs/user_guide/server.html) service. All dependencies can be easily installed via [Anaconda](https://www.continuum.io/) on the command line. I *highly* recommend using a virtual environment in order to guarantee that STALTA_tuner runs properly. Follow the directions below to install STALTA_tuner with a pre-defined virtual environment.

First, change directories to /stalta_tuner. You can create the virtual environment with the provided yml file, or you can create the environment manually.

To create the environment from a yml file, do the following steps:
```
$ conda config --add channels conda-forge
$ conda env create --file stalta37.yml
```

To create the environment manually, do this:
```
$ conda config --add channels conda-forge
$ conda env create --name stalta37
$ conda activate stalta37
$ conda install numpy
$ conda install scipy
$ conda install obspy
$ conda install matplotlib
$ conda install pandas
$ conda install bokeh
```

## Usage

First, activate the virtual environment
```
$ conda activate stalta37
```

Now, run the shell script to execute the code. Specify the configuration file without the extension. E.g.,
```
$ ./run.sh MSH_lite
```

The interactive tuner will open in your default browser. Change the STA/LTA algorithm, STA window, LTA window, and trigger thresholds to tune your STA/LTA settings. You can also change the timestamp to study. Only 30' are displayed at a time.

## Configuration file

Configuration files exist in ./configs. They are simple. Look at ./configs/MSH.py as an example. Set the server, stations (nslc), and the number of stations required to exceed the STA/LTA threshold to produce a trigger. Note, when you call the configuration file when running the program, do *not* include the extension, '.py'. See 'Usage'.

Check out the [Wiki](https://github.com/jwellik/STALTA_tuner/wiki) for more details.
