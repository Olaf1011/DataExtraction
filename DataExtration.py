import statistics
import time
import csv
import xml.etree.ElementTree as xml
import numpy as np
import PlotData as pd
from ground.base import get_context
from bentley_ottmann.planar import contour_self_intersects
from shapely.geometry import Polygon
from pyproj import Proj
'''Made By Olaf Oude Reimer, with help from Thomas Wells'''


class Position(object):
	def __init__(self, pos):
		self.x = pos[0]
		self.y = pos[1]


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
			if input("Different name y/n?").lower() == "y":
				self.mFileName = input("New name:")
				self.ExtractData()
				return
			self.mHasFile = False


		if self.mHasFile:
			# look for all instances of coordinats in kml file
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

	def ExportToVisual(self):
		print("Export to visuals")
		self.ExportData()
		pd.PlotData(self.mMedianArray, self.mQuartileRange, self.mCountArray)

	def BentleyOttman(self):
		if input("Are you sure you want to run Bentley Ottman? Y/N ").lower() == "n":
			return
		startTime = time.time()
		print("Running Bentley Ottman..")
		for i in range(len(self.mAllData)):
			context = get_context()
			point, contour = context.point_cls, context.contour_cls
			tempPolygon = []
			for j in range(len(self.mAllData[i].pos) - 1):
				tempPolygon.append((point(float(self.mAllData[i].pos[j].x), float(self.mAllData[i].pos[j].y))))

			if contour_self_intersects(contour(tempPolygon)):
				self.mAllData[i].isSimple = False
		print("Done Running Bentely Ottman it took %s seconds" % (time.time() - startTime))

	def PolygonCharacteristics(self):
		print("Calculating Area and Perimeter")
		for i in range(len(self.mAllData)):
			tempArray = []
			pa = Proj("+proj=cass")

			for x in range(len(self.mAllData[i].pos)):
				x, y = pa(float(self.mAllData[i].pos[x].x), float(self.mAllData[i].pos[x].y))
				tempArray.append((x, y))
			polygon = Polygon(Polygon(tempArray))

			self.mAllData[i].area = polygon.area
			self.mAllData[i].perimeter = polygon.length
			if polygon.area == 0.0:
				self.mAreaZero += 1
		print("Areas = 0:", self.mAreaZero)

	def Quartiles(self):
		# Finds the Lower and Upper Quartiles and calculates the Inter Quartile Range
		self.mMedian = statistics.median(self.mMedianArray)
		self.mLowerQuartile = np.quantile(self.mMedianArray, 0.25)
		self.mUpperQuartile = np.quantile(self.mMedianArray, 0.75)
		self.mQuartileRange = self.mUpperQuartile - self.mLowerQuartile
		self.CalculatedMax = self.mUpperQuartile + (1.5 * self.mQuartileRange)
		self.CalculatedMin = self.mLowerQuartile - (1.5 * self.mQuartileRange)

	def NumberPolygonGrouping(self):
		# Uses countArray to display occurences not equal to 0 as a total occurences of polygons
		for x in range(len(self.mCountArray)):
			if self.mCountArray[x] != 0:
				print("There is", self.mCountArray[x], "occurrences of", x, "sided polygons.")

	def AddToMedian(self, lineData):
		self.mMedianArray.append(len(lineData))

	def CheckPolygon(self, lineData):
		# Checks how big the array is and picks the integer for the last item in the array
		lastItem = len(lineData) - 1
		# Checks if the first item and last item are not the same. Meaning it's not a complete polygon.
		return lineData[0].x != lineData[lastItem].x and lineData[0].y != lineData[lastItem].y

	def CheckAverage(self, lineData, i):
		self.mAverage += len(lineData)
		# If it's the last item in the list divide by the total of elements in mAllData[1]
		if (i + 1) == len(self.mAllData):
			self.mAverage /= len(self.mAllData)

	def CountCheck(self):
		x = 0
		i = 0
		# Counts and appends the occurrences of length by group from mMedianArray into countArray
		while x < len(self.mMedianArray):
			countResult = self.mMedianArray.count(i)
			self.mCountArray.append(countResult)
			x += countResult
			i += 1

	def CheckUniqueness(self):
		print("Checking uniques")
		uniquesArray = [self.mAllData[0].name]
		for data in self.mAllData:
			isUnique = True
			for uniques in uniquesArray:
				# Checks if there is at least 1 entry in the uniquesArray that is equal to the name in mAllData
				# If true it will not append the uniquesArray with the name as it's already recorded dus not an unique entry
				if data.name == uniques:
					isUnique = False
					break
			if isUnique:
				uniquesArray.append(data.name)
		self.mUniques = len(uniquesArray)
		print("Uniques:", self.mUniques)

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
				coords = ""
				for i in range(len(allData.pos)):
					coords += str(allData.pos[i].x) + "," + str(allData.pos[i].y) + " "
				data = [allData.id, allData.name, allData.isPolygon, not allData.isSimple, allData.vertices,
				        (allData.area / 1000000.0), (allData.perimeter / 100.0)]
				writer.writerow(data)


if __name__ == "__main__":
	Main = DataHandler()
	Main.CheckData()
