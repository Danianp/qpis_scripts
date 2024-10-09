"""
Skrypt QGIS, który znajduje najbliższego sąsiada z jednej warstwy punktowej (Warstwa 2) dla każdego punktu z innej warstwy punktowej (Warstwa 1). 
Wynikiem działania skryptu jest nowa warstwa liniowa, w której każda linia łączy punkt z Warstwy 1 z najbliższym sąsiadem z Warstwy 2. 
Nowa warstwa zawiera atrybuty obu punktów, a także odległość między nimi.

Autor: [DP]
Data: [14-08-2024]

Funkcje:
- Inicjalizacja algorytmu: Definiuje parametry wejściowe i wyjściowe, czyli warstwy, które mają być użyte.
- Procesowanie algorytmu: 
  1. Pobiera warstwy wejściowe i tworzy indeks przestrzenny dla Warstwy 2.
  2. Dla każdego punktu z Warstwy 1 wyszukuje najbliższy punkt z Warstwy 2.
  3. Tworzy nową warstwę liniową, łączącą te punkty, i dodaje atrybuty obu punktów oraz odległość między nimi.
- Tworzenie instancji algorytmu: Służy do uruchamiania skryptu w QGIS.

Parametry:
- WARSTWA_1: Warstwa punktowa, której punkty będą przeszukiwane.
- WARSTWA_2: Warstwa punktowa, w której będą wyszukiwani najbliżsi sąsiedzi dla punktów z WARSTWA_1.
- WYJSCIE: Warstwa wynikowa, zawierająca linie łączące najbliższe punkty z obu warstw oraz ich atrybuty.
"""

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,  # Parametr wejściowy dla warstwy źródłowej
    QgsProcessingParameterFeatureSink,    # Parametr wyjściowy dla warstwy wynikowej
    QgsFeature,                           # Obiekt cechy
    QgsGeometry,                          # Obiekt geometrii
    QgsSpatialIndex,                      # Indeks przestrzenny dla szybszego wyszukiwania
    QgsProcessing,                        # Klasa podstawowa dla przetwarzania
    QgsWkbTypes,                          # Typy geometrii WKB
    QgsFeatureSink,                       # Miejsce docelowe dla wynikowych cech
    QgsFields,                            # Kolekcja pól (atrybutów)
    QgsField,                             # Pojedynczy atrybut (pole)
    QgsPoint,                             # Obiekt punktu (stary typ)
    QgsPointXY,                           # Obiekt punktu (nowy typ)
    QgsProject,                           # Bieżący projekt QGIS
    QgsFeatureRequest                     # Zapytanie dotyczące cech
)
from qgis.PyQt.QtCore import QVariant  # Typy danych, takie jak integer, double, string

