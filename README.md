# PBDA
PBDA - Preliminary Big Data Analysis

## Data

Let's start with what is data? In our case, the data is presented as a table with a large number of variables. As my experience (and the previous dataset) tells me, in the end there were 20 variables and 170 thousand rows in the table. 

Preliminary analysis - everything you need to know about the data to set hypotheses and confirm them.

## The first tab of the program is an analysis of what is available

![design1](main.png)
*design*

1) Difference graph with the ability to save (for a variable from the table by choice)
2) Box with whiskers with the ability to save (for a variable from the table by choice)
3) Arithmetic mean, dispersion, range, max value, min value, hyometric mean, harmonic mean, mean square, meldiana, standard deviation, mode (for a variable from the table by choice)

## The second tab of the program is emissions

![[hist]](hist.png)
*design*

1) filter the values, it looks something like this Variable name, maximum possible, minimum possible (by variable)
2)  Difference graph with the ability to save (for a variable from the table by choice)
3) Box with whiskers with the ability to save (for a variable from the table by choice)
4) Arithmetic mean, dispersion, range, max value, min value, hyometric mean, harmonic mean, mean square, meldiana, standard deviation, mode (for a variable from the table by choice)

## Features:

1. Uploading data:
- Uploading CSV files for analysis.
   - Support for processing data with missing values.

2. Data visualization:
- Plotting scattering.
   - Building a box with a mustache.
   - Histogram construction .
   - Color selection for each chart.
   - The ability to hide/display charts using checkboxes.

3. Statistical analysis:
- Calculation and display of the main statistical indicators:
- Mean.
     - Variance.
     - Range.
     - The maximum and minimum values (Max, Min).
     - The Median.
     - Standard Deviation.
     - Fashion (Mode).
     - Geometric Mean.
     - Harmonic Mean.
     - Quadratic mean (QuadraticMean).
4. Emissions analysis:
- Filtering data by specified minimum and maximum values.
   - Updating charts and statistics based on filtered data.

5. Saving graphs:
- Saving graphs (Scatter Plot, Box Plot) in PNG format.

6. Opening charts in a new window:
   - The ability to open charts in a separate window with zoom and navigation support.

7. Multilingual support:
- Supports two languages: English and Russian.
   - Dynamic updating of the interface text when changing the language.

8. Interface:
   - Using a Notebook to split functionality into tabs:
- Tab 1: Basic data analysis.
     - Tab 2: Emissions analysis.
   - Scrollable frames for ease of working with a large number of controls.      

## For the future
1. Plug-ins:
   - Plugin support for adding new functionality without changing the main code.

2. Correlation matrices

3. Machine learning support:
- Adding basic machine learning algorithms (e.g. clustering, regression).

## Installation:

You can download the latest version of the program build from the releases, or install the program yourself, first you need to install the file requiments.txt you can do this using the command: `pip install requiments.txt `
