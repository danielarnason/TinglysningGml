# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TinglysningGml
                                 A QGIS plugin
 Dan GML filer til tinglysning
                              -------------------
        begin                : 2017-03-02
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Daníel Örn Árnason
        email                : daniel.arnason@egekom.dk
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
from PyQt4.QtGui import QAction, QIcon, QFileDialog
from qgis.core import QgsMapLayerRegistry, QgsField, QgsVectorFileWriter, QgsCoordinateReferenceSystem
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from tinglysning_gml_dialog import TinglysningGmlDialog
import os.path
import datetime
import unicodedata
# MySettings (qgissettingmanager)
from tinglysning_gml_settings import MySettings

import processing

class TinglysningGml:
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
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'TinglysningGml_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Tinglysning')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'TinglysningGml')
        self.toolbar.setObjectName(u'TinglysningGml')

        # Instantiate MySettings
        self.settings = MySettings()

        # Producer info
        # TODO Flyt de her informationer i MySettings, så man kan ændre de her værdier

        self.cvrnr = '29188386'
        self.organization = 'Egedal kommune'

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
        return QCoreApplication.translate('TinglysningGml', message)


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

        # Create the dialog (after translation) and keep reference
        self.dlg = TinglysningGmlDialog()

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

        icon_path = ':/plugins/TinglysningGml/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Generer GML'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.set_time()
        self.set_methods()
        self.set_producer_info()
        self.set_layer_list()
        self.set_categories()

        # Pushbuttons
        self.dlg.pushButton_3.clicked.connect(self.select_output_file)
        self.dlg.pushButton_4.clicked.connect(self.refresh_layer_list)
        self.dlg.pushButton_2.clicked.connect(self.annuller_luk)
        self.dlg.pushButton.clicked.connect(self.save_gml)


        self.dlg.comboBox_3.activated[str].connect(self.set_under_kat)

        # Test nye methods knap!
        # self.dlg.pushButton_5.clicked.connect(self.save_gml)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Tinglysning'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def set_time(self):
        self.dlg.dateEdit.setDate(datetime.date.today())

    def set_methods(self):
        self.methods_dict = {'Absolut': 'A', 'Relativ': 'R', 'Relativ/Absolut': 'RA', 'Ejendom': 'E', 'Matrikel': 'M', 'Udefineret': 'U'}
        self.dlg.comboBox.addItems(self.methods_dict.keys())
        self.dlg.comboBox.setCurrentIndex(self.methods_dict.keys().index('Matrikel'))

    def select_output_file(self):
        self.output_filename = QFileDialog.getSaveFileName(self.dlg, u'Vælg placering', '', '*.gml')
        self.dlg.lineEdit_4.setText(self.output_filename)

    def set_producer_info(self):
        self.dlg.lineEdit.setText(self.cvrnr)
        self.dlg.lineEdit_2.setText(self.organization)

    def set_layer_list(self):
        self.lyrs = [layer.name() for layer in QgsMapLayerRegistry.instance().mapLayers().values()]
        self.dlg.comboBox_2.addItems(self.lyrs)
        self.cur_lyr = self.dlg.comboBox_2.currentText()

    def refresh_layer_list(self):
        self.dlg.comboBox_2.clear()
        self.set_layer_list()

    def annuller_luk(self):
        self.dlg.close()

    def gml_add_cols(self):
        self.cur_lyr = self.dlg.comboBox_2.currentText()
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == self.cur_lyr:
                res = lyr.dataProvider().addAttributes([QgsField('dato', QVariant.String),
                                                        QgsField('noejagt', QVariant.Int),
                                                        QgsField('metode', QVariant.String),
                                                        QgsField('oprindelse', QVariant.String),
                                                        QgsField('cvr', QVariant.Int),
                                                        QgsField('org', QVariant.String),
                                                        QgsField('esdh_nr', QVariant.String),
                                                        QgsField('overkat', QVariant.String),
                                                        QgsField('underkat', QVariant.String)
                                                        ])
                lyr.updateFields()

    def set_values(self):

        # Finder lag, de rskal være som baggrung
        self.cur_lyr = self.dlg.comboBox_2.currentText()

        # Identificer data, der skal fyldes i attributtabel
        metode = self.methods_dict[self.dlg.comboBox.currentText()]
        dato = self.dlg.dateEdit.text()

        if self.dlg.radioButton.isChecked():
            noejagtighed = 1
        elif self.dlg.radioButton_2.isChecked():
            noejagtighed = 2

        if self.dlg.radioButton_3.isChecked():
            oprindelse = 'TL'
        elif self.dlg.radioButton_4.isChecked():
            oprindelse = 'KF'

        # TODO Finde ud af encoding problemet! Skal det muligvis bare gemmes til QGIS3?
        overkat = unicodedata.normalize('NFKD', self.dlg.comboBox_3.currentText()).encode('ascii', 'ignore')
        underkat = unicodedata.normalize('NFKD', self.dlg.comboBox_4.currentText()).encode('ascii', 'ignore')

        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == self.cur_lyr:

                dato_idx = lyr.fieldNameIndex('dato')
                noejagt_idx = lyr.fieldNameIndex('noejagt')
                metode_idx = lyr.fieldNameIndex('metode')
                oprindelse_idx = lyr.fieldNameIndex('oprindelse')
                cvr_idx = lyr.fieldNameIndex('cvr')
                org_idx = lyr.fieldNameIndex('org')
                esdh_nr_idx = lyr.fieldNameIndex('esdh_nr')
                overkat_idx = lyr.fieldNameIndex('overkat')
                underkat_idx = lyr.fieldNameIndex('underkat')

                lyr.startEditing()
                for feat in lyr.getFeatures():
                    lyr.changeAttributeValue(feat.id(), dato_idx, str(dato))
                    lyr.changeAttributeValue(feat.id(), noejagt_idx, str(noejagtighed))
                    lyr.changeAttributeValue(feat.id(), metode_idx, str(metode))
                    lyr.changeAttributeValue(feat.id(), oprindelse_idx, str(oprindelse))
                    lyr.changeAttributeValue(feat.id(), cvr_idx, int(self.dlg.lineEdit.text()))
                    lyr.changeAttributeValue(feat.id(),  org_idx, str(self.dlg.lineEdit_2.text()))
                    lyr.changeAttributeValue(feat.id(), esdh_nr_idx, str(self.dlg.lineEdit_3.text()))
                    lyr.changeAttributeValue(feat.id(), overkat_idx, str(overkat))
                    lyr.changeAttributeValue(feat.id(), underkat_idx, str(underkat))
                lyr.commitChanges()

    def set_categories(self):
        self.categories = {
            'Andet': ['Andet', 'Ikke kategoriseret', u'Vandløb'],
            'Anvendelse': ['Andet', 'Anvendelsesforhold', 'Fredning', u'Højdebegrænsning', 'Sanering'],
            'Bebyggelse': ['Andet', 'Brandmur', 'Byggelinie', 'Bebyggelsesforhold', u'Vilkår'],
            'Brugs- eller ejerforhold': ['Andet', 'Jagtret'],
            'Ejendomsforhold': ['Andet', 'Byggeretligt skel', 'Grundejerforening', 'Hegn','Udstykning'],
            'Forsyning': ['Andet', 'Naturgas', 'Tilslutningspligt', 'Vand', 'Varme'],
            u'Køb og salg': ['Andet', 'Forkøbsret', 'Salgsforhold', u'Tilbagekøbsret/pligt, hjemfaldspligt'],
            'Ledninger': ['Andet', u'Forsyning/afløb', 'Telefon'],
            u'Tekniske anlæg': ['Andet', 'El, vand, varme eller gas', 'Master', u'Transformeranlæg', u'Vandværk'],
            u'Færdsel': ['Andet', 'Adgangsforhold', 'Parkering', 'Vej', 'Vejret'],
            u'Bygning på lejet grund': ['Andet']
        }

        self.dlg.comboBox_3.addItems(self.categories.keys())

        self.set_under_kat(self.dlg.comboBox_3.currentText())

    def set_under_kat(self, text):
        self.dlg.comboBox_4.clear()
        self.dlg.comboBox_4.addItems(self.categories[text])

    def save_gml(self):
        self.gml_add_cols()
        self.set_values()
        output_f = self.dlg.lineEdit_4.text()
        output_crs = QgsCoordinateReferenceSystem(25832, QgsCoordinateReferenceSystem.EpsgCrsId)
        self.cur_lyr = str(self.dlg.comboBox_2.currentText())

        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == self.cur_lyr:
                QgsVectorFileWriter.writeAsVectorFormat(lyr, output_f, 'utf-8', output_crs, 'GML')




    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
