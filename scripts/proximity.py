from qgis.PyQt.QtCore import (QCoreApplication, QVariant)
from qgis.core import (QgsProcessing,
                       QgsMessageLog,
                       QgsFields,
                       QgsWkbTypes,
                       QgsFeatureSink,
                       QgsGeometry,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsProject,
                       QgsProcessingAlgorithm,
                       QgsProcessingException,
                       QgsField,
                       QgsProcessingUtils,
                       QgsProcessingParameterDistance,
                       QgsVectorLayer,
                       QgsFeature,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterDestination)
import processing

class Proximity(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    DISTANCE = 'DISTANCE'
    SEGMENTS = 'SEGMENTS'
    ITERATIONS = 'ITERATIONS'
    RESOLUTION = 'RESOLUTION'

    END_CAP_STYLE = QgsGeometry.CapRound
    JOIN_STYLE = QgsGeometry.JoinStyleRound
    MITER_LIMIT = 2.0

    """
    This is an example algorithm that takes a vector layer,
    creates some new layers and returns some results.
    """

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        # Must return a new copy of your algorithm.
        return Proximity()

    def name(self):
        """
        Returns the unique algorithm name.
        """
        return 'proximity'

    def displayName(self):
        """
        Returns the translated algorithm name.
        """
        return self.tr('Create Proximity layer')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to.
        """
        return self.tr('scripts')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs
        to.
        """
        return 'scripts'

    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return self.tr('Creates a rasterized proximity layer, containing distance information (in meters) to the processed features.')

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input polygon layer'),
                types=[QgsProcessing.TypeVectorPolygon]
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.DISTANCE,
                self.tr('Buffer Distance (meters)'),
                type=QgsProcessingParameterNumber.Integer,
                minValue=5,
                maxValue=200000,
                defaultValue=5000,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.SEGMENTS,
                self.tr('Segments'),
                type=QgsProcessingParameterNumber.Integer,
                minValue=5,
                maxValue=50,
                defaultValue=20
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.ITERATIONS,
                self.tr('Iterations'),
                type=QgsProcessingParameterNumber.Integer,
                minValue=5,
                maxValue=50,
                defaultValue=20
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.RESOLUTION,
                self.tr('Rasterize render resolution (in degrees)'),
                type=QgsProcessingParameterNumber.Double,
                minValue=0.000001,
                defaultValue=0.0001
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                self.tr('Rasterized proximity layer')
            )
        )

    def prepareAlgorithm(self, parameters, context, feedback):
        self.distance = self.parameterAsDouble(
            parameters,
            self.DISTANCE,
            context)
        self.iterations = self.parameterAsInt(
            parameters,
            self.ITERATIONS,
            context)
        self.segments = self.parameterAsInt(
            parameters,
            self.SEGMENTS,
            context)
        self.resolution = self.parameterAsDouble(
            parameters,
            self.RESOLUTION,
            context)
        self.source = self.parameterAsSource(parameters,
                                        self.INPUT,
                                        context)
        self.source_crs = self.source.sourceCrs()
        if not self.source_crs.isGeographic():
            feedback.reportError('Layer CRS must be a Geograhpic CRS for this algorithm')
            return False
        return super().prepareAlgorithm(parameters, context, feedback)

    def processFeature(self, feature, distance):
        # Call QgsGeometry copy constructor explicity to force deep copy
        geometry = QgsGeometry(feature.geometry())

        # For point features, centroid() returns the point itself
        centroid = geometry.centroid()
        x = centroid.asPoint().x()
        y = centroid.asPoint().y()
        proj_string = 'PROJ4:+proj=aeqd +ellps=WGS84 +lat_0={} +lon_0={} +x_0=0 +y_0=0'.format(y, x)
        dest_crs = QgsCoordinateReferenceSystem(proj_string)
        xform = QgsCoordinateTransform(self.source_crs, dest_crs, QgsProject.instance())
        geometry.transform(xform)
        buffer = geometry.buffer(distance, self.segments, self.END_CAP_STYLE, self.JOIN_STYLE, self.MITER_LIMIT)
        buffer.transform(xform, QgsCoordinateTransform.ReverseTransform)

        # Be sure to leave the original feature untouched
        newFeature = QgsFeature(self.fields)
        newFeature.setGeometry(buffer)
        newFeature['BURN'] = distance

        return newFeature

    def processAlgorithm(self, parameters, context, feedback):
        numfeatures = self.source.featureCount()

        self.fields = QgsFields()
        self.fields.append(QgsField('BURN', QVariant.Int))

        # Create in-memory feature sink, and not through self.parameterAsSink
        # because we don't need the resulting output
        (sink, dest_id) = QgsProcessingUtils.createFeatureSink(
            'memory:',
            context,
            self.fields,
            self.source.wkbType(),
            self.source.sourceCrs()
        )

        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, 'memory'))

        total = 100.0 / numfeatures if numfeatures else 0

        distancePerIterarion = self.distance / self.iterations
        distance = self.distance

        done = False
        iteration = 0
        feedback.setProgress(0)
        while (distance > 0.0 and done == False):
            features = self.source.getFeatures()
            for current, feature in enumerate(features):
                # Stop the algorithm if cancel button has been clicked
                if feedback.isCanceled():
                    done = True
                    break

                # Add a feature in the sink
                sink.addFeature(self.processFeature(feature, distance), QgsFeatureSink.FastInsert)

            distance = distance - distancePerIterarion
            iteration = iteration + 1
            feedback.setProgress(int((iteration / self.iterations) * 100))

        # Copy to features for distance is 0
        features = self.source.getFeatures()
        for current, feature in enumerate(features):
            sink.addFeature(self.processFeature(feature, 0), QgsFeatureSink.FastInsert)

        # Rasterize
        layer = QgsProcessingUtils.mapLayerFromString(dest_id, context)
        extent = layer.extent();
        xmin = extent.xMinimum()
        xmax = extent.xMaximum()
        ymin = extent.yMinimum()
        ymax = extent.yMaximum()

        raster = processing.run(
            "gdal:rasterize",
            {
                "INPUT":layer,
                "FIELD":"BURN",
                "UNITS":1,
                "NODATA":-1,
                "WIDTH":self.resolution,
                "HEIGHT":self.resolution,
                "EXTENT": "%f,%f,%f,%f"% (xmin, xmax, ymin, ymax),
                "OUTPUT": parameters[self.OUTPUT]
            },
            is_child_algorithm=True,
            context=context,
            feedback=feedback
        )

        # Return the results
        return {self.OUTPUT: raster[self.OUTPUT]}