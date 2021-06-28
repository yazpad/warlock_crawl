from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor

from sklearn.svm import SVR
from sklearn import datasets

import sqlite3 as sl
from json import loads

from enums import composition, compToNum
from itertools import permutations
    

COMP = composition.W4_1SP

# Import train_test_split function
from sklearn.model_selection import train_test_split
con = sl.connect('isb.db')

def checkEntry(row, comp):
    if comp == str(composition.W1_0SP):
        if len(loads(row[2])) != 1:
            return False
        if len(loads(row[3])) != 0:
            return False
    elif comp == str(composition.W2_0SP):
        if len(loads(row[2])) != 2:
            return False
        if len(loads(row[3])) != 0:
            return False
    elif comp == str(composition.W1_1SP):
        if len(loads(row[2])) != 1:
            return False
        if len(loads(row[3])) != 1:
            return False
    elif comp == str(composition.W2_1SP):
        if len(loads(row[2])) != 2:
            return False
        if len(loads(row[3])) != 1:
            return False
    elif comp == str(composition.W3_1SP):
        if len(loads(row[2])) != 3:
            return False
        if len(loads(row[3])) != 1:
            return False
    elif comp == str(composition.W4_1SP):
        if len(loads(row[2])) != 4:
            return False
        if len(loads(row[3])) != 1:
            return False
    elif comp == str(composition.W5_1SP):
        if len(loads(row[2])) != 5:
            return False
        if len(loads(row[3])) != 1:
            return False
    elif comp == str(composition.W1_2SP):
        if len(loads(row[2])) != 1:
            return False
        if len(loads(row[3])) != 2:
            return False
    elif comp == str(composition.W2_2SP):
        if len(loads(row[2])) != 2:
            return False
        if len(loads(row[3])) != 2:
            return False
    elif comp == str(composition.W3_2SP):
        if len(loads(row[2])) != 3:
            return False
        if len(loads(row[3])) != 2:
            return False
    elif comp == str(composition.W4_2SP):
        if len(loads(row[2])) != 4:
            return False
        if len(loads(row[3])) != 2:
            return False
    elif comp == str(composition.W5_2SP):
        if len(loads(row[2])) != 5:
            return False
        if len(loads(row[3])) != 2:
            return False
    elif comp == str(composition.W1_3SP):
        if len(loads(row[2])) != 1:
            return False
        if len(loads(row[3])) != 3:
            return False
    elif comp == str(composition.W2_3SP):
        if len(loads(row[2])) != 2:
            return False
        if len(loads(row[3])) != 3:
            return False
    elif comp == str(composition.W3_3SP):
        if len(loads(row[2])) != 3:
            return False
        if len(loads(row[3])) != 3:
            return False
    elif comp == str(composition.W4_3SP):
        if len(loads(row[2])) != 4:
            return False
        if len(loads(row[3])) != 3:
            return False
    elif comp == str(composition.W5_3SP):
        if len(loads(row[2])) != 5:
            return False
        if len(loads(row[3])) != 3:
            return False
    else:
        return False
    return True

def getAllData(boss_id):
    data_for_size = {1 : {"X": [], "Y": []},
                     2 : {"X": [], "Y": []},
                     3 : {"X": [], "Y": []},
                     4 : {"X": [], "Y": []},
                     5 : {"X": [], "Y": []},
                     6 : {"X": [], "Y": []},
                     7 : {"X": [], "Y": []},
                     8 : {"X": [], "Y": []}}

    permute_init = {}
    for i in range(8):
        permute_init[i] = []
        for j in range(i):
            permute_init[i].append(j)

    spec_defs = {'shadow': 0, 'affliction': .33, 'demonology': .66, 'destruction': 1.0}

    with con:
        cursor = con.cursor()
        cursor.execute("SELECT COUNT(*) FROM USER WHERE boss_id == ?", (boss_id,))
        num = cursor.fetchone()
        print("There are ", num, "entries")
        data = con.execute("SELECT * FROM USER WHERE boss_id == ?", (boss_id,))
        for row in data:
            comp = str(row[1])
            num_players = compToNum(comp)
            print(row, comp, num_players)

            order = []
            #Num locks
            warlock_info = loads(row[2])
            priest_info = loads(row[3])
            for i in range(len(warlock_info)):
                if warlock_info[i].get('spec') is None:
                    warlock_info[i]['spec'] = "destruction"
                order.append((spec_defs[warlock_info[i]['spec']], warlock_info[i]['hit'], warlock_info[i]['crit']))
            for i in range(len(priest_info)):
                if priest_info[i].get('spec') is None:
                    priest_info[i]['spec'] = "shadow"
                order.append((spec_defs[priest_info[i]['spec']], priest_info[i]['hit'], 0))

            if not checkEntry(row,comp):
                continue
            # print(row, row[5])
            # time, warlock 1's hit, warlock 1's crit
            for perm in list(permutations(permute_init[num_players])):
                data_for_size[num_players]['X'].append([row[4]])
                if row[5] == -1:
                    data_for_size[num_players]['Y'].append(0)
                else:
                    data_for_size[num_players]['Y'].append(row[5])
                for i in perm:
                    for val in order[i]:
                        data_for_size[num_players]['X'][-1].append(val)

        return data_for_size

