from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn import preprocessing


from sklearn.svm import SVR
from sklearn import datasets

import sqlite3 as sl
from json import loads

from enums import composition, compToNum
from itertools import permutations
import random
    

COMP = composition.W4_1SP
BOSS_ID = "654"
#BOSS_ID = "*"
PLOT_SETTINGS = {"mlp": False, "polyreg": False, "rfr": True, 'binomial_distribution': True, "comps": [str(composition.W1_0SP), str(composition.W2_0SP), str(composition.W1_1SP), str(composition.W2_1SP), str(composition.W3_1SP)]}

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
    elif comp == str(composition.W3_0SP):
        if len(loads(row[2])) != 3:
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
        if boss_id == "*":
            cursor.execute("SELECT COUNT(*) FROM USER")
            num = cursor.fetchone()
            print("There are ", num, "entries")
            data = con.execute("SELECT * FROM USER")
        else:
            cursor.execute("SELECT COUNT(*) FROM USER WHERE boss_id == ?", (str(boss_id),))
            num = cursor.fetchone()
            print("There are ", num, "entries")
            data = con.execute("SELECT * FROM USER WHERE boss_id == ?", (str(boss_id),))
        for row in data:
            if "sample" in row[0]:
                continue
            comp = str(row[1])
            num_players = compToNum(comp)
            print(row, comp, num_players)

            order = []
            #Num locks
            warlock_info = loads(row[2])
            priest_info = loads(row[3])
            for i in range(len(warlock_info)):
                if warlock_info[i].get('spec') is None or warlock_info[i].get('spec')=="unknown":
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

def getTrainingData(boss_id):
    print("Printing db for boss", boss_id)
    X = []
    Y = []
    avg_hit = 0
    data_by_comp = {}

    def insertOrigin(X,Y,comp):
        random_time = random.randint(100,200)
        random_hit = random.randint(85,100)/100.
        crit = 0
        if comp == str(composition.W1_0SP):
            X.append([random_time, random_hit, crit])
            Y.append(0)
        if comp == str(composition.W1_1SP):
            X.append([random_time, random_hit, crit, random_hit])
            Y.append(0)
        if comp == str(composition.W2_0SP):
            X.append([random_time, random_hit, crit, random_hit, crit])
            Y.append(0)
        if comp == str(composition.W2_1SP):
            X.append([random_time, random_hit, crit, random_hit, crit, random_hit])
            Y.append(0)
        if comp == str(composition.W3_0SP):
            X.append([random_time, random_hit, crit, random_hit, crit, random_hit, crit])
            Y.append(0)
        if comp == str(composition.W3_1SP):
            X.append([random_time, random_hit, crit, random_hit, crit, random_hit, crit, random_hit])
            Y.append(0)

    def insertMax(X,Y,comp):
        random_time = random.randint(100,200)
        random_hit = random.randint(85,100)/100.
        crit = 5
        if comp == str(composition.W1_0SP):
            X.append([random_time, random_hit, crit])
            Y.append(1)
        if comp == str(composition.W1_1SP):
            X.append([random_time, random_hit, crit, random_hit])
            Y.append(1)
        if comp == str(composition.W2_0SP):
            X.append([random_time, random_hit, crit, random_hit, crit])
            Y.append(1)
        if comp == str(composition.W2_1SP):
            X.append([random_time, random_hit, crit, random_hit, crit, random_hit])
            Y.append(1)
        if comp == str(composition.W3_0SP):
            X.append([random_time, random_hit, crit, random_hit, crit, random_hit, crit])
            Y.append(1)
        if comp == str(composition.W3_1SP):
            X.append([random_time, random_hit, crit, random_hit, crit, random_hit, crit, random_hit])
            Y.append(1)

    with con:
        cursor = con.cursor()
        if boss_id == "*":
            cursor.execute("SELECT COUNT(*) FROM USER")
            num = cursor.fetchone()
            print("There are ", num, "entries")
            data = con.execute("SELECT * FROM USER")
        else:
            cursor.execute("SELECT COUNT(*) FROM USER WHERE boss_id == ?", (str(boss_id),))
            num = cursor.fetchone()
            print("There are ", num, "entries")
            data = con.execute("SELECT * FROM USER WHERE boss_id == ?", (str(boss_id),))
        #Inject 0 intercept data
        for k in range(1,9):
            for g in [0,.33,.66,1.0]:
                for i in range(0,100,10):
                    X.append([i])
                    for j in range(k):
                        X[-1].append([g,0,0])

        for row in data:
            comp = str(row[1])
            if not checkEntry(row,comp):
                continue
            if data_by_comp.get(comp) is None:
                data_by_comp[comp] = {"X": [], "Y": []}
            # print(row, row[5])
            # time, warlock 1's hit, warlock 1's crit
            X = data_by_comp[comp]['X']
            Y = data_by_comp[comp]['Y']

            insertOrigin(X,Y,comp)
            #insertMax(X,Y,comp)
            # print(X,Y)
            # X.append(insertOrigin(comp))
            # Y.append(0)

            X.append([row[4]])
            for i in range(len(loads(row[2]))):
                X[-1].append(loads(row[2])[i]['hit'])
                X[-1].append(loads(row[2])[i]['crit'])
            for i in range(len(loads(row[3]))):
                X[-1].append(loads(row[3])[i]['hit'])
            avg_hit += loads(row[2])[0]['hit']
            if row[5] == -1:
                Y.append(0)
            else:
                Y.append(row[5])

    return data_by_comp

