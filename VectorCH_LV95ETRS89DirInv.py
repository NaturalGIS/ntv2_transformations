# -*- coding: utf-8 -*-

"""
***************************************************************************
    VectorCH_LV95ETRS89DirInv.py
    ---------------------
    Date                 : March 2015
    Copyright            : (C) 2015 by Giovanni Manghi
    Email                : giovanni dot manghi at naturalgis dot pt
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Giovanni Manghi'
__date__ = 'March 2015'
__copyright__ = '(C) 2015, Giovanni Manghi'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
from urllib.request import urlretrieve

from qgis.PyQt.QtGui import QIcon

from qgis.core import (QgsProcessingException,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterVectorDestination
                      )

from processing.algs.gdal.GdalAlgorithm import GdalAlgorithm
from processing.algs.gdal.GdalUtils import GdalUtils

pluginPath = os.path.dirname(__file__)


class VectorCH_LV95ETRS89DirInv(GdalAlgorithm):

    INPUT = 'INPUT'
    TRANSF = 'TRANSF'
    CRS = 'CRS'
    GRID = 'GRID'
    OUTPUT = 'OUTPUT'

    def __init__(self):
        super().__init__()

    def name(self):
        return 'chvectortransform'

    def displayName(self):
        return '[CH] Direct and inverse Vector Tranformation'

    def group(self):
        return '[CH] Switzerland'

    def groupId(self):
        return 'switzerland'

    def tags(self):
        return 'vector,grid,ntv2,direct,inverse,switzerland'.split(',')

    def shortHelpString(self):
        return 'Direct and inverse vector tranformations using Switzerland NTv2 grids.'

    def icon(self):
        return QIcon(os.path.join(pluginPath, 'icons', 'ch.png'))

    def initAlgorithm(self, config=None):
        self.directions = ['Direct: CH1903/LV03 [EPSG:21781] -> New Data',
                           'Inverse: New Data -> CH1903/LV03 [EPSG:21781]'
                          ]

        self.datums = ['ETRS89 [EPSG:4258]',
                       'CH1903+ [EPSG:2056]'
                      ]

        self.grids = ['CHENyx06']

        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT,
                                                              'Input vector'))
        self.addParameter(QgsProcessingParameterEnum(self.TRANSF,
                                                     'Transformation',
                                                     options=self.directions,
                                                     defaultValue=0))
        self.addParameter(QgsProcessingParameterEnum(self.CRS,
                                                     'New Datum',
                                                     options=[i[0] for i in self.datums],
                                                     defaultValue=0))
        self.addParameter(QgsProcessingParameterEnum(self.GRID,
                                                     'NTv2 Grid',
                                                     options=self.grids,
                                                     defaultValue=0))
        self.addParameter(QgsProcessingParameterVectorDestination(self.OUTPUT,
                                                                  'Output'))

    def getConsoleCommands(self, parameters, context, feedback, executing=True):
        ogrLayer, layerName = self.getOgrCompatibleSource(self.INPUT, parameters, context, feedback, executing)
        outFile = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        self.setOutputValue(self.OUTPUT, outFile)

        output, outputFormat = GdalUtils.ogrConnectionStringAndFormat(outFile, context)
        if outputFormat in ('SQLite', 'GPKG') and os.path.isfile(output):
            raise QgsProcessingException('Output file "{}" already exists.'.format(output))

        direction = self.parameterAsEnum(parameters, self.TRANSF, context)
        crs = self.parameterAsEnum(parameters, self.CRS, context)
        grid = self.parameterAsEnum(parameters, self.GRID, context)

        arguments = []

        if direction == 0:
            # Direct transformation
            arguments.append('-t_srs')
            if crs == 0:
               arguments.append('EPSG:4258')
               gridFile = os.path.join(pluginPath, 'grids', 'chenyx06etrs.gsb')
               arguments.append('-s_srs')
               arguments.append('+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=600000 +y_0=200000 +ellps=bessel +nadgrids={} +wktext +units=m +no_defs'.format(gridFile))
               arguments.append('-f {}'.format(outputFormat))
               arguments.append('-lco')
               arguments.append('ENCODING=UTF-8')

               arguments.append(output)
               arguments.append(ogrLayer)
               arguments.append(layerName)
            else:
               arguments.append('+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=2600000 +y_0=1200000 +ellps=bessel +nadgrids=@null +wktext +units=m')
               gridFile = os.path.join(pluginPath, 'grids', 'CHENYX06a.gsb')
               arguments.append('-s_srs')
               arguments.append('+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=600000 +y_0=200000 +ellps=bessel +nadgrids={} +wktext +units=m +no_defs'.format(gridFile))
               arguments.append('-f')
               arguments.append('Geojson')
               arguments.append('/vsistdout/')
               arguments.append(ogrLayer)
               arguments.append(layerName)
               arguments.append('-lco')
               arguments.append('ENCODING=UTF-8')
               arguments.append('|')
               arguments.append('ogr2ogr')
               arguments.append('-f {}'.format(outputFormat))
               arguments.append('-a_srs')
               arguments.append('EPSG:2056')
               arguments.append(output)
               arguments.append('/vsistdin/')
        else:
            # Inverse transformation
            arguments = ['-s_srs']
            if crs == 0:
                arguments.append('EPSG:4258')
                gridFile = os.path.join(pluginPath, 'grids', 'chenyx06etrs.gsb')
                arguments.append('-t_srs')
                arguments.append('+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=600000 +y_0=200000 +ellps=bessel +nadgrids={} +wktext +units=m +no_defs'.format(gridFile))
                arguments.append('-f')
                arguments.append('Geojson')
                arguments.append('/vsistdout/')
                arguments.append(ogrLayer)
                arguments.append(layerName)
                arguments.append('-lco')
                arguments.append('ENCODING=UTF-8')
                arguments.append('|')
                arguments.append('ogr2ogr')
                arguments.append('-f {}'.format(outputFormat))
                arguments.append('-a_srs')
                arguments.append('EPSG:21781')
                arguments.append(output)
                arguments.append('/vsistdin/')
            else:
                gridFile = os.path.join(pluginPath, 'grids', 'CHENYX06a.gsb')
                arguments.append('+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=2600000 +y_0=1200000 +ellps=bessel +nadgrids=@null +wktext +units=m')
                arguments.append('-t_srs')
                arguments.append('+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=600000 +y_0=200000 +ellps=bessel +nadgrids={} +wktext +units=m +no_defs'.format(gridFile))
                arguments.append('-f')
                arguments.append('Geojson')
                arguments.append('/vsistdout/')
                arguments.append(ogrLayer)
                arguments.append(layerName)
                arguments.append('-lco')
                arguments.append('ENCODING=UTF-8')
                arguments.append('|')
                arguments.append('ogr2ogr')
                arguments.append('-f {}'.format(outputFormat))
                arguments.append('-a_srs')
                arguments.append('EPSG:21781')
                arguments.append(output)
                arguments.append('/vsistdin/')

        if not os.path.isfile(os.path.join(pluginPath, 'grids', 'CHENYX06a.gsb')):
            urlretrieve('http://www.naturalgis.pt/downloads/ntv2grids/ch/CHENYX06a.gsb', os.path.join(pluginPath, 'grids', 'CHENYX06a.gsb'))
            urlretrieve('http://www.naturalgis.pt/downloads/ntv2grids/ch/chenyx06etrs.gsb', os.path.join(pluginPath, 'grids', 'chenyx06etrs.gsb'))

        return ['ogr2ogr', GdalUtils.escapeAndJoin(arguments)]
