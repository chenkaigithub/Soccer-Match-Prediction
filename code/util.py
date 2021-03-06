from sklearn import linear_model
from sklearn import svm
from sklearn.naive_bayes import MultinomialNB
from sklearn.neural_network import MLPClassifier
from collections import defaultdict
import attributeVectorIterator as a

def fetchData(fileName):
    xf = open(fileName + 'X.txt', 'r')
    X = []
    l = []
    for line in xf:
        x = map(float, line.split())
        l.append(len(x))
        X.append(x)
    #print FileName, 'X', l
    xf.close()
    yf = open(fileName + 'Y.txt', 'r')
    Y = map(int, yf.readline().split())
    yf.close()
    return [X, Y]

def fetchFeatureOrder(filename):
    of = open(filename + '.txt', 'r')
    order = {}
    for line in of:
        words = line.split()
        numWords = len(words)
        key = " ".join(words[:numWords-1])
        value = int(words[numWords-1])
        order[key] = value
    return order

def createTrainData(years, writeToFile = False, FileName = ''):
    X = []
    Y = []
    if writeToFile:
        xf = open('trainX' + FileName + '.txt', 'w')
        yf = open('trainY' + FileName + '.txt', 'w')
        o = open('order.txt', 'w')

    order = defaultdict(list)
    length = 0
    
    for (av, result) in a.attributeVectorIterator(years):
        for key in av:
            if key not in order:
                order[key] = length
                length += 1
    for (av, result) in a.attributeVectorIterator(years):
        # preparing newX
        newX = [0] * length
        for key in av:
            newX[order[key]] = av[key]

        # preparing newY
        if result[0] == result[1]:
            newY = 0
        elif result[0] > result[1]:
            newY = 1
        else:
            newY = -1

        # saving results to file if need be
        if writeToFile:
            for i in newX:
                xf.write("%s " %i)
            yf.write("%s " %newY)
            xf.write("\n")
        X.append(newX)
        Y.append(newY)
    #print len(newX)
    if writeToFile:
        for key in order:
            o.write(key + ' ' + str(order[key]) + "\n")
        o.close()
        xf.close()
        yf.close()        
    return [X, Y, order]

def createTestData(years, order, writeToFile = False, FileName = ''):
    X = []
    Y = []
    if writeToFile:
        xf = open('testX' + FileName + '.txt', 'w')
        yf = open('testY' + FileName + '.txt', 'w')

    length = len(order)
    for (av, result) in a.attributeVectorIterator(years):
        # preparing newX
        newX = [0] * length
        for key in av:
            if key in order:
                newX[order[key]] = av[key]

        # preparing newY
        if result[0] == result[1]:
            newY = 0
        elif result[0] > result[1]:
            newY = 1
        else:
            newY = -1

        # saving results to file if need be
        if writeToFile:
            for i in newX:
                xf.write("%s " %i)
            yf.write("%s " %newY)
            xf.write("\n")
        X.append(newX)
        Y.append(newY)
    #print len(newX)
    if writeToFile:
        xf.close()
        yf.close()        
    return [X, Y]

# linear classification
# winBoundary is the value separating wins and draws
# lossBoundary is the value separating losses and draws
# final prediction

# Not sure if this is an actual algorithm lol. But sounds like a good idea to me.
def linearClassification(trainX, trainY, testX, testY, winBoundary=0.5, lossBoundary=-0.5):
    # linear classification
    reg = linear_model.LinearRegression()

    # fitting the data
    reg.fit(trainX, trainY)

    # prediction
    prediction = reg.predict(testX)
    # final prediction
    finalLinear = [1.0 * (x >= winBoundary) + 0 * (x < winBoundary and x >= lossBoundary) + (-1) * (x < lossBoundary) for x in prediction]
    print "Linear classification with boundaries", lossBoundary, winBoundary, "is equal to:", error
    return error

def layeredSVM(trainX, trainY, testX, testY):
    #print testY
    trainY1 = [1 * (x > 0) for x in trainY]
    clfWin = svm.SVC()
    clfWin.fit(trainX, trainY1)
    predictionWin = clfWin.predict(testX)
    #print "Prediction win:", predictionWin
    newTrainX = []
    newTrainY = []
    for i in range(len(trainX)):
        if trainY[i] <= 0:
            newTrainX.append(trainX[i])
            newTrainY.append(-trainY[i])
    clfLoss = svm.SVC()
    clfLoss.fit(newTrainX, newTrainY)
    predictionLoss = clfLoss.predict(testX)
    #print "Prediction Loss:", predictionLoss
    prediction = []
    for i in range(len(testX)):
        if predictionWin[i] == 1:
            prediction.append(1)
        else:
            if predictionLoss[i] == 1:
                prediction.append(-1)
            else:
                prediction.append(0)
    #trainError = sum([1.0 * (trainPrediction[i] != trainY[i]) for i in range(len(trainPrediction))]) / len(trainPrediction)
    error = sum([1.0 * (prediction[i] != testY[i]) for i in range(len(prediction))]) / len(prediction)
    #print "Layered SVM error: ", error
    return (trainError, error)

