from qgis.core import *

qgs = QgsApplication([], False)
qgs.initQgis()

# import processing *after* initializing the application
import processing
from processing.core.Processing import Processing
Processing.initialize()

from scripts.proximity import Proximity

# I load the VectorLayer in code and pass it as an argument; obviously you could also just pass the
# file name to 'INPUT'. This is just a demonstration that you can have full control over the input
# layer before you send it off to the processing script

inLayer = QgsVectorLayer('test/nl_airports.osm|layername=multipolygons')
if not inLayer.isValid():
    raise Exception("Layer failed to load!")

# Create the Proximity algorithm
alg = Proximity()

# Set the params needed for this algorithm
params = {
	'INPUT': inLayer,
	'DISTANCE': 10000, # in meters
	'OUTPUT': 'test/rasterized.tif'
}

# Run the algorithm as you would from inside the QGIS GUI
alg.initAlgorithm()
ctx = QgsProcessingContext()
feedback = QgsProcessingFeedback()
alg.prepareAlgorithm(params, ctx, feedback)
alg.processAlgorithm(params, ctx, feedback)

# All done
print("Done")

qgs.exitQgis()
