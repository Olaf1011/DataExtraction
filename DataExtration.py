import statistics
import io
import xml.etree.ElementTree as xml
import numpy as np
import matplotlib.pyplot as plt

class DataHandler:
    def __init__(self):
        self.mAllData = [[],[]]
        self.mAverage = 0
        self.mMedianArray = []
        self.THRESHOLD = 10
        self.ExtractData()
        self.mCountArray = []
        self.mUpperQaurtile = 0
        self.mLowerQuartile = 0
        self.mQaurtileRange = 0

    def ExtractData(self):

        try:
            #To Do Rename bigData.xml
            #Opens kml(xml) file
            myFile = xml.parse("bigData.kml")
            root = myFile.getroot()

            #look for all instances of coordinats in kml file
            for x  in range(1, len(root[0][0]) - 1):
                #ODSCode
                self.mAllData[0].append(root[0][0][x][1][0][0].text)
                #Coordinates
                self.mAllData[1].append(root[0][0][x][3][0][0][0].text.split())
            self.mHasFile = True

        except:
            print("couldn't open/find klm file.")
            self.mHasFile = False



    def CheckData(self):
        if(not self.mHasFile):
            return
        for x in range(len(self.mAllData[1])):
            #x + 1 (+1 because the lines start at 1) to show which line is incorrect data
            if(self.CheckPolygon(self.mAllData[1][x])):
                print("Line:", x + 1 , "is not a polygon.")

            self.CheckAverage(self.mAllData[1][x], x)
            self.AddToMedian(self.mAllData[1][x]);

        #Needs to be outside of the loop because it needs the average amount of items in each element
        self.CheckBelowAverage();
        self.mMedianArray.sort()
        #put quartile ranges after this point THOMAS

        self.Qaurtiles()
        self.CountCheck()

        self.PrintData()
        self.NumberPolygonGrouping()
        self.PlotData()

    def Qaurtiles(self):
        #Finds the Lower and Upper Quartiles and calculates the Inter Quartile Range 
        self.mLowerQuartile = np.quantile(self.mMedianArray, 0.25)
        self.mUpperQaurtile = np.quantile(self.mMedianArray, 0.75)
        self.mQaurtileRange = self.mUpperQaurtile - self.mLowerQuartile
        
    def PrintData(self):
        print("Lower Quartile is:" ,self.mLowerQuartile)
        print("Median is:" ,statistics.median(self.mMedianArray))
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
        return(lineData[0] != lineData[lastItem])         

    def CheckAverage(self, lineData, i):
        self.mAverage += len(lineData)
        #If it's the last item in the list divide by the total of elements in mAllData[1] 
        if((i + 1) == len(self.mAllData[1])):
            self.mAverage /=  len(self.mAllData[1])
            print("Average is:",int(self.mAverage))

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

        for x in range(len(self.mAllData[1])):
            #Checks if the items in element is less than the average amount of items in elements.
            #If true print which element has too little data. 
            #Threshold is to make sure that it isn't a too little difference.
            if(len(self.mAllData[1][x]) < self.mAverage - self.THRESHOLD):
                x = "line: " + str(x) + " has less than " + str(int(self.mAverage)) + " - " + str(self.THRESHOLD) + " data points\n"
                f.write(x)
        f.close()

    def PlotData(self):
        plt.figure(1)
        bp = plt.boxplot(self.mMedianArray,meanline=True, showmeans=True)
        plt.xticks([1], ['mon'])
        plt.savefig("Boxplot of total number of points")
        print(bp['medians'][0].get_ydata())
        print(bp['means'][0].get_ydata())
        print(bp['boxes'][0].get_ydata())
        
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
        plt.bar(tempArrayX, tempArrayY)
        plt.savefig("Barchart of total number of points")

        plt.figure(5)
        plt.subplot(2,2,1)
        plt.bar(tempArrayAx, tempArrayAy)
        
        plt.subplot(2,2,2)
        plt.bar(tempArrayBx, tempArrayBy)

        plt.subplot(2,2,3)
        plt.bar(tempArrayCx, tempArrayCy)

        plt.subplot(2,2,4)
        plt.bar(tempArrayDx, tempArrayDy)
        
              
        plt.show()



Main = DataHandler()
Main.CheckData();

print("Done")

