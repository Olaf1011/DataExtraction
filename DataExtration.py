import statistics
import time
import csv
import xml.etree.ElementTree as xml
import xml.etree.cElementTree as ET
import numpy as np
import PlotData as pd
from ground.base import get_context  # https://pypi.org/project/bentley-ottmann/
from bentley_ottmann.planar import contour_self_intersects  # https://pypi.org/project/bentley-ottmann/
from shapely.geometry import Polygon  # https://pypi.org/project/Shapely/
from pyproj import Proj  # https://pyproj4.github.io/pyproj/stable/index.html


'''Made By Olaf Oude Reimer, with help from Thomas Wells'''


class Position(object):
	def __init__(self, pos):
		self.longitude = pos[0]
		self.latitude = pos[1]


class ImportedData(object):
	def __init__(self, coords=None, name=None):
		self.pos = []
		for i in range(len(coords)):
			self.pos.append(Position(coords[i].split(",")))
		# OSDcode
		self.name = name
		# Number of coordinates
		self.vertices = -1
		# Simple or complex polygon
		self.isSimple = True
		self.isPolygon = True
		# Area of Polygons
		self.area = -1.0
		self.perimeter = -1.0
		# Unique id of data set
		self.id = -1


class DataHandler:
	def __init__(self):

		self.mAllData = []
		self.mCountArray = []
		self.mMedianArray = []
		self.mAreaZero = 0
		self.mUniques = 0
		self.mAverage = 0
		self.mMedian = 0
		self.mUpperQuartile = 0
		self.mLowerQuartile = 0
		self.mQuartileRange = 0
		self.CalculatedMax = 0
		self.CalculatedMin = 0
		self.THRESHOLD = 10
		self.mHasFile = True
		self.mFileName = "eDecJan-Mar2020.kml"
		# This has to be last!
		self.ExtractData()

	def ExtractData(self):
		try:
			# Opens kml(xml) file
			myFile = xml.parse(self.mFileName)
			root = myFile.getroot()
		except:
			print("couldn't open/find {}.".format(self.mFileName))
			print("Make sure the file is in the same folder as the python script")
			# Checks if the name might have changed. Gives the user the option to type in the new name.
			#
			if input("Different name y/n? ").lower() == "y":
				self.mFileName = input("New name: ")
				# Loops back to the top to try the new name. Comes back here if name doesn't work
				self.ExtractData()
				# Makes sure it doesn't run the rest
				return
			self.mHasFile = False

		if self.mHasFile:
			if input("This script will overwrite files made before by the same script."
					 "\nIt will NOT overwrite the original KML file.\nContinue? y/n? ").lower() == "n":
				return
			# look for all instances of coordinats in kml file
			assert (root is not None)
			for i in range(1, len(root[0][0]) - 1):
				# Coordinates ,ODSCode
				self.mAllData.append(ImportedData(root[0][0][i][3][0][0][0].text.split(), root[0][0][i][1][0][0].text))

	def CheckData(self):
		if not self.mHasFile:
			return
		print("Running..")

		self.AllCalculations()
		self.ExportToVisual()

		print("Done running all code.\nFind all export data in the same folder as this script")

	# self.PrintData()
	# self.NumberPolygonGrouping()

	def AllCalculations(self):
		for x in range(len(self.mAllData)):
			# Adds an unique ID to each entry
			self.mAllData[x].id = x + 1
			# x + 1 (+1 because the lines start at 1) to show which line is incorrect data
			if self.CheckPolygon(self.mAllData[x].pos):
				self.mAllData[x].isPolygon = False
				print("Line:", x + 1, "is not a polygon.")
			self.CheckAverage(self.mAllData[x].pos, x)
			self.AddToMedian(self.mAllData[x].pos)
			self.mAllData[x].vertices = len(self.mAllData[x].pos)

		self.BentleyOttman()

		self.mMedianArray.sort()

		self.Quartiles()
		self.CountCheck()

		self.PolygonCharacteristics()
		self.CheckUniqueness()
		print("Done Running calculations")

	# Runs all the code that exports the data in their own form
	def ExportToVisual(self):
		print("Export to visuals")
		self.ExportData()
		if input("Would like you to plot the visual data? y/n? ").lower() == "n":
			return
		pd.PlotData(self.mMedianArray, self.mQuartileRange, self.mCountArray)

	# Runs the Bentley Ottman algorithm (https://pypi.org/project/bentley-ottmann/)
	# To check if the given polygons are complex
	def BentleyOttman(self):
		if input("Are you sure you want to run Bentley Ottman? y/n? ").lower() == "n":
			print("!!Heads up all sets will show 'FALSE' for 'Is complex'!!")
			return
		startTime = time.time()
		print("Running Bentley Ottman..")
		for i in range(len(self.mAllData)):
			context = get_context()
			point, contour = context.point_cls, context.contour_cls
			tempPolygon = []
			# Converts our coordinates into coordinates the algorithm can use
			for j in range(len(self.mAllData[i].pos) - 1):
				tempPolygon.append(
					(point(float(self.mAllData[i].pos[j].longitude), float(self.mAllData[i].pos[j].latitude))))

			# If their is a line that intersects it will put False back into it's own data
			if contour_self_intersects(contour(tempPolygon)):
				self.mAllData[i].isSimple = False
		print("Done Running Bentely Ottman. It took %s seconds" % (time.time() - startTime))

	# Calculates the area and perimeter of the given polygons
	def PolygonCharacteristics(self):
		print("Calculating Area and Perimeter")
		for i in range(len(self.mAllData)):
			tempArray = []
			# Using the cassini-Solder projection
			pa = Proj("+proj=cass")
			# Converts the gps coordinates to meters from degrees using
			# (https://pyproj4.github.io/pyproj/stable/api/proj.html#pyproj-proj)
			for x in range(len(self.mAllData[i].pos)):
				x, y = pa(float(self.mAllData[i].pos[x].longitude), float(self.mAllData[i].pos[x].latitude))
				tempArray.append((x, y))

			polygon = Polygon(Polygon(tempArray))

			self.mAllData[i].area = polygon.area
			self.mAllData[i].perimeter = polygon.length
			if polygon.area == 0.0:
				self.mAreaZero += 1
		print("Areas = 0:", self.mAreaZero)

	# Finds the Lower and Upper Quartiles and calculates the Inter Quartile Range
	def Quartiles(self):
		self.mMedian = statistics.median(self.mMedianArray)
		self.mLowerQuartile = np.quantile(self.mMedianArray, 0.25)
		self.mUpperQuartile = np.quantile(self.mMedianArray, 0.75)
		self.mQuartileRange = self.mUpperQuartile - self.mLowerQuartile
		self.CalculatedMax = self.mUpperQuartile + (1.5 * self.mQuartileRange)
		self.CalculatedMin = self.mLowerQuartile - (1.5 * self.mQuartileRange)

	# Calculates the amount of x amount of x sides polygons.
	def NumberPolygonGrouping(self):
		# Uses countArray to display occurences not equal to 0 as a total occurences of polygons
		for x in range(len(self.mCountArray)):
			if self.mCountArray[x] != 0:
				print("There is", self.mCountArray[x], "occurrences of", x, "sided polygons.")

	def AddToMedian(self, lineData):
		self.mMedianArray.append(len(lineData))

	# Checks if it's a polygon or a line by check if the last coordinate is the same as the first thus
	# completing the polygon
	def CheckPolygon(self, lineData):
		# Checks how big the array is and picks the integer for the last item in the array
		lastItem = len(lineData) - 1
		# Checks if the first item and last item are not the same. Meaning it's not a complete polygon.
		return lineData[0].longitude != lineData[lastItem].longitude and lineData[0].latitude != lineData[
			lastItem].latitude

	# Checks the average amount of entries per data set
	def CheckAverage(self, lineData, i):
		self.mAverage += len(lineData)
		# If it's the last item in the list divide by the total of elements in mAllData[1]
		if (i + 1) == len(self.mAllData):
			self.mAverage /= len(self.mAllData)

	# Counts the amount there are of x amount of coordinates
	# So for example if there are 3 sets that only has 5 coordinates we count enter 3 into the array at the 5 position
	# So we can now see that there are only 3 sets that have 5 coordinates etc.
	def CountCheck(self):
		x = 0
		i = 0
		# Counts and appends the occurrences of length by group from mMedianArray into countArray
		while x < len(self.mMedianArray):
			countResult = self.mMedianArray.count(i)
			self.mCountArray.append(countResult)
			x += countResult
			i += 1

	# Checks how many unique ODScodes there are in the data set
	def CheckUniqueness(self):
		print("Checking uniques")
		tempArray = []
		# Move name data into it's own temp array to count
		for data in self.mAllData:
		    tempArray.append(data.name)

		self.mUniques = len(set(tempArray))

	def ExportXML(self):
		header = ["ID", "ODScode", "Ispolygon", "IsComplex", "NumberOfCoordinates", "Area",
		          "Perimeter", "Coordinates"]
		root = ET.Element("Data")
		root.tail = "\n"
		root.text = "\n\t"
		for allData in self.mAllData:
			doc = ET.SubElement(root, "Set")
			doc.tail = "\n"
			doc.text = "\n\t\t"
			for head in header:
				sub = ET.SubElement(doc, str(head))
				sub.tail = "\n\t\t"
				if head == header[0]:
					sub.text = str(allData.id)
				elif head == header[1]:
					sub.text = str(allData.name)
				elif head == header[2]:
					sub.text = str(allData.isPolygon)
				elif head == header[3]:
					sub.text = str(not allData.isSimple)
				elif head == header[4]:
					sub.text = str(allData.vertices)
				elif head == header[5]:
					sub.set("Units", "km^2")
					sub.text = str(allData.area / 1000000.0)
				elif head == header[6]:
					sub.text = str(allData.perimeter / 100.0)
					sub.set("Units", "km")
				elif head == header[7]:
					tempPos = ""
					for positions in allData.pos:
						tempPos += str(positions.longitude) + "," + str(positions.latitude) + " "
					sub.text = str(tempPos)
					sub.tail = "\n\t"
				else:
					assert(False, "Header is bigger than points of data")
			root[-1].tail = "\n\t"

		tree = ET.ElementTree(root)
		tree.write("ExportedData.xml")

	# Exports the data to a CSV file and text. Leaving out the coordinates as it's exceeds the excel char cell limit
	# CSV contains: "ID", "ODS code", "Is polygon", "Is Complex", "Number of coordinates", "Area (km²)"," Perimeter (km)"
	# Text contains: "Areas equal to 0:", "Unique entries:"
	def ExportData(self):
		print("Exporting data")
		f = open("ExtraDataExport.txt", "w")
		tempString = "Areas equal to 0: "
		tempString += str(self.mAreaZero)
		f.write(tempString)
		tempString = "\nUnique entries: "
		tempString += str(self.mUniques)
		f.write(tempString)
		f.close()
		header = ["ID", "ODS code", "Is polygon", "Is Complex", "Number of coordinates", "Area (km²)",
		          " Perimeter (km)"]
		with open('PolygonData.csv', 'w', newline='') as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow(header)
			for allData in self.mAllData:
				data = [allData.id, allData.name, allData.isPolygon, not allData.isSimple, allData.vertices,
			        (allData.area / 1000000.0), (allData.perimeter / 100.0)]
				writer.writerow(data)
		self.ExportXML()


# Makes sure that it will only run these functions if this is the file that is being executed and not being imported
if __name__ == "__main__":
	Main = DataHandler()
	Main.CheckData()
