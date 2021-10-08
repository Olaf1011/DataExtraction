import statistics
import io
import xml.etree.ElementTree as xml
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

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
        #try:
            #To Do Rename bigData.xml
            #Opens kml(xml) file
            myFile = xml.parse("bigData.kml")
            root = myFile.getroot()

            #look for all instances of coordinats in kml file
            for i  in range(1, len(root[0][0]) - 1):
                #Coordinates ,ODSCode
                self.mAllData.append(ImportedData(root[0][0][i][3][0][0][0].text.split(), root[0][0][i][1][0][0].text))

            self.mHasFile = True

        #except:
        #    print("couldn't open/find klm file.")
        #    self.mHasFile = False



    def CheckData(self):
        if(not self.mHasFile):
            return
        for x in range(len(self.mAllData)):
            #x + 1 (+1 because the lines start at 1) to show which line is incorrect data
            if(self.CheckPolygon(self.mAllData[x].pos)):
                print("Line:", x + 1 , "is not a polygon.")

            self.CheckAverage(self.mAllData[x].pos, x)
            self.AddToMedian(self.mAllData[x].pos);

        #Needs to be outside of the loop because it needs the average amount of items in each element
        self.CheckBelowAverage();
        self.mMedianArray.sort()
        #put quartile ranges after this point THOMAS

        self.Qaurtiles()
        self.CountCheck()

        #self.PrintData()
        #self.NumberPolygonGrouping()
        self.PlotData()

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
        plt.figure(1)
        #plt.subplot()
        bp = plt.boxplot(self.mMedianArray,meanline=True, showmeans=True)
        plt.xticks([1], ['mon'])
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

        ## build a rectangle in axes coords
        #left, width = .25, .5
        #bottom, height = .25, .5
        #right = left + width
        #top = bottom + height
        #fig = plt.figure()
        bp.add_axes([0, 0, 0.1, 0.1])
        ## axes coordinates: (0, 0) is bottom left and (1, 1) is upper right
        #p = patches.Rectangle((left, bottom), width, height,fill=False, transform=ax.transAxes, clip_on=False)
        #ax.add_patch(p)

        #ax.text(right, top, 'right bottom',horizontalalignment='right',verticalalignment='top',transform=ax.transAxes)

        plt.text(.75, .75, textstr,horizontalalignment='right',verticalalignment='top', transform = bp.transAxes)

        
        

        #plt.figure(3)
        #plt.hist(self.mMedianArray)
        #plt.savefig("Histogram of total number of points")


        #tempArrayX = []
        #tempArrayY = []
        #for i in range(len(self.mCountArray)):
        #    if(self.mCountArray[i] != 0):
        #        tempArrayX.append(i)
        #        tempArrayY.append(self.mCountArray[i])
        #print(len(self.mMedianArray))

        
        #FirstQ = int(len(tempArrayY)/4)
        #SecondQ = FirstQ * 2
        #ThirdQ = FirstQ * 3
        #FourthQ = len(tempArrayY)

        #tempArrayAx = []
        #tempArrayAy = []
        #tempArrayBx = []
        #tempArrayBy = []
        #tempArrayCx = []
        #tempArrayCy = []
        #tempArrayDx = []
        #tempArrayDy = []

        #for i in range(0 , FirstQ):
        #    tempArrayAx.append(tempArrayX[i])
        #    tempArrayAy.append(tempArrayY[i])

        #for i in range(FirstQ + 1 , SecondQ):
        #    tempArrayBx.append(tempArrayX[i])
        #    tempArrayBy.append(tempArrayY[i])

        #for i in range(SecondQ + 1 , ThirdQ):
        #    tempArrayCx.append(tempArrayX[i])
        #    tempArrayCy.append(tempArrayY[i])

        #for i in range(ThirdQ + 1 , FourthQ):
        #    tempArrayDx.append(tempArrayX[i])
        #    tempArrayDy.append(tempArrayY[i])

        #plt.figure(3)
        #plt.subplot(2,2,1)
        #plt.boxplot(tempArrayAx)

        #plt.subplot(2,2,2)
        #plt.boxplot(tempArrayBx)

        #plt.subplot(2,2,3)
        #plt.boxplot(tempArrayCx)

        #plt.subplot(2,2,4)
        #plt.boxplot(tempArrayDx)

        #plt.figure(4)
        #plt.bar(tempArrayX, tempArrayY)
        #plt.savefig("Barchart of total number of points")

        #plt.figure(5)
        #plt.subplot(2,2,1)
        #plt.bar(tempArrayAx, tempArrayAy)
        
        #plt.subplot(2,2,2)
        #plt.bar(tempArrayBx, tempArrayBy)

        #plt.subplot(2,2,3)
        #plt.bar(tempArrayCx, tempArrayCy)

        #plt.subplot(2,2,4)
        #plt.bar(tempArrayDx, tempArrayDy)
        
              
        plt.show()



Main = DataHandler()
Main.CheckData();

print("Done")

#from ground.base import get_context
#from bentley_ottmann.planar import contour_self_intersects

#context = get_context()
#Point, segment = context.point_cls, context.segment_cls
##unit_segments = [segment(point(0, 0), point(1, 2)), 
##                 segment(point(1, 2), point(2, 0)),
##                 segment(point(2, 0), point(0,0))]

#arrayTomBeingACunt = ["0,0","1,0","0,1"]
#arrayTomBeingACuntB = [arrayTomBeingACunt[0].split(","),arrayTomBeingACunt[1].split(","),arrayTomBeingACunt[2].split(",")]

#Contour = context.contour_cls

##complexPolygonT = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])

#complexPolygonT = Contour([Point(arrayTomBeingACuntB[0][0],arrayTomBeingACuntB[0][1]), Point(arrayTomBeingACuntB[1][0],arrayTomBeingACuntB[1][1]), Point(arrayTomBeingACuntB[2][0],arrayTomBeingACuntB[2][1])])
#complexPolygonC = Contour([Point(0, 0), Point(1, 0), Point(0, 1), Point(1,1)])
#complexPolygonS = Contour([Point(0, 0), Point(1, 0), Point(1, 1), Point(0,1)])

#print(contour_self_intersects(complexPolygonT))
#print(contour_self_intersects(complexPolygonC))
#print(contour_self_intersects(complexPolygonS))