data_by_size = getAllData(654)
rfr_by_size = {}
poly_regressor_by_size = {}

#Import scikit-learn metrics module for accuracy calculation
from sklearn import metrics
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression

for i in range(1,9):
    if len(data_by_size[i]['X']) == 0:
        continue
    rfr_by_size[i]=RandomForestRegressor(n_estimators=30)
    poly_regressor_by_size[i]= {"features": PolynomialFeatures(degree=2), "regressor": LinearRegression(fit_intercept=False)}

    X_train, X_test, y_train, y_test = train_test_split(data_by_size[i]['X'], data_by_size[i]['Y'], test_size=0.2) # 70% training and 30% test
    rfr_by_size[i].fit(X_train,y_train)
    rfr_by_size[i].fit(X_train,y_train)

    X_train_poly = poly_regressor_by_size[i]['features'].fit_transform(X_train)
    poly_regressor_by_size[i]['regressor'].fit(X_train_poly, y_train)

    y_pred=rfr_by_size[i].predict(X_test)
    y_pred_poly=poly_regressor_by_size[i]['regressor'].predict(poly_regressor_by_size[i]['features'].fit_transform(X_test))

    print(len(X_test))
    #for k in range(len(X_test)):
    #    print(X_test[k], y_pred[k])
    print('Mean Absolute Error (MAE) for RFR:', metrics.mean_absolute_error(y_test, y_pred), "num warlocks", i)
    print('Mean Absolute Error (MAE) for polyreg:', metrics.mean_absolute_error(y_test, y_pred_poly), "num warlocks", i)

def genCritDataFromNum(i, num_locks, num_priests):
    if num_locks == 1:
        if num_priests == 0:
            return [95, 1.0, .94, i/100.]
        if num_priests == 1:
            return [95, 1.0, .94, i/100., 0.0, .94, 0]
    if num_locks == 2:
        if num_priests == 0:
            return [95, 1.0, .94, i/100., 1.0, .94, i/100.]
        if num_priests == 1:
            return [95, 1.0, .94, i/100., 1.0, .94, .25, 0.0, .94, 0.0]


# # Data for plotting

import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots()

def plotReg(num_locks, num_priests):
    P = []
    Z = []
    x = []
    y = []
    for i in range(50):
        P.append(genCritDataFromNum(i, num_locks, num_priests))
        Z.append(genCritDataFromNum(i, num_locks, num_priests))
        x.append(i/100.)
        y.append(1-(1-.95*i/100.)**4)

    s = rfr_by_size[num_locks+num_priests].predict(P)

    z = poly_regressor_by_size[num_locks+num_priests]['regressor'].predict(poly_regressor_by_size[num_locks+num_priests]['features'].fit_transform(Z))

    ax.plot(x,s, label="random forest regressor, " + str(num_locks)+"W - " + str(num_priests)+"SP")
    ax.plot(x,z, label="polynomial regressor, " + str(num_locks)+"W - " + str(num_priests)+"SP")
    ax.plot(x,y, label="binomial distribution, " + str(num_locks)+"W - " + str(num_priests)+"SP")



