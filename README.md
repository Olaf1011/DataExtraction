To Install:
	Python 3.7 (If not installed yet)</br>
	pip install numpy
	pip install matplotlib.pyplot
	pip install bentley_ottmann.planar
	pip install shapely
	pip install pyproj
Need:
	eDecJan-Mar2020.kml (Download on https://digital.nhs.uk/data-and-information/data-collections-and-data-sets/data-collections/general-practice-data-collections)

How to:
	1. Place the "eDecJan-Mar2020.kml" file in the same folder as the python script
	2. Run the python script
	3. Select either "y" or "n" on the bentley_ottmann question (This is to determine whether the polygon is complex)
		If "n" is selected all entries will default to "FALSE"
	4. After it says it's done running the code you can find the exported data in the same folder as the script
	5. Use excel to open .csv file
