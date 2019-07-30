### Data Cleaning Exercise

##### Requested Function Locations
* The requested function is found in 'src.data_cleaning'
* The test found 'test.test_data_cleaning' performs the data cleaning and checks they are within the specified bounds
* The module 'src.data_utils' contains all the methods I needed due to being restricted to the standard library.   

##### Thought Process
* Since it specified data must be investigated in ascending order, I avoid using forward looking measures, for example using the standard dev and average of the whole data set.
* Therefore the cleaning methods use a rolling window approach or an exponential weighting.

##### Outlier Identification
I used 3 techniques and did multiple passes:
* IQR - inter quartile range
* MAD - Mean absolute deviation
* EWZ - Exponentially weighted Z-Score 
The arguments used  in each method can be found in 'src.data_cleaning'


 
    