def SVC(trainX, trainY, testX, testY, regCoeff=1.0):
    clf = svm.SVC(decision_function_shape='ovo', C=regCoeff)
    clf.fit(trainX, trainY)
    trainPrediction = clf.predict(trainX)
    trainError = sum([1.0 * (trainPrediction[i] != trainY[i]) for i in range(len(trainPrediction))]) / len(trainPrediction)
    prediction = clf.predict(testX)
    error = sum([1.0 * (prediction[i] != testY[i]) for i in range(len(prediction))]) / len(prediction)
    #print "Multiclass SVM error (SVC):", error
    return (trainError, error)

def linearSVC(trainX, trainY, testX, testY):
    clf = svm.LinearSVC()
    clf.fit(trainX, trainY)
    trainPrediction = clf.predict(trainX)
    trainError = sum([1.0 * (trainPrediction[i] != trainY[i]) for i in range(len(trainPrediction))]) / len(trainPrediction)
    prediction = clf.predict(testX)
    error = sum([1.0 * (prediction[i] != testY[i]) for i in range(len(prediction))]) / len(prediction)
    #print "linear SVC error (SVC):", error
    return (trainError, error)

def NB(trainX, trainY, testX, testY, smoothing = 1):
    clf = MultinomialNB(alpha = smoothing)
    clf.fit(trainX, trainY)
    trainPrediction = clf.predict(trainX)
    trainError = sum([1.0 * (trainPrediction[i] != trainY[i]) for i in range(len(trainPrediction))]) / len(trainPrediction)
    prediction = clf.predict(testX)
    error = sum([1.0 * (prediction[i] != testY[i]) for i in range(len(prediction))]) / len(prediction)
    #print "Naive Bayes error with smoothing =", smoothing, "is equal to:", error
    return (trainError, error)

def logisticRegression(trainX, trainY, testX, testY, regCoeff = 1.0):
    #clf = linear_model.LogisticRegression(penalty='l2', solver='newton-cg', C=regCoeff, multi_class='multinomial') 
    clf = linear_model.LogisticRegression(penalty='l2', solver='sag', C=regCoeff, multi_class='multinomial') 
    clf.fit(trainX, trainY)
    trainPrediction = clf.predict(trainX)
    trainError = sum([1.0 * (trainPrediction[i] != trainY[i]) for i in range(len(trainPrediction))]) / len(trainPrediction)
    prediction = clf.predict(testX)
    error = sum([1.0 * (prediction[i] != testY[i]) for i in range(len(prediction))]) / len(prediction)
    return (trainError, error)

def logisticRegressionConfusionMatrix(trainX, trainY, testX, testY, regCoeff = 1.0):
    #clf = linear_model.LogisticRegression(penalty='l2', solver='newton-cg', C=regCoeff, multi_class='multinomial', max_iter=1000) 
    clf = linear_model.LogisticRegression() 
    clf.fit(trainX, trainY)
    trainPrediction = clf.predict(trainX)
    prediction = clf.predict(testX)

    confMatrix = {}
    for i in range(len(prediction)):
        index = (prediction[i], testY[i])
        confMatrix[index] = confMatrix.get(index, 0.0) + 1.0

    return confMatrix


def MLP(trainX, trainY, testX, testY, layerSize, alph = 1e-5):
    clf = MLPClassifier(solver = 'lbfgs', alpha = alph, hidden_layer_sizes = layerSize, random_state = 1)
    clf.fit(trainX, trainY)
    prediction = clf.predict(testX)
    error = sum([1.0 * (prediction[i] != testY[i]) for i in range(len(prediction))]) / len(prediction)
    print "Multi-layer perceptron error with layerSize =", layerSize, "is equal to:", error
    return error

'''
trainYears = [ '2011/2012', '2012/2013', '2013/2014']
testYears = ['2014/2015']
[trainX, trainY, order] = createTrainData(trainYears)
[testX, testY] = createTestData(testYears, order)
MLP(trainX, trainY, testX, testY, (5, 5))
'''
