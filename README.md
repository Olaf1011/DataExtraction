## Introduction
In seeking to expand and develop data exploration skills using Python and mathematical problem-solving techniques, it was decided to investigate and study the quality of geographical (lng/lat) plot data.  An opportunity arose whereby a thought experiment could be applied to a data set published by NHS Digital, regarding GP boundaries.
NHS Digital publish GP boundary data at https://digital.nhs.uk/data-and-information/data-collections-and-data-sets/data-collections/general-practice-data-collections , on an annual basis. The website makes clear that the data is of ‘reasonable accuracy’ and that GP’s are required to update when changes occur to their boundaries.  The website also makes users of this public data aware, that it is an exact copy, and no forward cleansing or modification is undertaken.

## Thought Experiment Goal
The goal was to design and build a model that analyses geographical polygon data to determine mathematical properties to derive a sense of quality regarding– shape, area, perimeter length, types, line crossings. See https://en.wikipedia.org/wiki/Polygon for definitions.

## Design Consideration & Libraires Used
The design and checking calls on a number of Python mathematical libraires to evaluate, such as: -
import statistics
import numpy as np
import PlotData as pd
from ground.base import get_context  # https://pypi.org/project/bentley-ottmann/
from bentley_ottmann.planar import contour_self_intersects  # https://pypi.org/project/bentley-ottmann/
from shapely.geometry import Polygon  # https://pypi.org/project/Shapely/
from pyproj import Proj  # https://pyproj4.github.io/pyproj/stable/index.html

## Installation
### Prerequisites
Python 3.7
### Libraries
pip install numpy
pip install matplotlib.pyplot
pip install bentley_ottmann.planar
pip install shapely
pip install pyproj
pip install beautifulsoup


### Source Data
Data File: DecJan-Mar2020.kml downloaded from https://digital.nhs.uk/data-and-information/data-collections-and-data-sets/data-collections/general-practice-data-collections)</br>

### Build, Run, Results – how to
1. Place the "eDecJan-Mar2020.kml" file in the same folder as the python script
2. Run the python script – DataExtration.py
3. Select either "y" or "n" run bentley_ottmann checks ( this takes several mins to run!)
4. Result data is exported as PolygonData.csv for use with Excel

Made by Olaf Oude Reimer and Tom Wells(BSc Mathematics Sheffield Hallam).