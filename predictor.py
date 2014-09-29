import util, random, math, sys
from math import exp, log
from util import Counter

############################################################
# Feature extractors: a feature extractor should take a raw input x (tuple of
# tokens) and add features to the featureVector (Counter) provided.

def pivotFeatureExtractor(x):
  quarter, time, down, dist, yrdline, play, awyscr, homescr, epb, epa, home, team = x.split(",")
  featureVector = util.Counter()
  
  # For each token in the URL, add an indicator feature
  #featureVector['quarter:' + quarter] += 0.1
  
  featureVector['down:' + down] += 1
  featureVector['dist:' + dist] += 1
  
  if dist != '':
    if int(dist) > 20:
      dist = "20+"
    elif int(dist) >= 16:
      dist = "16-20"
    elif int(dist) >= 11:
      dist = "11-15"
  #featureVector['downdist:' + down + dist] += 0.6
  
  minute = time.split(":")

  featureVector['time:' + quarter + minute[0]] += 1
 
 
  lineint = 0 
  if team in yrdline:
    yrdinfo = yrdline.split(" ")
    lineint = int(yrdinfo[1])
    lineint = lineint // 10 
    featureVector['yrd:' + str(lineint)] += 1
  else:
    yrdinfo = yrdline.split(" ")
    first = yrdinfo[0]
    if (first == '50'):
      featureVector['yrd:5'] += 1
    elif (first == ''):
      featureVector['yrd:2PT'] += 1
    else:
      lineint = int(yrdinfo[1])
      if (lineint >= 45):
        lineint = 5
      elif (lineint >= 40):
        lineint = 6
      elif (lineint >= 35):
        lineint = 7
      elif (lineint >= 30):
        lineint = 8
      elif (lineint >= 25):
        lineint = 9
      elif (lineint >= 20):
        lineint = 10
      elif (lineint >= 15):
        lineint = 11
      elif (lineint >= 10):
        lineint = 12
      elif (lineint >= 5):
        lineint = 13
      else:
        lineint = 14
 
    featureVector['yrd:' + str(lineint)] += 1
  

  scorediff = 0
  homescore = int(homescr)
  awayscore = int(awyscr)
  if (home == "True"):
    scorediff = homescore - awayscore
  else:
    scorediff = awayscore - homescore
  if (scorediff <= -15):
    scorediff = -5
  elif (scorediff <= -11):
    scorediff = -4
  elif (scorediff <= -8):
    scorediff = -3
  elif (scorediff <= -4):
    scorediff = -2
  elif (scorediff <= -1):
    scorediff = -1
  elif (scorediff == 0):
    scorediff = 0
  elif (scorediff <= 3):
    scorediff = 1
  elif (scorediff <= 7):
    scorediff = 2
  elif (scorediff <= 10):
    scorediff = 3 
  elif (scorediff <= 14):
    scorediff = 4
  else:
    scorediff = 5
  featureVector['scrdiff:' + str(scorediff)] += 1
  
  """
  if (quarter != "OT"):
    if (int(quarter) == 2) or (int(quarter) == 4):
      if (minute[0] != ''):
        if (int(minute[0]) < 2):
          if (scorediff > 0):
            featureVector['l2:Yes' + quarter + "ahead"] += 5
          elif (scorediff == 0):
            featureVector['l2:Yes' + quarter + "tied"] += 5
          else:
            featureVector['l2:Yes' + quarter + "behind"] += 5
  """

  
  return featureVector



