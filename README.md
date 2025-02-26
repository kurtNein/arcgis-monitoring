# Project Title

This project is an interface for automating common needs when managing an ArcGIS organization.

The program, when entered through ```app.py```, serves a web-browser application with a simple GUI.

## Description

This project addresses a need to save backups of the same groups of ArcGIS hosted layers and Enterprise feature classes.
It has been expanded to include checking schema locks in Enterprise data, hosted domains for service interruptions, and checking for inactive users and feature layers.

The project comprises a Flask (Python) WSGI backend to receive requests, and a JavaScript/HTML/CSS frontend to make requests.

All calls to make changes within ArcGIS environments are accomplished in Python using the ```arcpy``` and ```arcgis``` Python packages.

## Getting Started

Clone or download this repository to the machine from which you will run these tools.
If you intend to make use of connecting to an Enterprise Geodatabase, create a Database Connection File (```.sde```) for this application to access.
You will need to provide the path to the file (absolute or relative to ```app.py```) in the ```creds.json``` file.
An ```.sde``` file is not required if you only intend to use ArcGIS Online tools.

### Dependencies

* arcpy environment (clone arcgispro-py3 from in-app ArcGIS Pro settings)
* Python 3.11 within the arcgispro-py3 environment as the interpreter for this program

### Configuration

* In ```app.py```, inside ```if __name__ == '__main__():```, configure the arguments of ```app.run()``` according to the documentation of the Flask.run() class method.
* Edit values in ```creds_sample.json``` to your credentials for your implementation, then rename the file to ```creds.json```.

### Executing program

* Run ```app.py``` with the arcgispro-py3 Python interpreter.
* Using a web browser, navigate to your domain and port as determined in your ```app.run()``` arguments.

* Alternatively, pick and choose which class methods to call under the ```if __name__ == '__main__():``` block in ```utils.py```.
```
if __name__ == '__main__():
    am = AutoMod()
    am.backup_agol()
```
* You could then schedule ```utils.py``` to run using whatever task scheduling tools available in your infrastructure.

## Authors

Kurt Neinstedt

## Acknowledgments

Inspiration and code snippets
* [joshsharpheward](https://github.com/joshsharpheward/gis-administration)
