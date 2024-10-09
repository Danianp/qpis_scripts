import processing, os, glob

from os.path import expanduser
home = expanduser("~")

result_path = home + "\Desktop\Results\\"
os.chdir(home + "\Desktop\Testing\\")

for fname in glob.glob("*.shp"):
    output_0=processing.runalg('qgis:deletecolumn', fname, "myFirstField", None)
    output_1=processing.runalg('qgis:deletecolumn', output_0['OUTPUT'], "mySecondField", None)
    output_2=processing.runalg('qgis:deletecolumn', output_1['OUTPUT'], "myThirdField", 
