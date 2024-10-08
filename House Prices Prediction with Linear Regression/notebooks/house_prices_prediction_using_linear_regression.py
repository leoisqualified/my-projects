# -*- coding: utf-8 -*-
"""House prices prediction using Linear Regression.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1SyQ7pDbax4xwtdZHnDLV_mc-cT1nXa7N
"""

'''
In this notebook we are going to predict the price of house given their square footage and number of bedrooms and bathrooms using linear regression models

'''

#import the libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import PolynomialFeatures

#load the train dataset
pd.set_option('display.max_columns', None)
train = pd.read_csv('/content/train.csv')

#check the dataset
train.head()

"""# Data Cleaning & Validation"""

'''
We will check the number of columns we have in our dataset to se the relevant columns we have to work with.
We will begin with data cleaning and validation. Then we will check for outliers and then check the relationship between these relevant columns.
'''

#check the columns
train.columns

#check the data
train.info()

'''
From the above data we see we have a lot of features and some missing values as well.
Per our objective we need to find the sale price of the house given the number of bathroom and bedrooms as well as their.
Beforw we continue we would like to see the relationship between all these features.
'''

#include columns of integer type
train_sub = train.select_dtypes(include=['int64'])

#check the correlation
plt.figure(figsize=(30,30))
sns.heatmap(train_sub.corr(), annot=True)

#show the plot
plt.show()

'''
The dataset visualization looks too overwhelming to look at.
We will subset our data to the relevants features to meet our projects objective. Per the metadata, we have Basement Half Bathrooms (BsmtHalfBath),
Basement Full Bathrooms (BsmtFullBath), FullBath, HalfBath we will find the total number of these features, subset the dataset for our work and then
check the correlation again.
'''

"""# Feature Engineering & Preprocessing"""

#sum the bathrooms
train_sub['TotalBath'] = train_sub['BsmtFullBath'] + train_sub['BsmtHalfBath'] + train_sub['FullBath'] + train_sub['HalfBath']

#subset the data
train_final = train_sub[['LotArea','TotalBath','BedroomAbvGr','SalePrice']]

#check the correlation
plt.figure(figsize=(10,10))
sns.heatmap(train_final.corr(), annot=True)

#show the plot
plt.show()

'''
From the above we see that TotalBath has a good correlation with SalePrice the other two features have a weak correlation but positive
this could also influence our predictions positively.
We will check the relationship and distribution of these features further
'''

#check the distribution
for column in train_final.columns:
  plt.figure(figsize=(10,10))

  #plot the distribution
  sns.distplot(train_final[column])

  #set the title
  plt.title(f'Distribution of {column.capitalize()}')

  #show the plot
  plt.show()

'''
From the plots we see that LotArea and SalePrice are skewed to the right. This indicates the presence of outliers
we will assert this claim with a boxplot and then cap outliers in our data since they could cause our model to predict
wrong results.
'''

for column in train_final.columns:
  plt.figure(figsize=(10,10))

  #plot the boxplot
  sns.boxplot(train_final[column])

  #set the title
  plt.title(f'Boxplot of {column.capitalize()}')

  #show the plot
  plt.show()

'''
We see that we have outliers in all features of our data. We will cap the outliers in data using interquartile range
'''

"""# Handling Outliers"""

# Step 1: Define the IQR for each column
Q1_saleprice = train_final['SalePrice'].quantile(0.25)  # 25th percentile (Q1)
Q3_saleprice = train_final['SalePrice'].quantile(0.75)  # 75th percentile (Q3)
IQR_saleprice = Q3_saleprice - Q1_saleprice  # IQR for SalePrice

Q1_lotarea = train_final['LotArea'].quantile(0.25)  # 25th percentile (Q1)
Q3_lotarea = train_final['LotArea'].quantile(0.75)  # 75th percentile (Q3)
IQR_lotarea = Q3_lotarea - Q1_lotarea  # IQR for LotArea

# Step 2: Define the bounds for outliers
lower_bound_saleprice = Q1_saleprice - 1.5 * IQR_saleprice  # Lower bound for SalePrice
upper_bound_saleprice = Q3_saleprice + 1.5 * IQR_saleprice  # Upper bound for SalePrice

lower_bound_lotarea = Q1_lotarea - 1.5 * IQR_lotarea  # Lower bound for LotArea
upper_bound_lotarea = Q3_lotarea + 1.5 * IQR_lotarea  # Upper bound for LotArea

# Step 3: Remove outliers for both 'SalePrice' and 'LotArea'
# Keep only rows that are within the bounds for both 'SalePrice' and 'LotArea'
train_final_filtered = train_final[
    (train_final['SalePrice'] >= lower_bound_saleprice) & (train_final['SalePrice'] <= upper_bound_saleprice) &
    (train_final['LotArea'] >= lower_bound_lotarea) & (train_final['LotArea'] <= upper_bound_lotarea)
]

# Optional: Check how many rows were removed
print(f"Original data shape: {train_final.shape}")
print(f"Filtered data shape: {train_final_filtered.shape}")

# Now you can use 'train_final_filtered' for further analysis/modeling
train_final_filtered.head()

#check the relationship
sns.pairplot(train_final)

#show the plot
plt.show()

#check the data
train_final_filtered.describe()

'''
  We have handled the outliers that can affect the models ability to generalise on unseen data.
  We will build our model
'''

"""# Model Training & Evaluation"""

#instantiate the model
lin_reg = LinearRegression()

#split the data
X = train_final_filtered[['LotArea','TotalBath','BedroomAbvGr']]
y = train_final_filtered['SalePrice']

#fit the model
lin_reg.fit(X, y)

#evaluate the model
print(f'R2 Score: {r2_score(y, lin_reg.predict(X))}')
print(f'MSE: {mean_squared_error(y, lin_reg.predict(X))}')

'''
We had a poor performance on our model because the relationship between these features is not so linear
We will try to make the relationship by linear by applying polynomial features
'''

#apply polynomial features
poly = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
X_poly = poly.fit_transform(X)

#fit the model
lin_reg.fit(X_poly, y)

#evaluate the model
print(f'R2 Score: {r2_score(y, lin_reg.predict(X_poly))}')
print(f'RMSE: {np.sqrt(mean_squared_error(y, lin_reg.predict(X_poly)))}')

#read the test data
test = pd.read_csv('/content/test.csv')

#add the bathroom
test['TotalBath'] = test['BsmtFullBath'] + test['BsmtHalfBath'] + test['FullBath'] + test['HalfBath']

#subset the data
test_final = test[['LotArea','TotalBath','BedroomAbvGr']]

'''
Model predicts with a fairly good R2 score given the relationship between our features is not so linear.
We will now use the model to predict on the test data
'''

#read the test data
test = pd.read_csv('/content/test.csv')

#add the bathrooms
test['TotalBath'] = test['BsmtFullBath'] + test['BsmtHalfBath'] + test['FullBath'] + test['HalfBath']

#subset the data
test_final = test[['LotArea','TotalBath','BedroomAbvGr']]

# Impute missing values in test_final
!pip install sklearn
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy='median') # Use the same strategy as your training data
test_final = imputer.fit_transform(test_final)

#apply polynomial features - this should be done after imputation to avoid errors
poly = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
test_final = poly.fit_transform(test_final)

#predict the saleprice
predictions = lin_reg.predict(test_final)

#save the data
submission = pd.DataFrame(predictions).to_csv('submission.csv', index=False)

#check the submission
!head submission.csv

#end of notebook