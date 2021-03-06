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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant, QSizeF, QSize, QRectF
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QPrinter, QPainter, QImage, QColor
from PyQt4.QtXml import QDomDocument
from qgis.core import QgsMapLayerRegistry, QgsField, QgsVectorFileWriter, QgsCoordinateReferenceSystem, QgsComposition, QgsComposerLabel, QgsComposerPicture
from qgis.gui import QgsMessageBar
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from tinglysning_gml_dialog import TinglysningGmlDialog
import os
import datetime
import unicodedata
import processing
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

        # Fyld plugin med værdier
        self.set_time()
        self.set_methods()
        self.set_info()
        self.set_layer_list()
        self.set_categories()

        # Pushbuttons
        self.dlg.pushButton_3.clicked.connect(self.select_output_file)
        self.dlg.pushButton_4.clicked.connect(self.refresh_layer_list)
        self.dlg.pushButton_2.clicked.connect(self.annuller_luk)
        self.dlg.pushButton.clicked.connect(self.save_gml)
        self.dlg.pushButton_5.clicked.connect(self.generer_kortbilag)
        self.dlg.pushButton_6.clicked.connect(self.select_logo_path)

        self.dlg.comboBox_3.activated[str].connect(self.set_under_kat)
        self.dlg.comboBox_5.currentIndexChanged.connect(self.set_matrikel_columns)

        self.dlg.lineEdit_8.textEdited.connect(self.set_scale)


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
        self.output_filename = QFileDialog.getSaveFileName(self.dlg, u'Vælg placering', self.settings.value('output_path'), '*.gml')
        self.dlg.lineEdit_4.setText(self.output_filename)

    def select_logo_path(self):
        self.logo_path = QFileDialog.getOpenFileName(self.dlg, 'V�lg fil med logo', self.settings.value('logo_path'))
        self.settings.set_value('logo_path', self.logo_path)
        self.dlg.lineEdit_9.setText(os.path.basename(self.logo_path))

    def set_info(self):
        self.dlg.lineEdit.setText(self.settings.value('cvrnr'))
        self.dlg.lineEdit_2.setText(self.settings.value('organization'))
        self.dlg.lineEdit_9.setText(os.path.basename(self.settings.value('logo_path')))

    def set_layer_list(self):
        self.lyrs = [layer.name() for layer in QgsMapLayerRegistry.instance().mapLayers().values()]
        self.dlg.comboBox_2.addItems(self.lyrs)
        self.dlg.comboBox_5.addItems(self.lyrs)
        self.cur_lyr = self.dlg.comboBox_2.currentText()

    def refresh_layer_list(self):
        self.dlg.comboBox_2.clear()
        self.dlg.comboBox_5.clear()
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

        if len(self.dlg.lineEdit_3.text()) > 0:
            esdh_nr = str(self.dlg.lineEdit_3.text())
        else:
            esdh_nr = ''

        self.settings.set_value('cvrnr', self.dlg.lineEdit.text())
        self.settings.set_value('organization', self.dlg.lineEdit_2.text())

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

                    if self.settings.value('cvrnr') == '':
                        lyr.changeAttributeValue(feat.id(), cvr_idx, 0)
                    else:
                        lyr.changeAttributeValue(feat.id(), cvr_idx, int(self.settings.value('cvrnr')))
                    
                    lyr.changeAttributeValue(feat.id(),  org_idx, str(self.settings.value('organization')))
                    lyr.changeAttributeValue(feat.id(), esdh_nr_idx, str(esdh_nr))
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
            u'Køb og salg': ['Andet', u'Forkøbsret', 'Salgsforhold', u'Tilbagekøbsret/pligt, hjemfaldspligt'],
            'Ledninger': ['Andet', u'Forsyning/afløb', 'Telefon'],
            u'Tekniske anlæg': ['Andet', 'El, vand, varme eller gas', 'Master', u'Transformeranlæg', u'Vandværk'],
            u'Færdsel': ['Andet', 'Adgangsforhold', 'Parkering', 'Vej', 'Vejret'],
            u'Bygning på lejet grund': ['Andet']
        }

        self.dlg.comboBox_3.addItems(self.categories.keys())
        self.dlg.comboBox_3.setCurrentIndex(3)

        self.set_under_kat(self.dlg.comboBox_3.currentText())
        self.dlg.comboBox_4.setCurrentIndex(3)

    def set_under_kat(self, text):
        self.dlg.comboBox_4.clear()
        self.dlg.comboBox_4.addItems(self.categories[text])

    def save_gml(self):
        try:
            self.set_matrikler()
            self.gml_add_cols()
            self.set_values()
            output_f = self.dlg.lineEdit_4.text()
            output_crs = QgsCoordinateReferenceSystem(25832, QgsCoordinateReferenceSystem.EpsgCrsId)
            self.cur_lyr = self.dlg.comboBox_2.currentText()
            self.settings.set_value('output_path', os.path.dirname(self.dlg.lineEdit_4.text()))

            for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
                if lyr.name() == self.cur_lyr:
                    QgsVectorFileWriter.writeAsVectorFormat(lyr, output_f, 'utf-8', output_crs, 'GML')

            if self.dlg.checkBox_4.isChecked() == True:
                for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
                    if lyr.name() == self.cur_lyr:
                        QgsMapLayerRegistry.instance().removeMapLayers([lyr.id()])

                self.iface.addVectorLayer(output_f, os.path.basename(output_f).split('.')[0], 'ogr')
                self.iface.messageBar().pushMessage('INFO', u'GML filen er gemt og åbnet i QGIS', level=QgsMessageBar.INFO, duration=5)
            else:
                self.iface.messageBar().pushMessage('INFO', u'GML filen er gemt', level=QgsMessageBar.INFO, duration=5)
        except KeyError:
            self.iface.messageBar().pushMessage('FEJL', u'Husk at vælge matrikellaget i lagvinduet', level=QgsMessageBar.CRITICAL, duration=10)
            # self.iface.activeLayer().removeSelection()
        except IndexError:
            self.iface.messageBar().pushMessage('FEJL', u'GML fil ikke gemt! Husk at markere matrikellaget i lagvinduet', level=QgsMessageBar.CRITICAL, duration=10)

    def generer_composition(self):

        comp_lyr = None
        home = os.path.expanduser('~')

        if self.dlg.checkBox_4.isChecked() == False:
            for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
                if lyr.name() == self.dlg.comboBox_2.currentText():
                    comp_lyr = lyr
                    processing.runalg('qgis:setstyleforvectorlayer', comp_lyr.source(), os.path.join(home, '.qgis2', 'python', 'plugins', 'TinglysningGml', 'hegn_style.qml'))
                    self.iface.mapCanvas().refresh()
                    self.iface.legendInterface().refreshLayerSymbology(lyr)
                else:
                    pass
        else:
            for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
                try:
                    if lyr.storageType() == 'GML':
                        comp_lyr = lyr
                        processing.runalg('qgis:setstyleforvectorlayer', comp_lyr.source(), os.path.join(home, '.qgis2', 'python', 'plugins', 'TinglysningGml', 'hegn_style.qml'))
                        self.iface.mapCanvas().refresh()
                        self.iface.legendInterface().refreshLayerSymbology(lyr)
                except AttributeError:
                    pass

        template_path = os.path.join(home, '.qgis2', 'python', 'plugins', 'TinglysningGml', 'print_skabelon.qpt')
        template_file = file(template_path)
        template_content = template_file.read()
        template_file.close()

        document = QDomDocument()
        document.setContent(template_content)

        canvas = self.iface.mapCanvas()

        composition = QgsComposition(canvas.mapSettings())
        composition.loadFromTemplate(document, {})

        # set map item
        map_item = composition.getComposerItemById('map')
        map_item.setMapCanvas(canvas)
        if len(self.dlg.lineEdit_8.text()) > 0:
            map_item.zoomToExtent(comp_lyr.extent())
            canvas.zoomScale(int(self.scale))
            map_item.setNewScale(canvas.scale())
        else:
            map_item.zoomToExtent(canvas.extent())

        # set text
        composerLabel = QgsComposerLabel(composition)
        composerLabel.setText('Vedr.:\t' + self.dlg.lineEdit_5.text() + '\n' + \
                              'Matrikler: ' + self.dlg.lineEdit_6.text() + '\n' + \
                              'Ejerlav: ' + self.dlg.lineEdit_7.text() + '\n' + \
                              'Journalnr: ' + self.dlg.lineEdit_3.text() + '\n' + \
                              'Dato: ' + self.dlg.dateEdit.text())
        composerLabel.setMarginY(-16)
        composerLabel.adjustSizeToText()
        composerLabel.setItemPosition(140, 196)
        # composerLabel.setFrameEnabled(True)
        composition.addItem(composerLabel)

        composerLabel2 = QgsComposerLabel(composition)
        composerLabel2.setText('{} erkl�rer, at der er overensstemmelse mellem rids og GML fil'.format(self.settings.value('organization')))
        composerLabel2.adjustSizeToText()
        composerLabel2.setItemPosition(1.739, 166.939)
        composition.addItem(composerLabel2)


        # Set northarrow
        northarrow = QgsComposerPicture(composition)
        northarrow_path = os.path.join(home, '.qgis2', 'python', 'plugins', 'TinglysningGml', 'northarrow.svg')
        northarrow.setPictureFile(northarrow_path)
        northarrow.setSceneRect(QRectF( 0, 0, 6, 10))
        northarrow.setItemPosition(285,5)
        composition.addItem(northarrow)

        # Set Egedal logo
        logo = QgsComposerPicture(composition)
        logo_path = self.settings.value('logo_path')
        logo.setPictureFile(logo_path)
        logo.setSceneRect(QRectF(0, 0, 57, 28))
        logo.setItemPosition(238, 179)
        composition.addItem(logo)

        return composition

    def generer_pdf(self, composition):

        output_name = 'rids_' + self.dlg.lineEdit_6.text().replace(', ', '_') + '_' + self.dlg.lineEdit_7.text().replace(', ', '_') + '.pdf'

        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(self.settings.value('output_path') + os.sep + output_name)
        printer.setPaperSize(QSizeF(composition.paperWidth(), composition.paperHeight()), QPrinter.Millimeter)
        printer.setFullPage(True)
        printer.setColorMode(QPrinter.Color)
        printer.setResolution(composition.printResolution())

        pdfPainter = QPainter(printer)
        paperRectMM = printer.pageRect(QPrinter.Millimeter)
        paperRectPixel = printer.pageRect(QPrinter.DevicePixel)
        composition.render(pdfPainter, paperRectPixel, paperRectMM)
        pdfPainter.end()
        self.iface.messageBar().pushMessage('INFO', u'PDF fil gemt!', level=QgsMessageBar.INFO, duration=5)

    def generer_img(self,composition, format):

        output_name = 'rids_' + self.dlg.lineEdit_6.text() + '_' + self.dlg.lineEdit_7.text() + '.{}'.format(format)

        dpmm = 300 / 25.4

        width = int(dpmm * composition.paperWidth())
        height = int(dpmm * composition.paperHeight())

        image = QImage(QSize(width, height), QImage.Format_ARGB32)
        image.setDotsPerMeterX(dpmm * 1000)
        image.setDotsPerMeterY(dpmm * 1000)
        image.fill(0)

        imagePainter = QPainter(image)
        composition.renderPage(imagePainter, 0)
        imagePainter.end()

        image.save(self.settings.value('output_path') + os.sep + output_name, '{}'.format(format))

    def generer_kortbilag(self):
        composition = self.generer_composition()
        if self.dlg.checkBox.isChecked() == True:
            self.generer_pdf(composition)

        if self.dlg.checkBox_2.isChecked() == True:
            self.generer_img(composition, 'jpg')

        if self.dlg.checkBox_3.isChecked() == True:
            self.generer_img(composition, 'png')

        if self.dlg.checkBox.isChecked() == False and self.dlg.checkBox_2.isChecked() == False and self.dlg.checkBox_3.isChecked() == False:
            self.iface.messageBar().pushMessage('FEJL', u'Du skal vælge mindst ét format til kortbilag', level=QgsMessageBar.CRITICAL, duration=5)

    def set_scale(self):
        self.scale = self.dlg.lineEdit_8.text()

    def set_matrikler(self):
        cur_lyr = None
        matrikler = None
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == self.dlg.comboBox_2.currentText():
                cur_lyr = lyr
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == self.dlg.comboBox_5.currentText():
                matrikler = lyr

        processing.runalg('qgis:selectbylocation', matrikler, cur_lyr, u'intersects', 0, 0)

        # if len(matrikler.selectedFeatures()) > 0:
        matrikel_lst = [feat.attribute(self.dlg.comboBox_6.currentText()) for feat in matrikler.selectedFeatures()]

        self.dlg.lineEdit_7.setText(matrikler.selectedFeatures()[0].attribute(self.dlg.comboBox_7.currentText()))
        self.dlg.lineEdit_6.setText(', '.join(i for i in matrikel_lst))

        matrikler.removeSelection()

    def set_matrikel_columns(self):
        self.dlg.comboBox_6.clear()
        self.dlg.comboBox_7.clear()
        attributes = None
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == self.dlg.comboBox_5.currentText():
                attributes = [lyr.attributeDisplayName(i) for i in lyr.attributeList()]
        if attributes == None:
            pass
        else:
            self.dlg.comboBox_6.addItems(attributes)
            self.dlg.comboBox_7.addItems(attributes)

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        self.set_matrikel_columns()

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
