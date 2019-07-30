### Data Cleaning Exercise

##### Requested Function Locations
* The requested function is found in 'src.data_cleaning'
* The test found in 'test.test_data_cleaning' performs the data cleaning and checks whether they are within the specified bounds
* The module 'src.data_utils' contains all the extra methods required without Pandas and Numpy available.   

##### Thought Process
 Data must be investigated in ascending order, so I avoid using forward looking measures, for example using the standard dev and average of the whole data set. As a result the cleaning methods use a rolling window approach or an exponential weighting.


##### Outlier Identification
I used 3 techniques and did multiple passes:
* IQR - inter quartile range
* MAD - Mean absolute deviation
* EWZ - Exponentially weighted Z-Score 

The parameters used for each method can be found in 'src.data_cleaning'


 
    
