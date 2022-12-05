from qgis.core import *
import sys
#sys.path.append("C://Program Files//QGIS 3.16//apps//qgis-ltr//python//plugins")
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

#inLayer = QgsVectorLayer('test/nl_airports.osm|layername=multipolygons')
urlWithParams = 'type=xyz&url=https://02e31dc0-tiles.spatialbuzz.net/tiles/fr_ca-v041/styles/fr_ca_v041_ext_lte/{z}/{x}/{y}.png'
inLayer = QgsRasterLayer(urlWithParams, 'freedom', 'wms')
if not inLayer.isValid():
    raise Exception("Layer failed to load!")

# Create the Proximity algorithm
#alg = Proximity()
source=inLayer
if source.isValid():
	provider = source.dataProvider()
fw = QgsRasterFileWriter()
fw.setOutputFormat('gpkg')
tableName = "freedom"
fw.setCreateOptions(["RASTER_TABLE=" + str(tableName), 'APPEND_SUBDATASET=YES'])
pipe = QgsRasterPipe()
if pipe.set(provider.clone()) is True:
	projector = QgsRasterProjector()
	projector.setCrs(provider.crs(), provider.crs())
	if pipe.insert(2, projector) is True:
		if fw.writeRaster(pipe, provider.xSize(), provider.ySize(), provider.extent(), provider.crs()) == 0:
			print("ok")
		else:
			print("error")
# Set the params needed for this algorithm
#params = {'INPUT': inLayer,'OUTPUT': '/Downloads/new_gpkg.gpkg','LAYER_NAME': 'new_layer_name'}
#result = processing.run("native:savefeatures", params)

# Run the algorithm as you would from inside the QGIS GUI
#alg.initAlgorithm()
#ctx = QgsProcessingContext()
#feedback = QgsProcessingFeedback()
#alg.prepareAlgorithm(params, ctx, feedback)

#alg.processAlgorithm(params, ctx, feedback)

# All done
print("Done")
#testing
#hello Fatemeh 
#qgs.exitQgis()