class NajblizszySasiad(QgsProcessingAlgorithm):
    # Zdefiniowanie nazw parametrów, które będą używane w algorytmie
    WARSTWA_1 = 'WARSTWA_1'
    WARSTWA_2 = 'WARSTWA_2'
    WYJSCIE = 'WYJSCIE'

    def initAlgorithm(self, config=None):
        # Definicja pierwszej warstwy punktowej jako parametru wejściowego
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.WARSTWA_1,
                'Wybierz pierwszą warstwę punktową',
                [QgsProcessing.TypeVectorPoint]
            )
        )

        # Definicja drugiej warstwy punktowej jako parametru wejściowego
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.WARSTWA_2,
                'Wybierz drugą warstwę punktową',
                [QgsProcessing.TypeVectorPoint]
            )
        )

        # Definicja wyjściowej warstwy liniowej jako parametru wynikowego
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.WYJSCIE,
                'Wyjściowa warstwa liniowa'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Pobranie pierwszej i drugiej warstwy jako obiekty QgsFeatureSource
        warstwa1 = self.parameterAsSource(parameters, self.WARSTWA_1, context)
        warstwa2 = self.parameterAsSource(parameters, self.WARSTWA_2, context)

        # Sprawdzenie, czy warstwy zostały poprawnie załadowane
        if warstwa1 is None or warstwa2 is None:
            raise QgsProcessingException('Nie udało się załadować warstw.')

        # Utworzenie indeksu przestrzennego dla drugiej warstwy, aby przyspieszyć wyszukiwanie najbliższych sąsiadów
        index = QgsSpatialIndex(warstwa2.getFeatures())

        # Definicja pól (atrybutów) dla warstwy wynikowej
        pola = QgsFields()
        pola.append(QgsField('ID_Warstwa1', QVariant.LongLong))  # ID z pierwszej warstwy
        pola.append(QgsField('ID_Warstwa2', QVariant.LongLong))  # ID z drugiej warstwy
        pola.append(QgsField('Odległość', QVariant.Double))      # Pole na odległość między punktami

        # Dodanie atrybutów z pierwszej warstwy do warstwy wynikowej
        for field in warstwa1.fields():
            pola.append(QgsField(f'Warstwa1_{field.name()}', field.type()))

        # Dodanie atrybutów z drugiej warstwy do warstwy wynikowej
        for field in warstwa2.fields():
            pola.append(QgsField(f'Warstwa2_{field.name()}', field.type()))

        # Utworzenie warstwy wynikowej
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.WYJSCIE,
            context,
            pola,
            QgsWkbTypes.LineString,  # Typ geometrii wynikowej (linia)
            warstwa1.sourceCrs()     # CRS (układ współrzędnych) zgodny z pierwszą warstwą
        )

        # Sprawdzenie, czy warstwa wynikowa została poprawnie utworzona
        if sink is None:
            raise QgsProcessingException('Nie udało się utworzyć warstwy wynikowej.')

        # Iteracja po wszystkich cechach (punktach) w pierwszej warstwie
        for feature1 in warstwa1.getFeatures():
            geom1 = feature1.geometry()  # Pobranie geometrii punktu
            nearest_ids = index.nearestNeighbor(geom1.asPoint(), 1)  # Wyszukiwanie najbliższego punktu w drugiej warstwie
            if nearest_ids:
                nearest_id = nearest_ids[0]
                # Znalezienie najbliższego sąsiada w drugiej warstwie na podstawie ID
                feature2 = next(warstwa2.getFeatures(QgsFeatureRequest().setFilterFid(nearest_id)))

                geom2 = feature2.geometry()  # Pobranie geometrii najbliższego sąsiada

                # Konwersja geometrii do starego typu QgsPoint, jeśli to konieczne
                point1 = QgsPoint(geom1.asPoint())
                point2 = QgsPoint(geom2.asPoint())

                # Utworzenie geometrii linii łączącej dwa punkty
                linia_geom = QgsGeometry.fromPolyline([point1, point2])

                # Obliczenie odległości między punktami (w metrach)
                odleglosc = point1.distance(point2)

                # Zaokrąglenie odległości do 4 miejsc po przecinku
                odleglosc_zaokraglona = round(odleglosc, 4)

                # Utworzenie nowego obiektu (linii) z geometrią i atrybutami
                nowy_feature = QgsFeature()
                nowy_feature.setGeometry(linia_geom)  # Ustawienie geometrii linii
                atrybuty = [feature1.id(), feature2.id(), odleglosc_zaokraglona]  # Dodanie ID obu punktów i odległości
                atrybuty.extend(feature1.attributes())     # Dodanie atrybutów z pierwszej warstwy
                atrybuty.extend(feature2.attributes())     # Dodanie atrybutów z drugiej warstwy
                nowy_feature.setAttributes(atrybuty)       # Przypisanie atrybutów do nowej cechy

                # Dodanie nowej cechy do warstwy wynikowej
                sink.addFeature(nowy_feature, QgsFeatureSink.FastInsert)

        # Zwrócenie identyfikatora warstwy wynikowej
        return {self.WYJSCIE: dest_id}

    def name(self):
        return 'najblizszy_sasiad'  # Unikalna nazwa algorytmu

    def displayName(self):
        return 'Najbliższy sąsiad'  # Nazwa algorytmu, która będzie wyświetlana w QGIS

    def group(self):
        return 'Narzędzia analizy przestrzennej'  # Grupa, do której algorytm należy

    def groupId(self):
        return 'analiza_przestrzenna'  # Unikalny identyfikator grupy

    def createInstance(self):
        return NajblizszySasiad()  # Tworzenie instancji algorytmu