def basicFeatureExtractor(x):
  quarter, time, down, dist, yrdline, play, awyscr, homescr, epb, epa, home, team = x.split(",")
  featureVector = util.Counter()
  
  # For each token in the URL, add an indicator feature
  #featureVector['quarter:' + quarter] += 0.1
  
  featureVector['down:' + down] += 0.4
  featureVector['dist:' + dist] += 0.4
  
  if dist != '':
    if int(dist) > 20:
      dist = "20+"
    elif int(dist) >= 16:
      dist = "16-20"
    elif int(dist) >= 11:
      dist = "11-15"
  #featureVector['downdist:' + down + dist] += 0.6
  
  minute = time.split(":")

  #featureVector['time:' + quarter + minute[0]] += 1
  """  
  lineint = 0 
  if team in yrdline:
    yrdinfo = yrdline.split(" ")
    lineint = int(yrdinfo[1])
    lineint = lineint // 10 
    featureVector['yrd:' + str(lineint)] += 0.2
  else:
    yrdinfo = yrdline.split(" ")
    first = yrdinfo[0]
    if (first == '50'):
      featureVector['yrd:5'] += 0.2
    elif (first == ''):
      featureVector['yrd:0'] += 1
    else:
      lineint = int(yrdinfo[1])
      if (lineint >= 40):
        lineint = 5
      elif (lineint >= 30):
        lineint = 6
      elif (lineint >= 20):
        lineint = 7
      elif (lineint >= 10):
        lineint = 8
      elif (lineint >= 5):
        lineint = 9
      else:
        lineint = 10
 
      featureVector['yrd:' + str(lineint)] += 0.2
  """

  scorediff = 0
  homescore = int(homescr)
  awayscore = int(awyscr)
  if (home == "True"):
    scorediff = homescore - awayscore
  else:
    scorediff = awayscore - homescore
  if (scorediff <= -15):
    scorediff = -5
  elif (scorediff <= -11):
    scorediff = -4
  elif (scorediff <= -8):
    scorediff = -3
  elif (scorediff <= -4):
    scorediff = -2
  elif (scorediff <= -1):
    scorediff = -1
  elif (scorediff == 0):
    scorediff = 0
  elif (scorediff <= 3):
    scorediff = 1
  elif (scorediff <= 7):
    scorediff = 2
  elif (scorediff <= 10):
    scorediff = 3 
  elif (scorediff <= 14):
    scorediff = 4
  else:
    scorediff = 5
  #featureVector['scrdiff:' + str(scorediff)] += 0.6
  
  """
  if (quarter != "OT"):
    if (int(quarter) == 2) or (int(quarter) == 4):
      if (minute[0] != ''):
        if (int(minute[0]) < 2):
          if (scorediff > 0):
            featureVector['l2:Yes' + quarter + "ahead"] += 5
          elif (scorediff == 0):
            featureVector['l2:Yes' + quarter + "tied"] += 5
          else:
            featureVector['l2:Yes' + quarter + "behind"] += 5
  """

  featureVector['situation:' + str(scorediff) + quarter] += 1

  featureVector['wombocombo:' + str(scorediff) + dist] += 0.5
  featureVector['wombocombodown:' + str(scorediff) + dist + down] += 1.1
  
  return featureVector

   


"""
The logistic loss, for a given weight vector.
@param featureVector: The featurized representation of a training example
@param y: The true value of the example (in our case, +/- 3)
@param weights: The weight vector assigning a weight to every feature
@return The scalar value of the logistic loss.
"""
def logisticLoss(featureVector, y, weights):
  wx = featureVector * weights
  return log(1 + exp(-(wx)*y))

"""
The gradient of the logistic loss with respect to the weight vector.
@param featureVector: The featurized representation of a training example
@param y: The true value of the example (in our case, +/- 1)
@param weights: The weight vector assigning a weight to every feature
@return The gradient [vector] of the logistic loss, with respect to w,
        the weights we are learning.
"""
def logisticLossGradient(featureVector, y, weights):
  wx = featureVector * weights
  newVector = featureVector
  newVector = newVector * (-y)*(1 / (1 + exp((wx)*y)))
  return newVector


"""
The hinge loss, for a given weight vector.
@param featureVector: The featurized representation of a training example
@param y: The true value of the example (in our case, +/- 1)
@param weights: The weight vector assigning a weight to every feature
@return The scalar value of the hinge loss.
"""
def hingeLoss(featureVector, y, weights):
  wx = featureVector * weights
  if ((1 - (wx * y)) > 0): return (1 - (wx * y))
  return 0

"""
The gradient of the hinge loss with respect to the weight vector.
@param featureVector: The featurized representation of a training example
@param y: The true value of the example (in our case, +/- 1)
@param weights: The weight vector assigning a weight to every feature
@return The gradient [vector] of the hinge loss, with respect to w,
        the weights we are learning.
        You should not worry about the case when the hinge loss is exactly 1
"""
def hingeLossGradient(featureVector, y, weights):
  wx = featureVector * weights
  newVector = featureVector
  if ((wx * y) < 1):
     newVector = newVector * -y  
  else:
     newVector = newVector * 0
  return newVector

"""
The squared loss, for a given weight vector.
@param featureVector: The featurized representation of a training example
@param y: The true value of the example (in our case, +/- 1)
@param weights: The weight vector assigning a weight to every feature
@return The scalar value of the squared loss.
"""
def squaredLoss(featureVector, y, weights):
  wx = featureVector * weights
  return (0.5*((wx - y)**2))

"""
The gradient of the squared loss with respect to the weight vector.
@param featureVector: The featurized representation of a training example
@param y: The true value of the example (in our case, +/- 1)
@param weights: The weight vector assigning a weight to every feature
@return The gradient [vector] of the squared loss, with respect to w,
        the weights we are learning.
"""
def squaredLossGradient(featureVector, y, weights):
  wx = featureVector * weights
  newVector = featureVector
  newVector = newVector * (wx - y)
  return newVector

