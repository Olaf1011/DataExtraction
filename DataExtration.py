import statistics
import xml.etree.ElementTree as xml

class DataHandler:
    def __init__(self):
        self.mAllData = [[],[]]
        self.mAverage = 0
        self.mMedianArray = []
        self.THRESHOLD = 10
        self.ExtractData()

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
        except:
            print("couldn't open/find klm file")


    def CheckData(self):
        for x in range(len(self.mAllData[1])):
            #x + 1 (+1 because the lines start at 1) to show which line is incorrect data
            if(self.CheckPolygon(self.mAllData[1][x])):
                print("Line:", x + 1 , "is not a polygon")

            self.CheckAverage(self.mAllData[1][x], x)
            self.AddToMedian(self.mAllData[1][x]);
        #Needs to be outside of the loop because it needs the average amount of items in each element
        self.CheckBelowAverage();
        self.mMedianArray.sort()
        
        print("Median is:" ,statistics.median(self.mMedianArray))
        print("Mode is:" ,statistics.mode(self.mMedianArray))


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


    

Main = DataHandler()
Main.CheckData();
print("Done")