plotReg(1, 0)
plotReg(1, 1)
#plotReg(2, 0)

for v in range(len(data_by_size[1]['X'])):
    ax.plot(data_by_size[1]['X'][v][3],data_by_size[1]['Y'][v], '.')

ax.legend()
ax.set_xlim([0,.6])
ax.set_ylim([0,1.0])
ax.set_title("ISB uptime vs Crit\n Composition=1 Warlock, Hit=.94, Time=.95, Boss=Maiden of Virtue")
ax.set_ylabel("ISB Uptime")
ax.set_xlabel("Crit rate")
plt.grid()

plt.show()
exit()

def getTrainingData(boss_id, comp):
    print("Printing db for boss", boss_id)
    X = []
    Y = []
    avg_hit = 0

    def checkEntry(row, comp):
        if comp == composition.W1_0SP:
            if len(loads(row[2])) != 1:
                return False
            if len(loads(row[3])) != 0:
                return False
        elif comp == composition.W2_0SP:
            if len(loads(row[2])) != 2:
                return False
            if len(loads(row[3])) != 0:
                return False
        elif comp == composition.W1_1SP:
            if len(loads(row[2])) != 1:
                return False
            if len(loads(row[3])) != 1:
                return False
        else:
            return False
        return True

    with con:
        cursor = con.cursor()
        cursor.execute("SELECT COUNT(*) FROM USER WHERE boss_id == ? and composition == ?", (boss_id, str(comp)))
        num = cursor.fetchone()
        print("There are ", num, "entries")
        data = con.execute("SELECT * FROM USER WHERE boss_id == ? and composition == ?", (boss_id, str(comp)))
        #Inject 0 intercept data
        for k in range(1,9):
            for g in [0,.33,.66,1.0]:
                for i in range(0,100,10):
                    X.append([i])
                    for j in range(k):
                        X[-1].append([g,0,0])

        for row in data:
            if not checkEntry(row,comp):
                continue
            # print(row, row[5])
            # time, warlock 1's hit, warlock 1's crit
            X.append([row[4]])
            for i in range(len(loads(row[2]))):
                X[-1].append(loads(row[2])[i]['hit'])
                X[-1].append(loads(row[2])[i]['crit'])
            for i in range(len(loads(row[3]))):
                X[-1].append(loads(row[3])[i]['hit'])
            # X.append([row[4], loads(row[2])[0]['hit'], loads(row[2])[0]['crit']])
            #X.append([loads(row[2])[0]['hit'], loads(row[2])[0]['crit']])
            avg_hit += loads(row[2])[0]['hit']
            if row[5] == -1:
                Y.append(0)
            else:
                Y.append(row[5])
            if row[5] < .1:
                print(row, len(X), len(Y))

    print(avg_hit/len(Y))
    return X,Y
X,Y = getTrainingData(661, COMP)

# Split dataset into training set and test set
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2) # 70% training and 30% test

from sklearn.gaussian_process.kernels import DotProduct, WhiteKernel
kernel = DotProduct() + WhiteKernel()


from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
degree=2

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
polyreg=make_pipeline(scaler,PolynomialFeatures(degree),LinearRegression())

poly = PolynomialFeatures(degree=2)

polyreg = LinearRegression(fit_intercept=True)


from sklearn.neural_network import MLPRegressor


#Create a Gaussian Classifier
clf=RandomForestRegressor(n_estimators=30, max_features=2)
# clf=MLPRegressor(random_state=1, alpha=.001, max_iter=100, hidden_layer_sizes=5, solver='sgd')
# clf = make_pipeline(StandardScaler(), SVR(kernel="poly", degree=2))
gpr=GaussianProcessRegressor(kernel=kernel, random_state=0)

#Train the model using the training sets y_pred=clf.predict(X_test)
clf.fit(X_train,y_train)
gpr.fit(X_train,y_train)
# polyreg.fit(X_train,y_train)

X_train_ = poly.fit_transform(X_train)
polyreg.fit(X_train_,y_train)

y_pred=clf.predict(X_test)

X_test_ = poly.fit_transform(X_test)
y_pred2=polyreg.predict(X_test_)
print(X_test, y_pred)