class StochasticGradientLearner():
  def __init__(self, featureExtractor):
    self.featureExtractor = util.memoizeById(featureExtractor)

  """
  This function takes a list of training examples and performs stochastic 
  gradient descent to learn weights.
  @param trainExamples: list of training examples (you should only use this to
                        update weights).
                        Each element of this list is a list whose first element
                        is the input, and the second element, and the second
                        element is the true label of the training example.
  @param validationExamples: list of validation examples (just to see how well
                             you're generalizing)
  @param loss: function that takes (x, y, weights) and returns a number
               representing the loss.
  @param lossGradient: function that takes (x, y, weights) and returns the
                       gradient vector as a counter.
                       Recall that this is a function of the featureVector,
                       the true label, and the current weights.
  @param options: various parameters of the algorithm
     * initStepSize: the initial step size
     * stepSizeReduction: the t-th update should have step size:
                          initStepSize / t^stepSizeReduction
     * numRounds: make this many passes over your training data
     * regularization: the 'lambda' term in L2 regularization
  @return No return value, but you should set self.weights to be a counter with
          the new weights, after learning has finished.
  """
  def learnPivot(self, trainExamples, validationExamples, pivot, loss, lossGradient, options):
    weights = util.Counter()
    random.seed(42)
    
    # You should go over the training data numRounds times.
    # Each round, go through all the examples in some random order and update
    # the weights with respect to the gradient.
    for round in range(0, options.numRounds):
      random.shuffle(trainExamples)
      numUpdates = 0  # Should be incremented with each example and determines the step size.
      trainingSize = len(trainExamples)
      # Loop over the training examples and update the weights based on loss and regularization.
      # If your code runs slowly, try to explicitly write out the dot products
      # in the code here (e.g., "for key,value in counter: counter[key] += ---"
      # rather than "counter * other_vector")
      for x, y in trainExamples:
          numUpdates += 1
          stepSize = options.initStepSize / (numUpdates**options.stepSizeReduction)
          featx = self.featureExtractor(x)
          reg = -1
          if (y == pivot): reg = 1
          gradient = lossGradient(featx, reg, weights)
          if (gradient.totalCount() != 0):
            updater = (gradient * stepSize)
            for key in updater:
                weights[key] -= updater[key]
          if (options.regularization != 0):
            for key in gradient:
                weights[key] -= stepSize * (weights[key] * (options.regularization / trainingSize))

      # Compute the objective function.
      # Here, we have split the objective function into two components:
      # the training loss, and the regularization penalty.
      # The objective function is the sum of these two values
      trainLoss = 0  # Training loss
      regularizationPenalty = 0  # L2 Regularization penalty
      
      for x, y in trainExamples:
          featx = self.featureExtractor(x)
          reg = -1
          if (y == pivot): reg = 1
          trainLoss += loss(featx, reg, weights)
      if (options.regularization != 0):
          for key in weights:
              regularizationPenalty += (weights[key]**2)
          regularizationPenalty *= (options.regularization / 2)
      self.objective = trainLoss + regularizationPenalty

      numMistakes = 0
      for x,y in trainExamples:
        predicted_y = self.predictPivots(x, weights)
        reg = -1
        if (y == pivot): reg = 1
        if (reg != predicted_y):
          if options.verbose > 0:
            featureVector = self.featureExtractor(x)
            margin = (featureVector * weights) * reg
            print "%s error (true y = %s, predicted y = %s, margin = %s): x = %s" % ('train', reg, predicted_y, margin, x)
            for f, v, w in sorted([(f, v, weights[f]) for f, v in featureVector.items()], key = lambda fvw: fvw[1]*fvw[2]):
              print " %-30s : %s * %.2f = %.2f" % (f, v, w, v * w)
          numMistakes += 1
      trainError = 1.0 * numMistakes / len(trainExamples)
      

      
      for x,y in validationExamples:
        predicted_y = self.predictPivots(x, weights)
        reg = -1
        if (y == pivot): reg = 1
        if (reg != predicted_y):
          if options.verbose > 0:
            featureVector = self.featureExtractor(x)
            margin = (featureVector * weights) * reg
            print "%s error (true y = %s, predicted y = %s, margin = %s): x = %s" % ('validation', reg, predicted_y, margin, x)
            for f, v, w in sorted([(f, v, weights[f]) for f, v in featureVector.items()], key = lambda fvw: fvw[1]*fvw[2]):
              print " %-30s : %s * %.2f = %.2f" % (f, v, w, v * w)
          numMistakes += 1
      validationError = 1.0 * numMistakes / len(validationExamples)

      print "Round %s/%s: objective = %.2f = %.2f + %.2f, train error = %.4f" % (round+1, options.numRounds, self.objective, trainLoss, regularizationPenalty, trainError)
      
      """
      # See how well we're doing on our actual goal (error rate).
      trainError = util.getClassificationErrorRate(trainExamples, self.predict, trainKickingExamples, 'train', options.verbose, self.featureExtractor, weights)
      
      if options.single == 'no':
        validationError = util.getClassificationErrorRate(validationExamples, self.predict, validationKickingExamples, 'validation', options.verbose, self.featureExtractor, weights)
      """
    return weights

 
  def learn(self, trainExamples, validationExamples, trainKickingExamples, validationKickingExamples, loss, lossGradient, options):
    self.weights = util.Counter()
    random.seed(42)
    
    # You should go over the training data numRounds times.
    # Each round, go through all the examples in some random order and update
    # the weights with respect to the gradient.
    for round in range(0, options.numRounds):
      random.shuffle(trainExamples)
      numUpdates = 0  # Should be incremented with each example and determines the step size.
      trainingSize = len(trainExamples)
      # Loop over the training examples and update the weights based on loss and regularization.
      # If your code runs slowly, try to explicitly write out the dot products
      # in the code here (e.g., "for key,value in counter: counter[key] += ---"
      # rather than "counter * other_vector")
      for x, y in trainExamples:
        numUpdates += 1
        stepSize = options.initStepSize / (numUpdates**options.stepSizeReduction)
        featx = self.featureExtractor(x)
        gradient = lossGradient(featx, y, self.weights)
        if (gradient.totalCount() != 0):
            updater = (gradient * stepSize)
            for key in updater:
                self.weights[key] -= updater[key]
        if (options.regularization != 0):
            for key in gradient:
                self.weights[key] -= stepSize * (self.weights[key] * (options.regularization / trainingSize))

      # Compute the objective function.
      # Here, we have split the objective function into two components:
      # the training loss, and the regularization penalty.
      # The objective function is the sum of these two values
      trainLoss = 0  # Training loss
      regularizationPenalty = 0  # L2 Regularization penalty
      
      for x, y in trainExamples:
          featx = self.featureExtractor(x)
          trainLoss += loss(featx, y, self.weights)
      if (options.regularization != 0):
          for key in self.weights:
              regularizationPenalty += (self.weights[key]**2)
          regularizationPenalty *= (options.regularization / 2)
      self.objective = trainLoss + regularizationPenalty

      # See how well we're doing on our actual goal (error rate).
      trainError = util.getClassificationErrorRate(trainExamples, self.predict, trainKickingExamples, 'train', options.verbose, self.featureExtractor, self.weights)
      
      if options.single == 'no':
        validationError = util.getClassificationErrorRate(validationExamples, self.predict, validationKickingExamples, 'validation', options.verbose, self.featureExtractor, self.weights)

        print "Round %s/%s: objective = %.2f = %.2f + %.2f, train error = %.4f, validation error = %.4f" % (round+1, options.numRounds, self.objective, trainLoss, regularizationPenalty, trainError, validationError)

    # Print out feature weights
    out = open('weights', 'w')
    for f, v in sorted(self.weights.items(), key=lambda x: -x[1]):
      print >>out, f + "\t" + str(v)
    out.close()
    if options.single == 'yes' and len(validationExamples) != 0:
      print (self.weights * self.featureExtractor(validationExamples[0][0]))
      if self.predict(validationExamples[0][0]) == 1:
        print "pass"
      else: print "run"
    elif options.single == 'yes' and len(validationKickingExamples) != 0:
      quarter, time, down, dist, yrdline, play, awyscr, homescr, epb, epa, home, team = validationKickingExamples[0][0].split(",")
      prediction = "field goal"
      minute = time.split(":")
      scorediff = 0
      if home == "True":
        scorediff = int(homescr) - int(awyscr)
      else:
        scorediff = int(awyscr) - int(homescr)
      if int(minute[0]) <= 3 and (quarter == "4"):
        if (scorediff < -3) and (scorediff >= -16):
          prediction = "pass"
        elif (scorediff >= -3) and scorediff < 0 and (team in yrdline):
          prediction = "pass"
      else:
        if team in yrdline:
          prediction = "punt"
        else:
          yrdinfo = yrdline.split(" ")
          first = yrdinfo[0]
          if first == "50": prediction = "punt"
          else:
            if int(yrdinfo[1]) >= 38: prediction = "punt"
      print prediction
        

  def predict(self, x):
    featureVector = self.featureExtractor(x)
    if ((self.weights * featureVector) < 0): return -1
    return 1

  def predictPivots(self, x, weights):
    featureVector = self.featureExtractor(x)
    if ((weights * featureVector) < 0): return -1
    return 1

if __name__ == '__main__':
  util.runLearner(sys.modules[__name__], sys.argv[1:])
