# -*- coding: utf-8 -*-
"""
/***************************************************************************
 kodypocztoweDialog
                                 A QGIS plugin
 Returns centroids or geometries of postal code areas
                             -------------------
        begin                : 2016-08-16
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Adam Borczyk, Bartosz Ligęza
        email                : ad.borczyk@gmail.com, ligeza.bartosz@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'kody_pocztowe_dialog_base.ui'))


class kodypocztoweDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(kodypocztoweDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
