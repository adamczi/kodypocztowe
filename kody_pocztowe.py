# -*- coding: utf-8 -*-
"""
/***************************************************************************
 kodypocztowe
                                 A QGIS plugin
 Returns centroids or geometries of postal code areas
                              -------------------
        begin                : 2016-08-16
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Adam Borczyk
        email                : ad.borczyk@gmail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant
from PyQt4.QtGui import QAction, QIcon
from qgis.core import QgsField, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPoint, QgsMapLayerRegistry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
from qgis.gui import QgsMessageBar
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from kody_pocztowe_dialog import kodypocztoweDialog
import os.path
import urllib, json, re


class kodypocztowe:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        ## To get information from canvas (EPSG)
        self.canvas = self.iface.mapCanvas() 

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'kodypocztowe_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference, window on top
        self.dlg = kodypocztoweDialog(self.iface.mainWindow())

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Kody pocztowe')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'kodypocztowe')
        self.toolbar.setObjectName(u'kodypocztowe')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('kodypocztowe', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ':/plugins/kodypocztowe/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Kody pocztowe'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Kody pocztowe'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def requestAPI(self, code):
        """ Send the request """
        queryString = 'http://127.0.0.1:5000/%s' % code
        try:
            ## Get the data
            response = urllib.urlopen(queryString)
            data = json.loads(response.read())
            if data != code: # if exists in database
                self.coords = data['coordinates']            
                return data            
            else:    
                return 'keyerror'
        except IOError:
            return 'db_error'

    def createShapefile(self):
        ## Get GeoJSON data from request
        geojson = self.requestAPI(self.code)

        ## Extract points from GeoJSON ...
        count = 0
        tempPolygons = []
        for j in geojson['coordinates']:
            tempPoints = [QgsPoint(i[0], i[1]) for i in geojson['coordinates'][count][0]]
            count += 1
            tempPolygons.append([tempPoints])        
        ## ... and store them in MultiPolygon geometry
        geom = QgsGeometry.fromMultiPolygon(tempPolygons)

        ## Get current EPSG and apply transformation if needed
        currentEPSG = self.canvas.mapRenderer().destinationCrs().authid()
        if currentEPSG != 'EPSG:2180':
            crsSrc = QgsCoordinateReferenceSystem(2180)    # WGS 84
            crsDest = QgsCoordinateReferenceSystem(int(currentEPSG[5:]))
            xform = QgsCoordinateTransform(crsSrc, crsDest)
            geom.transform(xform)

        ## Set appropriate layer and name parameters
        layerType = 'Point' if self.dlg.radioButton_1.isChecked() else 'Multipolygon'
        name = '_centr' if self.dlg.radioButton_1.isChecked() else '_geom'
        if self.dlg.radioButton_1.isChecked():
            geom = geom.centroid()


        ## Create vector layer
        vl = QgsVectorLayer("%s?crs=%s" % (layerType, currentEPSG), self.code+'%s' % name, "memory") 
        pr = vl.dataProvider()

        ## Add field
        pr.addAttributes([QgsField("item", QVariant.String)])
        vl.updateFields()

        ## Add feature with geometry
        fet = QgsFeature()
        fet.setGeometry(geom)
        fet.setAttributes([self.code])
        pr.addFeatures([fet])

        ## Add map layer
        vl.updateExtents()
        QgsMapLayerRegistry.instance().addMapLayer(vl)
        vl.setLayerTransparency(20)


    def codeCheck(self):
        """ Checks if code input is valid """
        self.code = self.dlg.lineEdit.text()
        pattern = '^[0-9]{2}-[0-9]{3}$'
        if re.match(pattern, self.code, flags=0) != None:
            return self.code                
        else: 
            return 'invalid code'        

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()

        self.dlg.lineEdit.setCursorPosition(0)
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            if self.codeCheck() != 'invalid code': # if code string valid
                if self.requestAPI(self.code) == 'keyerror': # if code exists
                    self.iface.messageBar().pushMessage("Error", "Taki kod nie istnieje w bazie", level=QgsMessageBar.WARNING, duration=3)
                elif self.requestAPI(self.code) == 'db_error':
                    self.iface.messageBar().pushMessage("Error", u"Brak połączenia z bazą danych", level=QgsMessageBar.CRITICAL, duration=3)
                else:
                    self.createShapefile() # do things
            else:
                self.iface.messageBar().pushMessage("Error", u"Nieprawidłowy kod pocztowy", level=QgsMessageBar.WARNING, duration=3)