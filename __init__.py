# -*- coding: utf-8 -*-
"""
/***************************************************************************
 kodypocztowe
                                 A QGIS plugin
 Returns centroids or geometries of postal code areas
                             -------------------
        begin                : 2016-08-16
        copyright            : (C) 2016 by Adam Borczyk, Bartosz Ligęza
        email                : ad.borczyk@gmail.com, ligeza.bartosz@gmail.com
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
    """Load kodypocztowe class from file kodypocztowe.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .kody_pocztowe import kodypocztowe
    return kodypocztowe(iface)
