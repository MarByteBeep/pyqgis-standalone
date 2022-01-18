# PyQGIS Standalone Script Executer

Standalone PyQGIS application that is able to run a custom script, in this case `Proximity.py` without the need of a GUI. Also we don't need to set all kinds of environment variables using a batch file: just launch the VS Code project, and off you go. This was created for Windows.

# Installation

First get `OSGeo4W LTR` by running `install/qgis_deploy_install_upgrade_ltr.ps1` from PowerShell console with administrative rights. Ensure to fetch QGIS LTR. This script will automatically download and install `OSGeo4W`. You can obviously do this manually as well. Just ensure you get QGIS LTR and the _full_ installation. Also ensure to install everything in `C:/OSGeo4W`. If not, change the paths in `.env` and `.settings.json`, see below.

## Access Rights

If the script is failing because of accessrights, you need to temporarily bypass the ExecutionPolicy

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

# Verify `.env`

Open up `.env` in the root folder and verify that following settings match your installation:

```
OSGEO4W_ROOT=C:/OSGeo4W
QGIS_CONFIG=qgis-ltr
PYTHON_VERSION=Python39
```

# Verify `settings.json`

Open up `.vscode/settings.json` and verify that the path in `python.defaultInterpreterPath` exists. If it doesn't, update it to match your configuration. You probably need to update `PYTHON_VERSION` in `.env` as well.

# Run example

I've included an example geometry in the `test` folder: it contains a number of airports in the netherlands. From VS Code select the `Launch` configuration and hit `F5`. It'll execute `main.py`, which in turn executes the `Proximity.py` script on that test geometry and outputs a rasterized tif.

This should be enough to get you going. Enjoy!

# Credits

This is based on work by @isogeo: https://github.com/isogeo/isogeo-plugin-qgis/blob/master/.vscode/settings.json as well as various posts on the QGIS stackexchange forum and in particular Kadir Şahbaz: https://gis.stackexchange.com/questions/421329/pyqgis-outside-gui-module-qgis-processing-has-no-attribute-run

# Wishful thinking

It would be great if the QGIS team at one point in the future, would integrate all this in their API/SDK to make this whole process seamless :)
