from qgis.PyQt.QtWidgets import QAction
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsField,
    QgsFeatureRequest,
)
from PyQt5.QtCore import QVariant
import pandas as pd
from .altitude_diff_dialog import AltitudeDiffDialog
from qgis.core import QgsRaster

class AltitudeDiffPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dialog = None

    def initGui(self):
        self.action = QAction("Altitude Diff", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("Altitude Diff", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removePluginMenu("Altitude Diff", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        self.dialog = AltitudeDiffDialog()

        # Remplir les ComboBox
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if isinstance(layer, QgsVectorLayer) and layer.geometryType() == 0:
                self.dialog.comboPointLayer.addItem(layer.name())
            if isinstance(layer, QgsRasterLayer):
                self.dialog.comboRasterLayer.addItem(layer.name())

        # Lancer le calcul quand on clique
        self.dialog.btnRun.clicked.connect(self.lancer_calcul)

        self.dialog.show()

    def lancer_calcul(self):
        point_name = self.dialog.comboPointLayer.currentText()
        raster_name = self.dialog.comboRasterLayer.currentText()

        if not point_name or not raster_name:
            self.dialog.labelStatus.setText("❌ Sélectionnez les deux couches.")
            return

        layer_point = QgsProject.instance().mapLayersByName(point_name)[0]
        layer_raster = QgsProject.instance().mapLayersByName(raster_name)[0]

        nom_champ_altitude = "altitude"
        champs_existants = [champ.name() for champ in layer_point.fields()]
        if nom_champ_altitude not in champs_existants:
            layer_point.startEditing()
            layer_point.dataProvider().addAttributes([QgsField(nom_champ_altitude, QVariant.Double)])
            layer_point.updateFields()
            layer_point.commitChanges()

        index_champ = layer_point.fields().indexFromName(nom_champ_altitude)

        layer_point.startEditing()
        for feature in layer_point.getFeatures():
            geom = feature.geometry()
            if geom.isEmpty() or not geom.isGeosValid():
                continue
            point = geom.asPoint()
            ident = layer_raster.dataProvider().identify(point, QgsRaster.IdentifyFormatValue)
            if ident.isValid():
                altitude = ident.results().get(1)
                feature.setAttribute(index_champ, altitude)
                layer_point.updateFeature(feature)
        layer_point.commitChanges()

        # Collecte des altitudes pour comparaison
        points = {}
        for feature in layer_point.getFeatures():
            point_id = feature.id()
            altitude = feature[nom_champ_altitude]
            points[point_id] = altitude

        calculations = []
        for p1_id, alt1 in points.items():
            for p2_id, alt2 in points.items():
                if p1_id < p2_id:
                    diff_altitude = alt1 - alt2
                    calculations.append({
                        'Point 1': f"p{p1_id}",
                        'Point 2': f"p{p2_id}",
                        'Différence Altitude': diff_altitude
                    })

        # Export vers Excel
        df = pd.DataFrame(calculations)
        output_file = "altitude_differences.xlsx"
        df.to_excel(output_file, index=False, header=True, engine='openpyxl')

        self.dialog.labelStatus.setText(f"✅ Fichier enregistré : {output_file}")
