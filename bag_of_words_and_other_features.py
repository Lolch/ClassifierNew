from sklearn.feature_extraction.text import CountVectorizer
from Email import Email
from collections import defaultdict
from sklearn import linear_model
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import KFold
from numpy import array
import re, string, pickle
from sklearn.naive_bayes import BernoulliNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
import pprint
import settings

def get_top_n_words(corpus, n=None):
    pprint.pprint(corpus)
    vec = CountVectorizer().fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key = lambda x: x[1], reverse=True)
    return words_freq[:n]

with open(settings.LINE_CLASSES_PATH, 'rb') as f:
    lineClasses = pickle.load(f)
with open(settings.SAMPLE_EMAILS_PATH, 'rb') as f:
    emailsList = pickle.load(f)
    


#for key, value in classWords.items():
#    if not key == 'se':
#        print('\n\n' + key + ':')
#        topWords = get_top_n_words(value, 20)
#        print(topWords)

otherFeatures = ['lengthUnder12', 'endsComma', 'containsDashes', 'endsColon', 'inFirst10Perc',
                 'inLast10Perc', 'prevLineBlank', 'nextLineBlank', 'beginsGreater',
                 'containsUnderscores', 'containsNumbers', 'containsAster', 'inAngleBrac',
                 'inDoubleAngleBrac', 'endsFullStop', 'endsExcla', 'startsDash', 'isLineBlank',
                 'lengthUnder20', 'under3Words', 'endsPunct', 'containsPunct', 'containsAt',
                 'lengthOver50', 'containsForwardSlash', 'startsCapLetter']
        
def getFeatures(email, number, features):
    lineText = email.getLine(int(number)-1)
    lineFeatures = []
    for feature in features:
        if feature in lineText:
            lineFeatures.append(1)
        else: lineFeatures.append(0)
    
    lengthUnder12 = 1 if len(lineText) < 12 else 0
    endsComma = 1 if lineText.endswith(',') else 0
    containsDashes = 1 if '-----' in lineText else 0
    endsColon = 1 if lineText.endswith(':') else 0
    inFirst10Perc = 1 if email.getPosition(number) <= 0.1 else 0
    inLast10Perc = 1 if email.getPosition(number) >= 0.9 else 0
    prevLineBlank = 0
    if not int(number) == 1:
        prevLineText = email.getLine(int(number)-2)
        if prevLineText.strip() == '':
            prevLineBlank = 1
    nextLineBlank = 0
    if not int(number) == email.getNoLines():
        nextLineText = email.getLine(int(number))
        if nextLineText.strip() == '':
            nextLineBlank = 1
    beginsGreater = 1 if lineText.startswith('>') else 0
    containsUnderscores = 1 if '____' in lineText else 0
    containsNumbers = 1 if any(char.isdigit() for char in lineText) else 0
    containsAster = 1 if '****' in lineText else 0
    inAngleBrac = 1 if re.match('<.*?>', lineText) else 0
    inDoubleAngleBrac = 1 if re.match('<<.*?>>', lineText) else 0
    endsFullStop = 1 if lineText.endswith('.') else 0
    endsExcla = 1 if lineText.endswith('!') else 0
    startsDash = 1 if lineText.strip().startswith('-') else 0
    isLineBlank = 1 if lineText.strip() == '' else 0
    lengthUnder20 = 1 if len(lineText) < 20 else 0
    under3Words = 1 if len(lineText.split()) < 3 else 0
    endsPunct = 1 if len(lineText) > 0 and lineText[-1] in '.?-:;!,' else 0
    count = lambda l1, l2: len(list(filter(lambda c: c in l2, l1)))
    containsPunct = 1 if count(lineText, string.punctuation) > 0 else 0
    containsAt = 1 if '@' in lineText else 0
    lengthOver50 = 1 if len(lineText) > 50 else 0
    containsForwardSlash = 1 if '/' in lineText else 0
    startsCapLetter = 0
    if len(lineText) > 0:
        startsCapLetter = 1 if lineText[0].isupper() else 0
        
    lineFeatures.extend([lengthUnder12, endsComma, containsDashes, endsColon, inFirst10Perc,
                         inLast10Perc, prevLineBlank, nextLineBlank, beginsGreater,
                         containsUnderscores, containsNumbers, containsAster, inAngleBrac,
                         inDoubleAngleBrac, endsFullStop, endsExcla, startsDash,
                         isLineBlank, lengthUnder20, under3Words, endsPunct, containsPunct,
                         containsAt, lengthOver50, containsForwardSlash, startsCapLetter])
    
    return lineFeatures

