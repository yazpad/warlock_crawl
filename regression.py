from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor

from sklearn.svm import SVR
from sklearn import datasets

import sqlite3 as sl
from json import loads

from enums import composition
    

#Load dataset
iris = datasets.load_iris()

# print the label species(setosa, versicolor,virginica)
print(iris.target_names)

# print the names of the four features
print(iris.feature_names)

# print the iris data (top 5 records)
print(iris.data[0:5])

# print the iris labels (0:setosa, 1:versicolor, 2:virginica)
print(iris.target)

# print the iris data (top 5 records)
print(iris.data[0:5])

# print the iris labels (0:setosa, 1:versicolor, 2:virginica)
print(iris.target)

# print the iris data (top 5 records)
print(iris.data[0:5])

# print the iris labels (0:setosa, 1:versicolor, 2:virginica)
print(iris.target)

# Creating a DataFrame of given iris dataset.
import pandas as pd
data=pd.DataFrame({
    'sepal length':iris.data[:,0],
    'sepal width':iris.data[:,1],
    'petal length':iris.data[:,2],
    'petal width':iris.data[:,3],
    'species':iris.target
})
data.head()

print(composition.W1_0SP)

# Import train_test_split function
from sklearn.model_selection import train_test_split

X=data[['sepal length', 'sepal width', 'petal length', 'petal width']]  # Features
y=data['species']  # Labels

con = sl.connect('isb.db')

def getTrainingData(boss_id, comp):
    print("Printing db for boss", boss_id)
    X = []
    Y = []
    avg_hit = 0

    def checkEntry(row):
        if len(loads(row[2])) != 1:
            return False
        if len(loads(row[3])) != 0:
            return False
        return True

    with con:
        cursor = con.cursor()
        cursor.execute("SELECT COUNT(*) FROM USER WHERE boss_id == ? and composition == ?", (boss_id, str(comp)))
        num = cursor.fetchone()
        print("There are ", num, "entries")
        data = con.execute("SELECT * FROM USER WHERE boss_id == ? and composition == ?", (boss_id, str(comp)))
        for row in data:
            if not checkEntry(row):
                continue
            # print(row, row[5])
            # time, warlock 1's hit, warlock 1's crit
            # X.append([row[4], loads(row[2])[0]['hit'], loads(row[2])[0]['crit']])
            X.append([loads(row[2])[0]['hit'], loads(row[2])[0]['crit']])
            avg_hit += loads(row[2])[0]['hit']
            if row[5] == -1:
                Y.append(0)
            else:
                Y.append(row[5])
            print(row, len(X), len(Y))

    print(avg_hit/len(Y))
    return X,Y
X,Y = getTrainingData(654, composition.W1_0SP)

# Split dataset into training set and test set
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3) # 70% training and 30% test

from sklearn.gaussian_process.kernels import DotProduct, WhiteKernel
kernel = DotProduct() + WhiteKernel()


from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
degree=2
polyreg=make_pipeline(PolynomialFeatures(degree),LinearRegression())


#Create a Gaussian Classifier
clf=RandomForestRegressor(n_estimators=100)
gpr=GaussianProcessRegressor(kernel=kernel, random_state=0)

#Train the model using the training sets y_pred=clf.predict(X_test)
clf.fit(X_train,y_train)
gpr.fit(X_train,y_train)
polyreg.fit(X_train,y_train)

y_pred=clf.predict(X_test)
print(X_test, y_pred)

#Import scikit-learn metrics module for accuracy calculation
from sklearn import metrics
print('Mean Absolute Error (MAE):', metrics.mean_absolute_error(y_test, y_pred))

# Model Accuracy, how often is the classifier correct?
# print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

import matplotlib.pyplot as plt
import numpy as np

# # Data for plotting
P = []
Z = []
x = []
y = []
for i in range(50):
    P.append([.95, i/100.])
    Z.append([.95, i/100.])
    x.append(i/100.)
    y.append(1-(1-.95*i/100.)**4)

s = clf.predict(P)
z = polyreg.predict(Z)

fig, ax = plt.subplots()
ax.plot(x,s)
ax.plot(x,y)
ax.plot(x,z)

for v in range(len(X)):
    ax.plot(X[v][1],Y[v], '.')


# ax.set(xlabel='time (s)', ylabel='voltage (mV)',
#        title='About as simple as it gets, folks')
# ax.grid()

# fig.savefig("test.png")
plt.show()