data_by_size = getAllData(BOSS_ID)
rfr_by_size = {}
poly_regressor_by_size = {}

data_by_comp = getTrainingData(BOSS_ID)
print(data_by_comp)
rfr_by_comp = {}
poly_regressor_by_comp = {}
mlp_by_comp = {}
mlp_scaler_by_comp = {}

#Import scikit-learn metrics module for accuracy calculation
from sklearn import metrics
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
from scipy.optimize import curve_fit
import numpy as np



def sigmoid(x, a, b, c, d, e):
    val = b*x[1]+c*x[2]+d*x[3]
    y = a / (1 + np.exp(-e*val))-.5
    return (y)

def train_by_num():
    for i in range(1,9):
        if len(data_by_size[i]['X']) == 0:
            continue
        rfr_by_size[i]=RandomForestRegressor(n_estimators=100)
        poly_regressor_by_size[i]= {"features": PolynomialFeatures(degree=2), "regressor": LinearRegression(fit_intercept=False)}

        X_train, X_test, y_train, y_test = train_test_split(data_by_size[i]['X'], data_by_size[i]['Y'], test_size=0.2) # 70% training and 30% test
        rfr_by_size[i].fit(X_train,y_train)
        rfr_by_size[i].fit(X_train,y_train)

        X_train_poly = poly_regressor_by_size[i]['features'].fit_transform(X_train)
        poly_regressor_by_size[i]['regressor'].fit(X_train_poly, y_train)

        y_pred=rfr_by_size[i].predict(X_test)
        y_pred_poly=poly_regressor_by_size[i]['regressor'].predict(poly_regressor_by_size[i]['features'].fit_transform(X_test))

        # if i == 1:
        #     p0 = [1.0,.001,.001,.001, 10.0]
        #     time = [item[0] for item in X_train]
        #     spec = [item[1] for item in X_train]
        #     hit = [item[2] for item in X_train]
        #     crit = [item[3] for item in X_train]
        #     popt, pcov = curve_fit(sigmoid, (time,spec,hit,crit), y_train,p0, method='dogbox')
        #     y_pred3 = []
        #     for v in X_test:
        #         print(v)
        #         y_pred3.append(sigmoid(v, float(popt[0]), float(popt[1]), float(popt[2]), float(popt[3]), float(popt[4])))
        #     print("Popt", popt)
        #     print('Mean Absolute Error (MAE) for logreg:', metrics.mean_absolute_error(y_test, y_pred3), "num warlocks", i)


        print(len(X_test))
        #for k in range(len(X_test)):
        #    print(X_test[k], y_pred[k])
        print('Mean Absolute Error (MAE) for RFR:', metrics.mean_absolute_error(y_test, y_pred), "num warlocks", i)
        print('Mean Absolute Error (MAE) for polyreg:', metrics.mean_absolute_error(y_test, y_pred_poly), "num warlocks", i)

for comp, data in data_by_comp.items():
    if comp not in PLOT_SETTINGS['comps']:
        continue
    rfr_by_comp[comp]=RandomForestRegressor(n_estimators=1000, bootstrap=True,criterion="mse", max_depth=4)
    #rfr_by_comp[comp]=KNeighborsRegressor(n_neighbors=10, weights='distance')
    poly_regressor_by_comp[comp]= {"features": PolynomialFeatures(degree=2), "regressor": LinearRegression(fit_intercept=False)}
    mlp_by_comp[comp]=MLPRegressor(random_state=1, max_iter=500, solver="adam", alpha=.00001)

    X_train, X_test, y_train, y_test = train_test_split(data_by_comp[comp]['X'], data_by_comp[comp]['Y'], test_size=0.2) # 70% training and 30% test
    rfr_by_comp[comp].fit(X_train,y_train)

    X_train_poly = poly_regressor_by_comp[comp]['features'].fit_transform(X_train)
    poly_regressor_by_comp[comp]['regressor'].fit(X_train_poly, y_train)


    mlp_scaler_by_comp[comp] = preprocessing.StandardScaler().fit(X_train)
    X_train_mlp = mlp_scaler_by_comp[comp].transform(X_train)
    mlp_by_comp[comp].fit(X_train_mlp,y_train)



    y_pred=rfr_by_comp[comp].predict(X_test)
    y_pred_poly=poly_regressor_by_comp[comp]['regressor'].predict(poly_regressor_by_comp[comp]['features'].fit_transform(X_test))
    y_pred_mlp=mlp_by_comp[comp].predict(mlp_scaler_by_comp[comp].transform(X_test))

    print('Mean Absolute Error (MAE) for RFR:', metrics.mean_absolute_error(y_test, y_pred), str(comp), "size: ", len(X_train)+len(X_test))
    print('Mean Absolute Error (MAE) for polyreg:', metrics.mean_absolute_error(y_test, y_pred_poly), str(comp))
    print('Mean Absolute Error (MAE) for MLP:', metrics.mean_absolute_error(y_test, y_pred_poly), str(comp))

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
            return [95, 1.0, .94, i/100., 1.0, .94, i/100., 0.0, .94, 0.0]
    if num_locks == 3:
        if num_priests == 0:
            return [95, 1.0, .94, i/100., 1.0, .94, i/100., 1.0, .94, i/100.]
        if num_priests == 1:
            return [95, 1.0, .94, i/100., 1.0, .94, i/100., 1.0, .94, i/100., 0.0, .94, 0.0]
    if num_locks == 4:
        if num_priests == 0:
            return [95, 1.0, .94, i/100., 1.0, .94, i/100., 1.0, .94, i/100., 1.0, .94, i/100.]
        if num_priests == 1:
            return [95, 1.0, .94, i/100., 1.0, .94, i/100., 1.0, .94, i/100., 0.0, .94, 0.0]

