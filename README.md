<img src="https://raw.githubusercontent.com/jwellik/STALTA_tuner/master/lib/staltatuner.png" width=638 alt="REDPy Logo" />

# STALTA_tuner
Interactive configuration for STA/LTA algorithms. Applied to seismology.

## Installation
Download the [zip file](https://github.com/jwellik/STALTA_tuner/archive/master.zip) or use `git` to clone the entire repository to a working directory (e.g., mine is `/Users/jaywellik/PYTHON/stalta_tuner/`). All scripts will be run from this directory, and all new files will be generated here.

STALTA_tuner runs on Python 3.7. The program is interactive and will run in your default browser. It is powered by the Bokeh server service. All dependencies can be easily installed via [Anaconda](https://www.continuum.io/) on the command line. I *highly* recommend using a virtual environment in order to guarantee that STALTA_tuner runs properly. Follow the directions below to install STALTA_tuner with a pre-defined virtual environment.

First, change directories to /stalta_tuner

Then create the virtual environment
```
>> conda config --add channels condo-forge
>> conda env create --file stalta37.yml
```

## Usage

First, activate the virtual environment
```
>> condo activate stalta37
```

Now, run the shell script to execute the code
```
>>./run.sh MSH_lite
```

The interactive tuner will open in your default browser. Change the STA/LTA algorithm, STA window, LTA window, and trigger thresholds to tune your STA/LTA settings. You can also change the timestamp to study. Only 30' are displayed at a time.

## Configuration file

Configuration files exist in ./configs. They are simple. Look at ./configs/MSH.py as an example. Set the server, stations (nslc), and the number of stations required to exceed the STA/LTA threshold to produce a trigger. Note, when you call the configuration file when running the program, do *not* include the extension, '.py'. See 'Usage'.