print('Mean Absolute Error (MAE):', metrics.mean_absolute_error(y_test, y_pred2))

# Model Accuracy, how often is the classifier correct?
# print("Accuracy:",metrics.accuracy_score(y_test, y_pred))

import matplotlib.pyplot as plt
import numpy as np

def genCritData(i, comp):
    if comp == composition.W1_0SP:
        return [95, .94, i/100.]
    elif comp == composition.W1_1SP:
        return [95, .94, i/100., .95]

def genCritDataFromNum(i, num):
    if num == 1:
        return [95, 1.0, .94, i/100.]


fig, ax = plt.subplots()

def plotReg(num):
    # # Data for plotting
    P = []
    Z = []
    x = []
    y = []
    for i in range(50):
        P.append(genCritData(i, COMP))
        Z.append(genCritData(i, COMP))
        x.append(i/100.)
        y.append(1-(1-.95*i/100.)**4)

    s = clf.predict(P)

    Z = poly.fit_transform(Z)
    z = polyreg.predict(Z)

    ax.plot(x,s)
    ax.plot(x,y)
    ax.plot(x,z)


# # Data for plotting
P = []
Z = []
x = []
y = []
for i in range(50):
    P.append(genCritData(i, COMP))
    Z.append(genCritData(i, COMP))
    x.append(i/100.)
    y.append(1-(1-.95*i/100.)**4)

s = clf.predict(P)
Z = poly.fit_transform(Z)
z = polyreg.predict(Z)

ax.plot(x,s)
ax.plot(x,y)
ax.plot(x,z)

for v in range(len(X)):
    ax.plot(X[v][2],Y[v], '.')


# ax.set(xlabel='time (s)', ylabel='voltage (mV)',
#        title='About as simple as it gets, folks')
# ax.grid()
coefs = polyreg.coef_
powers = poly.powers_

sample_x = [genCritData(25, COMP)]
ans = 0 
txt = "="
coef_dict = {composition.W1_0SP : {0 : "cTime", 1 : "cHit", 2: "cCrit"},
             composition.W1_1SP : {0 : "cTime", 1 : "WONEcHit", 2: "WONEcCrit", 3 : "SPONEcHit"}}
print(coefs)
for p in range(len(powers)):
    v = coefs[p]
    txt+= str(coefs[p])
    for j in range(len(powers[p])):
        for k in range(powers[p][j]):
            txt+= "*" + coef_dict[COMP][j]
            v *= sample_x[0][j]
    ans += v
    if p != len(powers) - 1:
        txt += "+" 
print(txt)

print(sample_x)
sample_x = poly.fit_transform(sample_x)
print(ans, polyreg.predict(sample_x))
print(clf.estimators_[0].tree_.threshold[i], clf.estimators_[0].tree_.feature[i],  clf.estimators_[0].tree_.value[i])

def calculateTree(tree, node, inp):
    if tree.children_left[node] == -1:
        return tree.value[node]
    else:
        if inp[tree.feature[node]] <= tree.threshold[node]:
            return calculateTree(tree, tree.children_left[node], inp )
        else:
            return calculateTree(tree, tree.children_right[node], inp)

def printTree(tree, node, txt):
    if tree.children_left[node] == -1:
        txt[0]+=str(tree.value[node][0][0])
        return
    else:
        txt[0]+=str("IF(")+coef_dict[COMP][tree.feature[node]]+"<="+str(tree.threshold[node])+","
        printTree(tree, tree.children_left[node], txt)
        txt[0]+=","
        printTree(tree, tree.children_right[node], txt)
        txt[0]+=")"

sample_x = genCritData(25, COMP)
num = 0
avg = 0
txt = [""]
print(len(clf.estimators_))
for tree in clf.estimators_:
    txt[0] +="="
    num += 1
    avg += calculateTree(tree.tree_, 0,  sample_x)[0]
    printTree(tree.tree_, 0,  txt)

    txt[0] += "|"

print(avg/num, clf.predict([sample_x]))
print(txt)


# fig.savefig("test.png")
# print(polyreg.get_params()['linearregression'].coef_)
# print(polyreg.get_params()['polynomialfeatures'].powers_)


plt.show()
