# -*- coding: utf-8 -*-

"""
***************************************************************************
    RasterES_ED50ERTS89DirInv.py
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

import inspect
import os

from PyQt4.QtGui import QIcon

from processing.gui.Help2Html import getHtmlFromRstFile

try:
    from processing.parameters.ParameterRaster import ParameterRaster
    from processing.parameters.ParameterSelection import ParameterSelection
    from processing.outputs.OutputRaster import OutputRaster
except:
    from processing.core.parameters import ParameterRaster
    from processing.core.parameters import ParameterSelection
    from processing.core.outputs import OutputRaster

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.algs.gdal.GdalUtils import GdalUtils


class RasterES_ED50ERTS89DirInv(GeoAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    TRANSF = 'TRANSF'
    TRANSF_OPTIONS = ['Direct: Old Data -> ETRS89 [EPSG:4258]',
                      'Inverse: ETRS89 [EPSG:4258] -> Old Data']
    CRS = 'CRS'
    CRS_OPTIONS = ['ED50/UTM 29N [EPSG:23029]',
                   'ED50/UTM 30N [EPSG:23030]',
                   'ED50/UTM 31N [EPSG:23031]']
    GRID = 'GRID'
    GRID_OPTIONS = ['PENR2009']

    def getIcon(self):
        return  QIcon(os.path.dirname(__file__) + '/icons/es.png')

    def help(self):
        name = self.commandLineName().split(':')[1].lower()
        filename = os.path.join(os.path.dirname(inspect.getfile(self.__class__)), 'help', name + '.rst')
        try:
          html = getHtmlFromRstFile(filename)
          return True, html
        except:
          return False, None

    def defineCharacteristics(self):
        self.name = '[ES] Direct and inverse Raster Tranformation'
        self.group = '[ES] Spain (mainland)'
        self.addParameter(ParameterRaster(self.INPUT, 'Input raster', False))
        self.addParameter(ParameterSelection(self.TRANSF, 'Transformation',
                          self.TRANSF_OPTIONS))
        self.addParameter(ParameterSelection(self.CRS, 'Old Datum',
                          self.CRS_OPTIONS))
        self.addParameter(ParameterSelection(self.GRID, 'NTv2 Grid',
                          self.GRID_OPTIONS))
        self.addOutput(OutputRaster(self.OUTPUT, 'Output'))

    def processAlgorithm(self, progress):

        if self.getParameterValue(self.TRANSF) == 0:
            # Direct transformation
            arguments = ['-s_srs']
            if self.getParameterValue(self.CRS) == 0:
                # ED50/UTM 29N [EPSG:23029]
                if self.getParameterValue(self.GRID) == 0:
                    # PENR2009
                    arguments.append('+proj=utm +zone=29 +ellps=intl +nadgrids=' + os.path.dirname(__file__) + '/grids/PENR2009.gsb +wktext +units=m +no_defs')
                    arguments.append('-t_srs')
                    arguments.append('EPSG:4258')
            elif self.getParameterValue(self.CRS) == 1:
                # ED50/UTM 30N [EPSG:23030]
                if self.getParameterValue(self.GRID) == 0:
                    # PENR2009
                    arguments.append('+proj=utm +zone=30 +ellps=intl +nadgrids=' + os.path.dirname(__file__) + '/grids/PENR2009.gsb +wktext +units=m +no_defs')
                    arguments.append('-t_srs')
                    arguments.append('EPSG:4258')
            elif self.getParameterValue(self.CRS) == 2:
                # ED50/UTM 31N [EPSG:23031]
                if self.getParameterValue(self.GRID) == 0:
                    # PENR2009
                    arguments.append('+proj=utm +zone=31 +ellps=intl +nadgrids=' + os.path.dirname(__file__) + '/grids/PENR2009.gsb +wktext +units=m +no_defs')
                    arguments.append('-t_srs')
                    arguments.append('EPSG:4258')
        else:
            # Inverse transformation
            arguments = ['-t_srs']
            if self.getParameterValue(self.CRS) == 0:
                # ED50/UTM 29N [EPSG:23029]
                if self.getParameterValue(self.GRID) == 0:
                    # PENR2009
                    arguments.append('+proj=utm +zone=29 +ellps=intl +nadgrids=' + os.path.dirname(__file__) + '/grids/PENR2009.gsb +wktext +units=m +no_defs')
                    arguments.append('-s_srs')
                    arguments.append('EPSG:4258')
            elif self.getParameterValue(self.CRS) == 1:
                # ED50/UTM 30N [EPSG:23030]
                if self.getParameterValue(self.GRID) == 0:
                    # PENR2009
                    arguments.append('+proj=utm +zone=30 +ellps=intl +nadgrids=' + os.path.dirname(__file__) + '/grids/PENR2009.gsb +wktext +units=m +no_defs')
                    arguments.append('-s_srs')
                    arguments.append('EPSG:4258')
            elif self.getParameterValue(self.CRS) == 2:
                # ED50/UTM 31N [EPSG:23031]
                if self.getParameterValue(self.GRID) == 0:
                    # PENR2009
                    arguments.append('+proj=utm +zone=31 +ellps=intl +nadgrids=' + os.path.dirname(__file__) + '/grids/PENR2009.gsb +wktext +units=m +no_defs')
                    arguments.append('-s_srs')
                    arguments.append('EPSG:4258')

        arguments.append('-multi')
        arguments.append('-of')
        out = self.getOutputValue(self.OUTPUT)
        arguments.append(GdalUtils.getFormatShortNameFromFilename(out))
        arguments.append(self.getParameterValue(self.INPUT))
        arguments.append(out)

        if os.path.isfile(os.path.dirname(__file__) + '/grids/PENR2009.gsb') is False:
            try:
                from urllib import urlretrieve
            except ImportError:
                from urllib.request import urlretrieve
            urlretrieve ("https://github.com/NaturalGIS/ntv2_transformations_grids_and_sample_data/raw/master/es/PENR2009.gsb", os.path.dirname(__file__) + "/grids/PENR2009.gsb")

        GdalUtils.runGdal(['gdalwarp', GdalUtils.escapeAndJoin(arguments)],
                          progress)
