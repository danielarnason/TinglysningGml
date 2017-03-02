# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TinglysningGml
                                 A QGIS plugin
 Dan GML filer til tinglysning
                             -------------------
        begin                : 2017-03-02
        copyright            : (C) 2017 by Daníel Örn Árnason
        email                : daniel.arnason@egekom.dk
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load TinglysningGml class from file TinglysningGml.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .tinglysning_gml import TinglysningGml
    return TinglysningGml(iface)
