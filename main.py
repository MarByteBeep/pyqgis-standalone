from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtWidgets import *

import processing
from qgis.analysis import QgsNativeAlgorithms
from processing.core.Processing import Processing

class MapViewer(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self, None)
		self._canvas = QgsMapCanvas()
		self._root = QgsProject.instance().layerTreeRoot()

		self.bridge = QgsLayerTreeMapCanvasBridge(self._root, self._canvas)
		self.model = QgsLayerTreeModel(self._root)
		self.model.setFlag(0x25043)
		self.model.setFlag(QgsLayerTreeModel.ShowLegend)
		self.layer_treeview = QgsLayerTreeView()
		self.layer_treeview.setModel(self.model)

		self.layer_tree_dock = QDockWidget("Layers")
		self.layer_tree_dock.setObjectName("layers")
		self.layer_tree_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
		self.layer_tree_dock.setWidget(self.layer_treeview)

		self.splitter = QSplitter()
		self.splitter.addWidget(self.layer_tree_dock)
		self.splitter.addWidget(self._canvas)
		self.splitter.setCollapsible(0, False)
		self.splitter.setStretchFactor(1, 1)

		self.layout = QHBoxLayout()
		self.layout.addWidget(self.splitter)
		self.contents = QWidget()
		self.contents.setLayout(self.layout)
		self.setCentralWidget(self.contents)

		self.load_layers()

	def load_layers(self):
		source_path = "path/to/data/source"
			# layer = QgsVectorLayer(source_path, 'Layer1', 'ogr')
			# QgsProject.instance().addMapLayer(layer)
		urlWithParams = "type=xyz&url=https://02e31dc0-tiles.spatialbuzz.net/tiles/fr_ca-v041/styles/fr_ca_v041_ext_lte/{z}/{x}/{y}.png"
		layer = QgsRasterLayer(urlWithParams, 'freedom', 'wms')
		QgsProject.instance().addMapLayer(layer)
		self._canvas.setExtent(layer.extent())
		self._canvas.setLayers([layer])

			### PROCESSING
		#result = processing.run("native:buffer", {'INPUT': layer, 'DISTANCE': 10, 'OUTPUT': 'memory:'})
		#params = {'INPUT': layer,'OUTPUT': '/Downloads/new_gpkg.gpkg','LAYER_NAME': 'new_layer_name'}
		#result = processing.run("native:savefeatures", params)
		#result = processing.run("native:buffer", {'INPUT': source_path, 'DISTANCE': 10, 'OUTPUT': 'memory:'})
		QgsProject.instance().addMapLayer(result["OUTPUT"])
    ########################

qgs = QgsApplication([], True)
qgs.initQgis()

Processing.initialize()
#QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

main_window = MapViewer()
main_window.show()

qgs.exec_()
qgs.exitQgis()