import statistics
import io
import xml.etree.ElementTree as xml
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from ground.base import get_context
from bentley_ottmann.planar import contour_self_intersects
import time

class Position(object):
    def __init__(self,pos):
        self.x = pos[0]
        self.y = pos[1]

class ImportedData(object):
    def __init__(self, coords = None, name = None):
        self.pos = []
        for i in range(len(coords)):
            self.pos.append(Position(coords[i].split(",")))

        self.name = name

class DataHandler:
    def __init__(self):
        
        self.mAllData = []
        self.mCountArray = []
        self.mMedianArray = []
        self.mAverage = 0
        self.mMedian = 0
        self.mUpperQaurtile = 0
        self.mLowerQuartile = 0
        self.mQaurtileRange = 0
        self.CalculatedMax = 0
        self.CalculatedMin = 0
        self.THRESHOLD = 10
        #This has to be last!
        self.ExtractData()
        

    def ExtractData(self):
        try:
            #To Do Rename bigData.xml
            #Opens kml(xml) file
            myFile = xml.parse("bigData.kml")
            root = myFile.getroot()

            #look for all instances of coordinats in kml file
            for i  in range(1, len(root[0][0]) - 1):
                #Coordinates ,ODSCode
                self.mAllData.append(ImportedData(root[0][0][i][3][0][0][0].text.split(), root[0][0][i][1][0][0].text))

            self.mHasFile = True

        except:
            print("couldn't open/find klm file.")
            self.mHasFile = False



    def CheckData(self):
        if(not self.mHasFile):
            return
        print("Running..")
        for x in range(len(self.mAllData)):
            #x + 1 (+1 because the lines start at 1) to show which line is incorrect data
            if(self.CheckPolygon(self.mAllData[x].pos)):
                print("Line:", x + 1 , "is not a polygon.")
            self.CheckAverage(self.mAllData[x].pos, x)
            self.AddToMedian(self.mAllData[x].pos);

        self.BentleyOttman();

        #Needs to be outside of the loop because it needs the average amount of items in each element
        self.CheckBelowAverage();
        self.mMedianArray.sort()

        self.Qaurtiles()
        self.CountCheck()

        #self.PrintData()
        self.NumberPolygonGrouping()
        self.PlotData()
    
    def BentleyOttman(self):
        if(input("Are you sure you want to run BentleyOttman? Y/N ").lower() == "n"):
            return
        startTime = time.time() 
        print("Running BentleyOttman..")
        f = open("Bentley_Ottman.txt", "w")
        for i in range(len(self.mAllData)):
            context = get_context()
            point , contour = context.point_cls, context.contour_cls
            tempPolygon = []
            for j in range(len(self.mAllData[i].pos) - 1):
                tempPolygon.append((point(float(self.mAllData[i].pos[j].x), float(self.mAllData[i].pos[j].y))))    

            if(contour_self_intersects(contour(tempPolygon))):
                if(i != 0 and i != len(self.mAllData)):
                    f.write(str("ODSCode of complex polygon: " + self.mAllData[i].name + ". ODSCode of previous: " + self.mAllData[i - 1].name + ". ODSCode of next: " + self.mAllData[i + 1].name + "\n"))
                else:
                    f.write(str("ODSCode of complex polygon: " + self.mAllData[i].name + ". This is either the last or first entry") + "\n")
        
        f.close()
        print("Done Running Bentely Ottman it took %s seconds" % (time.time() - startTime))


    def Qaurtiles(self):
        #Finds the Lower and Upper Quartiles and calculates the Inter Quartile Range 
        self.mMedian = statistics.median(self.mMedianArray)
        self.mLowerQuartile = np.quantile(self.mMedianArray, 0.25)
        self.mUpperQaurtile = np.quantile(self.mMedianArray, 0.75)
        self.mQaurtileRange = self.mUpperQaurtile - self.mLowerQuartile
        self.CalculatedMax = self.mUpperQaurtile + (1.5 * self.mQaurtileRange)
        self.CalculatedMin = self.mLowerQuartile - (1.5 * self.mQaurtileRange)

    def PrintData(self):
        print("Lower Quartile is:" ,self.mLowerQuartile)
        print("Median is:" ,self.mMedian)
        print("Upper Qaurtile is:" ,self.mUpperQaurtile)
        print("Qaurtile Range is:" ,self.mQaurtileRange)
        print("Mode is:" ,statistics.mode(self.mMedianArray))
        

    def NumberPolygonGrouping(self):
        #Uses countArray to display occurences not equal to 0 as a total occurences of polygons  
        for x in range(len(self.mCountArray)):
            if self.mCountArray[x] != 0:
                print("There is", self.mCountArray[x],"occurences of", x,"sided polygons.")

    def AddToMedian(self, lineData):
        self.mMedianArray.append(len(lineData))
           
    def CheckPolygon(self, lineData):
        #Checks how big the array is and picks the integer for the last item in the array
        lastItem = len(lineData) - 1    
        #Checks if the first item and last item are not the same. Meaning it's not a complete polygon.
        return(lineData[0].x != lineData[lastItem].x and lineData[0].y != lineData[lastItem].y)         

    def CheckAverage(self, lineData, i):
        self.mAverage += len(lineData)
        #If it's the last item in the list divide by the total of elements in mAllData[1] 
        if((i + 1) == len(self.mAllData)):
            self.mAverage /=  len(self.mAllData)

    def CountCheck(self):
        x = 0
        i = 0
        #Counts and appends the occurences of length by group from mMedianArray into countArray
        while x < len(self.mMedianArray):
          countResult = self.mMedianArray.count(i)
          self.mCountArray.append(countResult)
          x += countResult
          i += 1

    def CheckBelowAverage(self):

        #Prints the result into a txt file for easier use. (!!Overwrites the previous one with same name!!)
        f = open("AverageResult.txt", "w")

        for x in range(len(self.mAllData)):
            #Checks if the items in element is less than the average amount of items in elements.
            #If true print which element has too little data. 
            #Threshold is to make sure that it isn't a too little difference.
            if(len(self.mAllData[x].pos) < self.mAverage - self.THRESHOLD):
                x = "line: " + str(x) + " has less than " + str(int(self.mAverage)) + " - " + str(self.THRESHOLD) + " data points\n"
                f.write(x)
        f.close()

    def PlotData(self):
        plt.figure()
        bp = plt.boxplot(self.mMedianArray,meanline=True, showmeans=True)
        plt.xticks([1], ['March 2020'])
        plt.xlabel('Polygons cooridnates grouped by year')
        plt.ylabel('Total number of coordinates stored for polygons') 
        plt.title('Spread of total coordinates for all boundry polygons in NHS dataset')
        plt.savefig("Boxplot of total number of points")

        DataPoints = []

        DataPoints.append("Mean is: {:d}".format(int(bp['means'][0].get_ydata()[0])))
        DataPoints.append("Median is: {:d}".format(int(bp['medians'][0].get_ydata()[0])))
        DataPoints.append("Lower Quartile is: {:d}".format(int(bp['boxes'][0].get_ydata()[0])))
        DataPoints.append("Upper Quartile is: {:d}".format(int(bp['boxes'][0].get_ydata()[2])))
        DataPoints.append("Interqaurtile Range is: {:d}".format(int(self.mQaurtileRange)))

        DataPoints.append("Actual Max is: {:d}".format(int(max(self.mMedianArray))))
        DataPoints.append("Calculated Max is: {:d}".format(int(bp['caps'][1].get_ydata()[0])))
        DataPoints.append("Actual Min is: {:d}".format(int(min(self.mMedianArray))))
        DataPoints.append("Calculated Min is: {:d}".format(int(bp['caps'][0].get_ydata()[0])))

        textstr = '\n'.join(DataPoints)
        print(textstr)

        plt.text(1.05, 2000, textstr,horizontalalignment='left',verticalalignment='top', bbox= dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.figure(2)
        plt.hist(self.mMedianArray)
        plt.savefig("Histogram of total number of points")

        tempArrayX = []
        tempArrayY = []
        for i in range(len(self.mCountArray)):
            if(self.mCountArray[i] != 0):
                tempArrayX.append(i)
                tempArrayY.append(self.mCountArray[i])
        print(len(self.mMedianArray))

        
        FirstQ = int(len(tempArrayY)/4)
        SecondQ = FirstQ * 2
        ThirdQ = FirstQ * 3
        FourthQ = len(tempArrayY)

        tempArrayAx = []
        tempArrayAy = []
        tempArrayBx = []
        tempArrayBy = []
        tempArrayCx = []
        tempArrayCy = []
        tempArrayDx = []
        tempArrayDy = []

        for i in range(0 , FirstQ):
            tempArrayAx.append(tempArrayX[i])
            tempArrayAy.append(tempArrayY[i])

        for i in range(FirstQ + 1 , SecondQ):
            tempArrayBx.append(tempArrayX[i])
            tempArrayBy.append(tempArrayY[i])

        for i in range(SecondQ + 1 , ThirdQ):
            tempArrayCx.append(tempArrayX[i])
            tempArrayCy.append(tempArrayY[i])

        for i in range(ThirdQ + 1 , FourthQ):
            tempArrayDx.append(tempArrayX[i])
            tempArrayDy.append(tempArrayY[i])

        plt.figure(3)
        plt.subplot(2,2,1)
        plt.boxplot(tempArrayAx)

        plt.subplot(2,2,2)
        plt.boxplot(tempArrayBx)

        plt.subplot(2,2,3)
        plt.boxplot(tempArrayCx)

        plt.subplot(2,2,4)
        plt.boxplot(tempArrayDx)

        plt.figure(4)
        plt.title('Frequency of total coordinates for all boundry polygons in NHS dataset')
        plt.bar(tempArrayX, tempArrayY)
        plt.savefig("Barchart of total number of points")

        plt.figure(5)
        plt.suptitle('Frequency of total coordinates for all boundry polygons in NHS dataset')

        plt.subplot(2,2,1)
        plt.bar(tempArrayAx, tempArrayAy)
        plt.xlabel('Total number of coordinates stored for polygons')
        plt.ylabel('Frequency') 
        plt.title('0-25% of the data')
        
        plt.subplot(2,2,2)
        plt.bar(tempArrayBx, tempArrayBy)
        plt.xlabel('Total number of coordinates stored for polygons')
        plt.ylabel('Frequency') 
        plt.title('"25%-50% of the data')

        plt.subplot(2,2,3)
        plt.bar(tempArrayCx, tempArrayCy)
        plt.xlabel('Total number of coordinates stored for polygons')
        plt.ylabel('Frequency') 
        plt.title('50%-75% of the data')

        plt.subplot(2,2,4)
        plt.bar(tempArrayDx, tempArrayDy)
        plt.xlabel('Total number of coordinates stored for polygons')
        plt.ylabel('Frequency') 
        plt.title('75%-100% of the data')
             
        plt.show()


def Main():
    Main = DataHandler()
    Main.CheckData();

    print("Done")

if __name__ == "__main__":
    Main()