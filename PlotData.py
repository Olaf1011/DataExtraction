'''Made By Thomas Wells, with help from Olaf Oude Reimer'''

import matplotlib.pyplot as plt

class PlotData(object):
	def __init__(self, medianArray, quartileRange, countArray):
		self.mAllCoordFreqPos = []
		self.mAllCoordFreqEntries = []

		self.mFirstQCoordFreqPos = []
		self.mFirstQCoordFreqEntries = []
		self.mSecondQCoordFreqPos = []
		self.mSecondQCoordFreqEntries = []
		self.mThirdQCoordFreqPos = []
		self.mThirdQCoordFreqEntries = []
		self.mFourthQCoordFreqPos = []
		self.mFourthQCoordFreqEntries = []

		self.mMedianArray = medianArray
		self.mQuartileRange = quartileRange
		self.mCountArray = countArray

		self.FillArray()
		self.Plot()

	def Plot(self):
		self.FigureOne()
		self.FigureTwo()
		self.FigureThree()
		self.FigureFour()
		plt.show()

	def FillArray(self):
		for i in range(len(self.mCountArray)):
			if self.mCountArray[i] != 0:
				self.mAllCoordFreqPos.append(i)
				self.mAllCoordFreqEntries.append(self.mCountArray[i])

		FirstQ = int(len(self.mAllCoordFreqEntries) / 4)
		SecondQ = FirstQ * 2
		ThirdQ = FirstQ * 3
		FourthQ = len(self.mAllCoordFreqEntries)

		for i in range(0, FirstQ):
			self.mFirstQCoordFreqPos.append(self.mAllCoordFreqPos[i])
			self.mFirstQCoordFreqEntries.append(self.mAllCoordFreqEntries[i])

		for i in range(FirstQ + 1, SecondQ):
			self.mSecondQCoordFreqPos.append(self.mAllCoordFreqPos[i])
			self.mSecondQCoordFreqEntries.append(self.mAllCoordFreqEntries[i])

		for i in range(SecondQ + 1, ThirdQ):
			self.mThirdQCoordFreqPos.append(self.mAllCoordFreqPos[i])
			self.mThirdQCoordFreqEntries.append(self.mAllCoordFreqEntries[i])

		for i in range(ThirdQ + 1, FourthQ):
			self.mFourthQCoordFreqPos.append(self.mAllCoordFreqPos[i])
			self.mFourthQCoordFreqEntries.append(self.mAllCoordFreqEntries[i])

	def FigureOne(self):
		plt.figure()
		bp = plt.boxplot(self.mMedianArray, meanline=True, showmeans=True)
		plt.xticks([1], ['March 2020'])
		plt.xlabel('Polygons coordinates grouped by year')
		plt.ylabel('Total number of coordinates stored for polygons')
		plt.title('Spread of total coordinates for all boundary polygons in NHS dataset')
		plt.savefig("Boxplot of total number of points")

		DataPoints = ["Mean is: {:d}".format(int(bp['means'][0].get_ydata()[0])),
		              "Median is: {:d}".format(int(bp['medians'][0].get_ydata()[0])),
		              "Lower Quartile is: {:d}".format(int(bp['boxes'][0].get_ydata()[0])),
		              "Upper Quartile is: {:d}".format(int(bp['boxes'][0].get_ydata()[2])),
		              "Inter quartile Range is: {:d}".format(int(self.mQuartileRange)),
		              "Actual Max is: {:d}".format(int(max(self.mMedianArray))),
		              "Calculated Max is: {:d}".format(int(bp['caps'][1].get_ydata()[0])),
		              "Actual Min is: {:d}".format(int(min(self.mMedianArray))),
		              "Calculated Min is: {:d}".format(int(bp['caps'][0].get_ydata()[0]))]

		textstr = '\n'.join(DataPoints)
		print(textstr)

		plt.text(1.05, 2000, textstr, horizontalalignment='left', verticalalignment='top',
		         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

	def FigureTwo(self):
		plt.figure(2)
		plt.hist(self.mMedianArray)
		plt.savefig("Histogram of total number of points")

	def FigureThree(self):
		plt.figure(3)
		plt.title('Frequency of total coordinates for all boundary polygons in NHS dataset')
		plt.bar(self.mAllCoordFreqPos, self.mAllCoordFreqEntries)
		plt.xlabel('Total number of coordinates stored for polygons')
		plt.ylabel('Frequency')
		plt.savefig("Barchart of total number of points")

	def FigureFour(self):
		plt.figure(4)
		plt.suptitle('Frequency of total coordinates for all boundary polygons in NHS dataset')

		plt.subplot(2, 2, 1)
		plt.bar(self.mFirstQCoordFreqPos, self.mFirstQCoordFreqEntries)
		plt.xlabel('Total number of coordinates stored for polygons')
		plt.ylabel('Frequency')
		plt.title('0-25% of the data')

		plt.subplot(2, 2, 2)
		plt.bar(self.mSecondQCoordFreqPos, self.mSecondQCoordFreqEntries)
		plt.xlabel('Total number of coordinates stored for polygons')
		plt.ylabel('Frequency')
		plt.title('25%-50% of the data')

		plt.subplot(2, 2, 3)
		plt.bar(self.mThirdQCoordFreqPos, self.mThirdQCoordFreqEntries)
		plt.xlabel('Total number of coordinates stored for polygons')
		plt.ylabel('Frequency')
		plt.title('50%-75% of the data')

		plt.subplot(2, 2, 4)
		plt.bar(self.mFourthQCoordFreqPos, self.mFourthQCoordFreqEntries)
		plt.xlabel('Total number of coordinates stored for polygons')
		plt.ylabel('Frequency')
		plt.title('75%-100% of the data')

		plt.savefig("Four quarter Barchart of total number of points")
