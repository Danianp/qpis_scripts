from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsVectorFileWriter,
    QgsWkbTypes
)
from qgis.PyQt.QtWidgets import QInputDialog, QMessageBox
import math
import os

# Funkcja do tworzenia okręgów
def create_circle(center, radius, segments=36):
    points = []
    for i in range(segments):
        angle = (i * (360 / segments))
        angle_radians = angle * (math.pi / 180)
        x = center.x() + (radius * math.cos(angle_radians))
        y = center.y() + (radius * math.sin(angle_radians))
        points.append(QgsPointXY(x, y))
    points.append(points[0])
    return QgsGeometry.fromPolygonXY([points])

# Wywołanie dialogu do wyboru warstwy
layers = QgsProject.instance().mapLayers().values()
layer_list = [layer.name() for layer in layers]
layer_name, ok = QInputDialog.getItem(None, "Wybór warstwy", "Wybierz warstwę punktową:", layer_list, 0, False)

if not ok:
    QMessageBox.critical(None, "Błąd", "Nie wybrano warstwy!")
    exit()

# Pobranie wybranej warstwy
layer = QgsProject.instance().mapLayersByName(layer_name)[0]

# Sprawdzenie, czy warstwa jest warstwą punktową
if layer.geometryType() != QgsWkbTypes.PointGeometry:
    QMessageBox.critical(None, "Błąd", "Wybrana warstwa nie jest warstwą punktową!")
    exit()

# Ustawienie układu współrzędnych EPSG:2177 (Układ 2000, strefa VI)
crs = QgsCoordinateReferenceSystem("EPSG:2177")
layer.setCrs(crs)

# Tworzymy nową warstwę tymczasową dla okręgów
temp_layer = QgsVectorLayer("Polygon?crs=EPSG:2177", "okręgi", "memory")
temp_layer_pr = temp_layer.dataProvider()
temp_layer.updateFields()

# Definiujemy promień okręgów
radius = 10  # jednostki zgodne z CRS warstwy

# Iteracja przez wszystkie punkty i tworzenie okręgów
features = layer.getFeatures()
circle_features = []

for feature in features:
    point = feature.geometry().asPoint()
    circle = create_circle(point, radius)
    new_feature = QgsFeature()
    new_feature.setGeometry(circle)
    circle_features.append(new_feature)

# Dodanie okręgów do nowej warstwy
temp_layer_pr.addFeatures(circle_features)
temp_layer.updateExtents()

# Debugowanie - Sprawdzenie liczby okręgów
print(f"Liczba wygenerowanych okręgów: {len(circle_features)}")

# Sprawdzanie geometrii nowej warstwy
for feat in temp_layer.getFeatures():
    print(feat.geometry())

# Ścieżka do pliku DXF
output_dxf_path = os.path.join(os.path.expanduser('~'), 'exported_points.dxf')

# Opcje eksportu DXF
dxf_options = QgsVectorFileWriter.SaveVectorOptions()
dxf_options.driverName = "DXF"
dxf_options.fileEncoding = "UTF-8"

# Eksportuj warstwę do DXF
error, errMsg = QgsVectorFileWriter.writeAsVectorFormatV2(temp_layer, output_dxf_path, QgsCoordinateTransformContext(), dxf_options)

# Sprawdzanie błędów eksportu
if error == QgsVectorFileWriter.NoError:
    print(f"Warstwa została wyeksportowana do pliku: {output_dxf_path}")
else:
    print(f"Nie udało się wyeksportować warstwy. Kod błędu: {error}")
    print(f"Komunikat błędu: {errMsg}")
    if error == QgsVectorFileWriter.ErrInvalidLayer:
        print("Błąd: Warstwa jest nieprawidłowa.")
    elif error == QgsVectorFileWriter.ErrCreateLayer:
        print("Błąd: Nie udało się utworzyć warstwy.")
    elif error == QgsVectorFileWriter.ErrCreateDataSource:
        print("Błąd: Nie udało się utworzyć źródła danych.")
    elif error == QgsVectorFileWriter.ErrEmptyOutputFile:
        print("Błąd: Plik wyjściowy jest pusty.")