def trainTestModel(model, emailsArray):
    kf = KFold(5, True, 7)
    lineList = list((lineClasses))
    trainLines = {}
    testLines = {}
    y_true = []
    y_pred = []
    trainAccuracy = []
    accuracies = []
    
    for train_index, test_index in kf.split(emailsArray):
        trainFPs = emailsArray[train_index]
        trainLines = {}
        testLines = {}
        for line in lineList:
            fp = line.split('lineno')[0]
            if fp in trainFPs:
                trainLines[line] = lineClasses[line]
            else:
                testLines[line] = lineClasses[line]
        lineIDs = list((trainLines))
        X = list()
        Y = list()
        
        
        classWords = defaultdict(list)
        for lineID, lineType in trainLines.items():
            filepath = lineID.split('lineno')[0]
            number = lineID.split('lineno')[1]
            email = Email(filepath)
            lineText = email.getLine(int(number)-1)
            classWords[lineType].append(lineText)
            print(lineText)
        
#        topClassWords = defaultdict(list)
#        for key, value in classWords.items():
#            print("KEY is " + key)
#            pprint.pprint(value)
#            if not key == 'se':
#                topClassWords[key] = get_top_n_words(value, 30)
#        
        # create list of words as features
#        features = []
#        for value in topClassWords.values(): # for each list of words
#            for word in value:
#                if not word[0] in features: # if it hasn't already been added
#                    features.append(word[0])
                    
                    
        features = []
        for value in classWords.values():
            for word in value:
                if not word in features:
                    features.append(word)
        
        for lineID in lineIDs:
            fp = lineID.split('lineno')[0]
            lineNo = lineID.split('lineno')[1]
            email = Email(fp)
            X.append(getFeatures(email, lineNo, features))
            Y.append(lineClasses[lineID])
        model.fit(X, Y)
        
        trainPredictedClasses = {}
        for line in trainLines:
            email = Email(line.split('lineno')[0])
            lineFeatures = getFeatures(email, line.split('lineno')[1], features)
            prediction = model.predict([lineFeatures])
            trainPredictedClasses[line] = prediction
            
        correct = 0
        for key, value in trainPredictedClasses.items():
            if value == lineClasses[key]:
                correct += 1
            else:
                if value == 'se':
                    correct += 1
        trainAccuracy.append((correct/float(len(trainLines)))*100)
        
        predictedClasses = {}
        for line in testLines:
            email = Email(line.split('lineno')[0])
            testFeatures = getFeatures(email, line.split('lineno')[1], features)
            prediction = model.predict([testFeatures])
            predictedClasses[line] = prediction
            
        correct = 0
        
        for key, value in predictedClasses.items():
            y_true.append(lineClasses[key])
            y_pred.append(value)
            if value == lineClasses[key]:
                correct += 1
            else:
                # assume all lines labelled as separators are correct - 
                # this means blank lines within e.g. a body do not lower the accuracy
                if value == 'se':
                    correct += 1
                if value == 'se' and lineClasses[key] == 'tso' and (lineText.strip() == '' or lineText.strip() == None):
                    em = Email(key.split('lineno')[0])
                    print(key + '\n-' + em.getLine(int(key.split('lineno')[1])-1) + '-\n\n\n')
                
        accuracies.append((correct/float(len(testLines)))*100)
        
    overallTrainAccuracy = sum(trainAccuracy)/len(trainAccuracy)
    overallAccuracy = sum(accuracies)/len(accuracies)
    
    labels = ['a', 'b', 'g', 'sa', 'se', 'so', 'tb', 'tg', 'th', 'tsa', 'tso']
    cm = confusion_matrix(y_true, y_pred, labels)
    ax = plt.subplot()
    sns.heatmap(cm, annot=True, ax=ax, fmt='g')
    ax.set_xlabel('Predicted labels')
    ax.set_ylabel('True labels')
    modelType = ((str(type(model)).split('.')[-1])[:-2])
    ax.set_title('Confusion matrix for {0}'.format(modelType))
    ax.xaxis.set_ticklabels(labels)
    ax.yaxis.set_ticklabels(labels)
    plt.show()
    print('Overall training accuracy: {0}'.format("%.2f" % overallTrainAccuracy))
    print('Overall test accuracy: {0}'.format("%.2f" % overallAccuracy))
    
emailsArray = array(emailsList)

#bnb = BernoulliNB()
#trainTestModel(bnb, emailsArray)

regr = linear_model.LogisticRegression(C=1e5)
trainTestModel(regr, emailsArray)

#knn = KNeighborsClassifier()
#trainTestModel(knn, emailsArray)
#
#svc = svm.SVC(kernel='linear')
#trainTestModel(svc, emailsArray)