def genCritDataFromComp(i, comp):
    if comp == str(composition.W1_0SP):
        return [95, .94, i/100.]
    if comp == str(composition.W1_1SP):
        return [95, .94, i/100., .94]
    if comp == str(composition.W2_0SP):
        return [95, .94, i/100., .94, i/100.]
    if comp == str(composition.W2_1SP):
        return [95, .94, i/100., .94, i/100., .94]
    if comp == str(composition.W3_0SP):
        return [95, .94, i/100., .94, i/100., .94, i/100.]
    if comp == str(composition.W3_1SP):
        return [95, .94, i/100., .94, i/100., .94, i/100., .94]


# # Data for plotting

import matplotlib.pyplot as plt

fig, ax = plt.subplots()

def plotRegComp(comp):
    P = []
    Z = []
    G = []
    x = []
    y = []
    for i in range(50):
        P.append(genCritDataFromComp(i, comp))
        Z.append(genCritDataFromComp(i, comp))
        x.append(i/100.)
        y.append(1-(1-.95*i/100.)**4)

    if PLOT_SETTINGS['rfr']:
        s = rfr_by_comp[comp].predict(P)
        ax.plot(x,s, label="random forest regressor, " + str(comp))
    if PLOT_SETTINGS['polyreg']:
        z = poly_regressor_by_comp[comp]['regressor'].predict(poly_regressor_by_comp[comp]['features'].fit_transform(Z))
        ax.plot(x,z, label="polynomial regressor, " + str(comp))
    if PLOT_SETTINGS['mlp']:
        s = mlp_by_comp[comp].predict(mlp_scaler_by_comp[comp].transform(P))
        ax.plot(x,s, label="MLP, " + str(comp))
    if PLOT_SETTINGS['binomial_distribution']:
        ax.plot(x,y, label="binomial distribution, " + str(comp))

def plotReg(num_locks, num_priests):
    P = []
    Z = []
    G = []
    x = []
    y = []
    for i in range(50):
        P.append(genCritDataFromNum(i, num_locks, num_priests))
        Z.append(genCritDataFromNum(i, num_locks, num_priests))
        x.append(i/100.)
        y.append(1-(1-.95*i/100.)**4)

    #s = rfr_by_size[num_locks+num_priests].predict(P)
    s = rfr_by_size[num_locks+num_priests].predict(P)

    z = poly_regressor_by_size[num_locks+num_priests]['regressor'].predict(poly_regressor_by_size[num_locks+num_priests]['features'].fit_transform(Z))

    ax.plot(x,s, label="random forest regressor, " + str(num_locks)+"W - " + str(num_priests)+"SP")
    ax.plot(x,z, label="polynomial regressor, " + str(num_locks)+"W - " + str(num_priests)+"SP")
    ax.plot(x,y, label="binomial distribution, " + str(num_locks)+"W - " + str(num_priests)+"SP")



#plotReg(1, 0)
#plotReg(2, 0)
#plotReg(3, 0)
for comp in PLOT_SETTINGS['comps']:
    plotRegComp(comp)
#plotReg(1, 1)
#plotReg(3, 1)
#plotReg(2, 0)

for v in range(len(data_by_size[3]['X'])):
    ax.plot(data_by_size[3]['X'][v][3],data_by_size[3]['Y'][v], 'k.', alpha=.25)

ax.legend()
ax.set_xlim([0,.6])
ax.set_ylim([0,1.0])
ax.set_title("ISB uptime vs Crit\n Composition=1 Warlock, Hit=.94, Time=.95, Boss=Maiden of Virtue")
ax.set_ylabel("ISB Uptime")
ax.set_xlabel("Crit rate")
plt.grid()

plt.show()
exit()

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
