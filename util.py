import sys, math
from math import exp, log

# Return the error rate on examples when using predict.
# featureExtractor, if specified is used for debugging.
def getClassificationErrorRate(examples, predict, kickingExamples, displayName=None, verbose=0, featureExtractor=None, weights=None):
  numMistakes = 0
  # For each example, make a prediction.
  for x, y in examples:
    predicted_y = predict(x)
    if y != predicted_y:
      if verbose > 0:
        featureVector = featureExtractor(x)
        margin = (featureVector * weights) * y
        print "%s error (true y = %s, predicted y = %s, margin = %s): x = %s" % (displayName, y, predicted_y, margin, x)
        for f, v, w in sorted([(f, v, weights[f]) for f, v in featureVector.items()], key = lambda fvw: fvw[1]*fvw[2]):
          print "  %-30s : %s * %.2f = %.2f" % (f, v, w, v * w)
      numMistakes += 1
  
  for x, y in kickingExamples:
    quarter, time, down, dist, yrdline, play, awyscr, homescr, epb, epa, home, team = x.split(",")
    prediction = "field goal"
    if (down == "4"):
      if team in yrdline:
        prediction = "punt"
      else:
        yrdinfo = yrdline.split(" ")
        first = yrdinfo[0]
        if first == "50": prediction = "punt"
        else:
          if int(yrdinfo[1]) >= 38:
            prediction = "punt"
      scorediff = 0
      if home == "True":
        scorediff = int(homescr) - int(awyscr)
      else:
        scorediff = int(awyscr) - int(homescr)
      if (scorediff < -3) and (scorediff >= -16):
        if (quarter == "4"):
          minute = time.split(":")
          if minute != '':
            if int(minute[0]) <= 3:
              prediction = "pass"
      elif (scorediff < 0) and (scorediff >= -3) and (team in yrdline):
        if (quarter == "4"):
          minute = time.split(":")
          if minute != '':
            if int(minute[0]) <= 3:
              prediction = "pass"
    if prediction != y:
      print "%s error (true y = %s, predicted y = %s): x = %s" % (displayName, y, prediction, x)
      numMistakes += 1
  return 1.0 * numMistakes / (len(examples) + len(kickingExamples))
 

def readPivotExamples(path, team):
  examples = []
  home = False
  for line in path:
    if ("kicks off" not in line) and ("extra point" not in line):
      if not line.startswith(",,,,,"):
        if (not line.startswith("Quarter")) and (not line.startswith("Overtime")):
          if not line.startswith("\n"): 
            if ",Penalty" not in line:
              line = line + "," + str(home) + ',' + team
              x = line
              if ("field goal" in line):
                y = "field goal"
              elif ("punts" in line):
                y = "punt"
              elif ("pass incomplete" in line) or ("pass complete" in line) or ("sacked" in line) or ("spiked" in line):
                y = "pass"
              else:
                y = "run"
              examples.append((x, y))
        else:
          if "Detail,"+team in line:
            home = False
          else:
            home = True 
  print "Read %d examples from %s" % (len(examples), path)
  return examples


def readExamples(path, team):
  examples = []
  kickingexamples = []
  home = False
  for line in path:
    if ("kicks off" not in line) and ("extra point" not in line):
      if not line.startswith(",,,,,"):
        if (not line.startswith("Quarter")) and (not line.startswith("Overtime")):
          if not line.startswith("\n"): 
            if ",Penalty" not in line:
              quarter, time, down, dist, yrdline, play, awyscr, homescr, epb, epa = line.split(",")
              if (down == "4"):
                line = line + "," + str(home) + ',' + team
                x = line
                if ("pass incomplete" in line) or ("pass complete" in line) or ("sacked" in line) or ("spiked" in line):
                  y = "pass"
                elif ("field goal" in line):
                  y = "field goal"
                elif ("punts" in line): 
                  y = "punt"
                else:
                  y = "run"
                kickingexamples.append((x,y))
              else:
                line = line + "," + str(home) + ',' + team
                x = line
                if ("pass incomplete" in line) or ("pass complete" in line) or ("sacked" in line) or ("spiked" in line):
                  y = 1
                else:
                  y = -1
                examples.append((x, y))
        else:
          if "Detail,"+team in line:
            home = False
          else:
            home = True 
  print "Read %d examples from %s" % (len(examples), path)
  print "Read %d kicking examples from %s" % (len(kickingexamples), path)
  return (examples, kickingexamples)

def buildBayesProbability(path, team, laplace):
  examples = []
  home = False
  for line in path:
    if ("extra point" not in line) and ("kicks off" not in line):
      if not line.startswith(",,,,,"):
        if (not line.startswith("Quarter")) and (not line.startswith("Overtime")):
          if not line.startswith("\n"): 
            if ",Penalty" not in line:
                line = line + "," + str(home)
                x = line
                if ("pass incomplete" in line) or ("pass complete" in line) or ("sacked" in line) or ("spiked" in line):
                  y = "pass"
                elif ("field goal" in line):
                  y = "field goal"
                elif ("punts" in line):
                  y = "punt"
                else:
                  y = "run"
                examples.append((x, y))
        else:
          if "Detail,"+team in line:
            home = False
          else:
            home = True 
  passprobs = {'min:OT':0, 'min:45':0, 'min:36':0, 'min:35':0, 'min:34':0, 'min:33':0, 'min:32':0, 'min:31':0, 'min:30':0, 'min:15':0, 'min:6':0, 'min:5':0, 'min:4':0, 'min:3':0, 'min:2':0, 'min:1':0, 'min:0':0, '1st': 0, '2nd': 0, '3rd': 0, '4th': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, '10': 0, '11-20': 0, '20+': 0, 'yd2PT': 0, 'yd0': 0, 'yd1': 0, 'yd2': 0, 'yd3': 0, 'yd4': 0, 'yd5': 0, 'yd6': 0, 'yd7': 0, 'yd8': 0, 'yd9': 0, 'yd10': 0, 'yd11': 0, 'yd12': 0, 'yd13': 0, 'yd14': 0, 'diff-5': 0, 'diff-4': 0, 'diff-3': 0, 'diff-2': 0, 'diff-1': 0, 'diff0': 0, 'diff1': 0, 'diff2': 0, 'diff3': 0, 'diff4': 0, 'diff5': 0}
  runprobs = {'min:OT':0, 'min:45':0, 'min:36':0, 'min:35':0, 'min:34':0, 'min:33':0, 'min:32':0, 'min:31':0, 'min:30':0, 'min:15':0, 'min:6':0, 'min:5':0, 'min:4':0, 'min:3':0, 'min:2':0, 'min:1':0, 'min:0':0, '1st': 0, '2nd': 0, '3rd': 0, '4th': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, '10': 0, '11-20': 0, '20+': 0, 'yd2PT': 0, 'yd0': 0, 'yd1': 0, 'yd2': 0, 'yd3': 0, 'yd4': 0, 'yd5': 0, 'yd6': 0, 'yd7': 0, 'yd8': 0, 'yd9': 0, 'yd10': 0, 'yd11': 0, 'yd12': 0, 'yd13': 0, 'yd14': 0, 'diff-5': 0, 'diff-4': 0, 'diff-3': 0, 'diff-2': 0, 'diff-1': 0, 'diff0': 0, 'diff1': 0, 'diff2': 0, 'diff3': 0, 'diff4': 0, 'diff5': 0}
  fgprobs = {'min:OT':0, 'min:45':0, 'min:36':0, 'min:35':0, 'min:34':0, 'min:33':0, 'min:32':0, 'min:31':0, 'min:30':0, 'min:15':0, 'min:6':0, 'min:5':0, 'min:4':0, 'min:3':0, 'min:2':0, 'min:1':0, 'min:0':0, '1st': 0, '2nd': 0, '3rd': 0, '4th': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, '10': 0, '11-20': 0, '20+': 0, 'yd2PT': 0, 'yd0': 0, 'yd1': 0, 'yd2': 0, 'yd3': 0, 'yd4': 0, 'yd5': 0, 'yd6': 0, 'yd7': 0, 'yd8': 0, 'yd9': 0, 'yd10': 0, 'yd11': 0, 'yd12': 0, 'yd13': 0, 'yd14': 0, 'diff-5': 0, 'diff-4': 0, 'diff-3': 0, 'diff-2': 0, 'diff-1': 0, 'diff0': 0, 'diff1': 0, 'diff2': 0, 'diff3': 0, 'diff4': 0, 'diff5': 0}
  puntprobs = {'min:OT':0, 'min:45':0, 'min:36':0, 'min:35':0, 'min:34':0, 'min:33':0, 'min:32':0, 'min:31':0, 'min:30':0, 'min:15':0, 'min:6':0, 'min:5':0, 'min:4':0, 'min:3':0, 'min:2':0, 'min:1':0, 'min:0':0, '1st': 0, '2nd': 0, '3rd': 0, '4th': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0, '10': 0, '11-20': 0, '20+': 0, 'yd2PT': 0, 'yd0': 0, 'yd1': 0, 'yd2': 0, 'yd3': 0, 'yd4': 0, 'yd5': 0, 'yd6': 0, 'yd7': 0, 'yd8': 0, 'yd9': 0, 'yd10': 0, 'yd11': 0, 'yd12': 0, 'yd13': 0, 'yd14': 0, 'diff-5': 0, 'diff-4': 0, 'diff-3': 0, 'diff-2': 0, 'diff-1': 0, 'diff0': 0, 'diff1': 0, 'diff2': 0, 'diff3': 0, 'diff4': 0, 'diff5': 0}

       
  for key, value in passprobs.iteritems():
    passprobs[key] = passprobs[key] + laplace
  for key, value in runprobs.iteritems():
    runprobs[key] = runprobs[key] + laplace
  for key, value in fgprobs.iteritems():
    fgprobs[key] = fgprobs[key] + laplace
  for key, value in puntprobs.iteritems():
    puntprobs[key] = puntprobs[key] + laplace
  
  numpasses = 0
  numruns = 0
  numfgs = 0
  numpunts = 0

  for x,y in examples:
    quarter, time, down, dist, yrdline, play, awyscr, homescr, epb, epa, home = x.split(",")
    if y == "pass":
      numpasses += 1

      timeleft = 0
      minute = time.split(":")
      if quarter == "OT":
        timeleft = "OT"
      else:
        qint = int(quarter)
        timeleft = (4 - qint) * 15
        if (qint == 2) or (qint == 4):
          if minute[0] != '':
            if int(minute[0]) <= 5:
              timeleft += int(minute[0])
            else: timeleft += 6
      #if "min:"+str(timeleft) in passprobs.keys():
      passprobs['min:'+str(timeleft)] = passprobs['min:'+str(timeleft)] + 1
      #else:
      #  passprobs['min:'+str(timeleft)] = 1
      
      if down == "1":
        passprobs['1st'] = passprobs['1st'] + 1
      elif down == "2": 
        passprobs['2nd'] = passprobs['2nd'] + 1
      elif down == "3":
        passprobs['3rd'] = passprobs['3rd'] + 1
      elif down == "4":
        passprobs['4th'] = passprobs['4th'] + 1
      
      if dist != '':
        if int(dist) <= 10:
          passprobs[dist] = passprobs[dist] + 1
        elif int(dist) <= 20:
          passprobs['11-20'] = passprobs['11-20'] + 1
        else:
          passprobs['20+'] = passprobs['20+'] + 1
        """
        elif int(dist) <= 15:
          passprobs['11-15'] = passprobs['11-15'] + 1
        elif int(dist) <= 20:
          passprobs['16-20'] = passprobs['16-20'] + 1
        """
      else: passprobs['2'] = passprobs['2'] + 1

      lineint = 0
      yrdinfo = yrdline.split(" ")
      if team in yrdline:
        lineint = int(yrdinfo[1])
        lineint = lineint // 10
        if (lineint == 0):
          passprobs['yd0'] = passprobs['yd0'] + 1
        elif (lineint == 1):
          passprobs['yd1'] = passprobs['yd1'] + 1
        elif (lineint == 2):
          passprobs['yd2'] = passprobs['yd2'] + 1
        elif (lineint == 3):
          passprobs['yd3'] = passprobs['yd3'] + 1
        else:
          passprobs['yd4'] = passprobs['yd4'] + 1
      else:
        first = yrdinfo[0]
        if first == '50':
          passprobs['yd5'] = passprobs['yd5'] + 1
        elif first == '':
          passprobs['yd2PT'] = passprobs['yd2PT'] + 1
        else:
          lineint = int(yrdinfo[1])
          if (lineint >= 45):
            passprobs['yd5'] = passprobs['yd5'] + 1
          elif (lineint >= 40):
            passprobs['yd6'] = passprobs['yd6'] + 1
          elif (lineint >= 35):
            passprobs['yd7'] = passprobs['yd7'] + 1
          elif (lineint >= 30):
            passprobs['yd8'] = passprobs['yd8'] + 1
          elif (lineint >= 25):
            passprobs['yd9'] = passprobs['yd9'] + 1
          elif (lineint >= 20):
            passprobs['yd10'] = passprobs['yd10'] + 1
          elif (lineint >= 15):
            passprobs['yd11'] = passprobs['yd11'] + 1
          elif (lineint >= 10):
            passprobs['yd12'] = passprobs['yd12'] + 1
          elif (lineint >= 5):
            passprobs['yd13'] = passprobs['yd13'] + 1
          else:
            passprobs['yd14'] = passprobs['yd14'] + 1

      scorediff = 0
      homescore = int(homescr)
      awayscore = int(awyscr)
      if (home == "True"):
        scorediff = homescore - awayscore
      else:
        scorediff = awayscore - homescore
      if (scorediff <= -15):
        passprobs['diff-5'] = passprobs['diff-5'] + 1
      elif (scorediff <= -11):
        passprobs['diff-4'] = passprobs['diff-4'] + 1
      elif (scorediff <= -8):
        passprobs['diff-3'] = passprobs['diff-3'] + 1
      elif (scorediff <= -4):
        passprobs['diff-2'] = passprobs['diff-2'] + 1
      elif (scorediff <= -1):
        passprobs['diff-1'] = passprobs['diff-1'] + 1
      elif (scorediff == 0):
        passprobs['diff0'] = passprobs['diff0'] + 1
      elif (scorediff <= 3):
        passprobs['diff1'] = passprobs['diff1'] + 1
      elif (scorediff <= 7):
        passprobs['diff2'] = passprobs['diff2'] + 1
      elif (scorediff <= 10):
        passprobs['diff3'] = passprobs['diff3'] + 1
      elif (scorediff <= 14):
        passprobs['diff4'] = passprobs['diff4'] + 1
      else: 
        passprobs['diff5'] = passprobs['diff5'] + 1
     
    elif y == "field goal":
      numfgs += 1

      timeleft = 0
      minute = time.split(":")
      if quarter == "OT":
        timeleft = "OT"
      else:
        qint = int(quarter)
        timeleft = (4 - qint) * 15
        if (qint == 2) or (qint == 4):
          if minute[0] != '':
            if int(minute[0]) <= 5:
              timeleft += int(minute[0])
            else: timeleft += 6
      #if "min:"+str(timeleft) in fgprobs.keys():
      fgprobs['min:'+str(timeleft)] = fgprobs['min:'+str(timeleft)] + 1
      #else:
      #  fgprobs['min:'+str(timeleft)] = 1
      
      if down == "1":
        fgprobs['1st'] = fgprobs['1st'] + 1
      elif down == "2": 
        fgprobs['2nd'] = fgprobs['2nd'] + 1
      elif down == "3":
        fgprobs['3rd'] = fgprobs['3rd'] + 1
      elif down == "4":
        fgprobs['4th'] = fgprobs['4th'] + 1
      
      if dist != '':
        if int(dist) <= 10:
          fgprobs[dist] = fgprobs[dist] + 1
        elif int(dist) <= 20:
          fgprobs['11-20'] = fgprobs['11-20'] + 1
        else:
          fgprobs['20+'] = fgprobs['20+'] + 1
        """
        elif int(dist) <= 15:
          fgprobs['11-15'] = fgprobs['11-15'] + 1
        elif int(dist) <= 20:
          fgprobs['16-20'] = fgprobs['16-20'] + 1
        """
      else: fgprobs['2'] = fgprobs['2'] + 1

      lineint = 0
      yrdinfo = yrdline.split(" ")
      if team in yrdline:
        lineint = int(yrdinfo[1])
        lineint = lineint // 10
        if (lineint == 0):
          fgprobs['yd0'] = fgprobs['yd0'] + 1
        elif (lineint == 1):
          fgprobs['yd1'] = fgprobs['yd1'] + 1
        elif (lineint == 2):
          fgprobs['yd2'] = fgprobs['yd2'] + 1
        elif (lineint == 3):
          fgprobs['yd3'] = fgprobs['yd3'] + 1
        else:
          fgprobs['yd4'] = fgprobs['yd4'] + 1
      else:
        first = yrdinfo[0]
        if first == '50':
          fgprobs['yd5'] = fgprobs['yd5'] + 1
        elif first == '':
          fgprobs['yd2PT'] = fgprobs['yd2PT'] + 1
        else:
          lineint = int(yrdinfo[1])
          if (lineint >= 45):
            fgprobs['yd5'] = fgprobs['yd5'] + 1
          elif (lineint >= 40):
            fgprobs['yd6'] = fgprobs['yd6'] + 1
          elif (lineint >= 35):
            fgprobs['yd7'] = fgprobs['yd7'] + 1
          elif (lineint >= 30):
            fgprobs['yd8'] = fgprobs['yd8'] + 1
          elif (lineint >= 25):
            fgprobs['yd9'] = fgprobs['yd9'] + 1
          elif (lineint >= 20):
            fgprobs['yd10'] = fgprobs['yd10'] + 1
          elif (lineint >= 15):
            fgprobs['yd11'] = fgprobs['yd11'] + 1
          elif (lineint >= 10):
            fgprobs['yd12'] = fgprobs['yd12'] + 1
          elif (lineint >= 5):
            fgprobs['yd13'] = fgprobs['yd13'] + 1
          else:
            fgprobs['yd14'] = fgprobs['yd14'] + 1

      scorediff = 0
      homescore = int(homescr)
      awayscore = int(awyscr)
      if (home == "True"):
        scorediff = homescore - awayscore
      else:
        scorediff = awayscore - homescore
      if (scorediff <= -15):
        fgprobs['diff-5'] = fgprobs['diff-5'] + 1
      elif (scorediff <= -11):
        fgprobs['diff-4'] = fgprobs['diff-4'] + 1
      elif (scorediff <= -8):
        fgprobs['diff-3'] = fgprobs['diff-3'] + 1
      elif (scorediff <= -4):
        fgprobs['diff-2'] = fgprobs['diff-2'] + 1
      elif (scorediff <= -1):
        fgprobs['diff-1'] = fgprobs['diff-1'] + 1
      elif (scorediff == 0):
        fgprobs['diff0'] = fgprobs['diff0'] + 1
      elif (scorediff <= 3):
        fgprobs['diff1'] = fgprobs['diff1'] + 1
      elif (scorediff <= 7):
        fgprobs['diff2'] = fgprobs['diff2'] + 1
      elif (scorediff <= 10):
        fgprobs['diff3'] = fgprobs['diff3'] + 1
      elif (scorediff <= 14):
        fgprobs['diff4'] = fgprobs['diff4'] + 1
      else: 
        fgprobs['diff5'] = fgprobs['diff5'] + 1
     
       
    elif y == "punt":   
      numpunts += 1

      timeleft = 0
      minute = time.split(":")
      if quarter == "OT":
        timeleft = "OT"
      else:
        qint = int(quarter)
        timeleft = (4 - qint) * 15
        if (qint == 2) or (qint == 4):
          if minute[0] != '':
            if int(minute[0]) <= 5:
              timeleft += int(minute[0])
            else: timeleft += 6
      #if "min:"+str(timeleft) in puntprobs.keys():
      puntprobs['min:'+str(timeleft)] = puntprobs['min:'+str(timeleft)] + 1
      #else:
      #  puntprobs['min:'+str(timeleft)] = 1
      
      if down == "1":
        puntprobs['1st'] = puntprobs['1st'] + 1
      elif down == "2": 
        puntprobs['2nd'] = puntprobs['2nd'] + 1
      elif down == "3":
        puntprobs['3rd'] = puntprobs['3rd'] + 1
      elif down == "4":
        puntprobs['4th'] = puntprobs['4th'] + 1
      
      if dist != '':
        if int(dist) <= 10:
          puntprobs[dist] = puntprobs[dist] + 1
        elif int(dist) <= 20:
          puntprobs['11-20'] = puntprobs['11-20'] + 1
        else:
          puntprobs['20+'] = puntprobs['20+'] + 1
        """
        elif int(dist) <= 15:
          puntprobs['11-15'] = puntprobs['11-15'] + 1
        elif int(dist) <= 20:
          puntprobs['16-20'] = puntprobs['16-20'] + 1
        """
      else: puntprobs['2'] = puntprobs['2'] + 1

      lineint = 0
      yrdinfo = yrdline.split(" ")
      if team in yrdline:
        lineint = int(yrdinfo[1])
        lineint = lineint // 10
        if (lineint == 0):
          puntprobs['yd0'] = puntprobs['yd0'] + 1
        elif (lineint == 1):
          puntprobs['yd1'] = puntprobs['yd1'] + 1
        elif (lineint == 2):
          puntprobs['yd2'] = puntprobs['yd2'] + 1
        elif (lineint == 3):
          puntprobs['yd3'] = puntprobs['yd3'] + 1
        else:
          puntprobs['yd4'] = puntprobs['yd4'] + 1
      else:
        first = yrdinfo[0]
        if first == '50':
          puntprobs['yd5'] = puntprobs['yd5'] + 1
        elif first == '':
          puntprobs['yd2PT'] = puntprobs['yd2PT'] + 1
        else:
          lineint = int(yrdinfo[1])
          if (lineint >= 45):
            puntprobs['yd5'] = puntprobs['yd5'] + 1
          elif (lineint >= 40):
            puntprobs['yd6'] = puntprobs['yd6'] + 1
          elif (lineint >= 35):
            puntprobs['yd7'] = puntprobs['yd7'] + 1
          elif (lineint >= 30):
            puntprobs['yd8'] = puntprobs['yd8'] + 1
          elif (lineint >= 25):
            puntprobs['yd9'] = puntprobs['yd9'] + 1
          elif (lineint >= 20):
            puntprobs['yd10'] = puntprobs['yd10'] + 1
          elif (lineint >= 15):
            puntprobs['yd11'] = puntprobs['yd11'] + 1
          elif (lineint >= 10):
            puntprobs['yd12'] = puntprobs['yd12'] + 1
          elif (lineint >= 5):
            puntprobs['yd13'] = puntprobs['yd13'] + 1
          else:
            puntprobs['yd14'] = puntprobs['yd14'] + 1

      scorediff = 0
      homescore = int(homescr)
      awayscore = int(awyscr)
      if (home == "True"):
        scorediff = homescore - awayscore
      else:
        scorediff = awayscore - homescore
      if (scorediff <= -15):
        puntprobs['diff-5'] = puntprobs['diff-5'] + 1
      elif (scorediff <= -11):
        puntprobs['diff-4'] = puntprobs['diff-4'] + 1
      elif (scorediff <= -8):
        puntprobs['diff-3'] = puntprobs['diff-3'] + 1
      elif (scorediff <= -4):
        puntprobs['diff-2'] = puntprobs['diff-2'] + 1
      elif (scorediff <= -1):
        puntprobs['diff-1'] = puntprobs['diff-1'] + 1
      elif (scorediff == 0):
        puntprobs['diff0'] = puntprobs['diff0'] + 1
      elif (scorediff <= 3):
        puntprobs['diff1'] = puntprobs['diff1'] + 1
      elif (scorediff <= 7):
        puntprobs['diff2'] = puntprobs['diff2'] + 1
      elif (scorediff <= 10):
        puntprobs['diff3'] = puntprobs['diff3'] + 1
      elif (scorediff <= 14):
        puntprobs['diff4'] = puntprobs['diff4'] + 1
      else: 
        puntprobs['diff5'] = puntprobs['diff5'] + 1
     
       
    else:
      numruns += 1
      
      timeleft = 0
      minute = time.split(":")
      if quarter == "OT":
        timeleft = "OT"
        #timeleft = minute[0]
      else:
        qint = int(quarter)
        timeleft = (4 - qint) * 15
        if (qint == 2) or (qint == 4):
          if minute == '':
            if int(minute[0]) <= 5:
              timeleft += int(minute[0])
            else: timeleft += 6
      #if "min:"+str(timeleft) in runprobs.keys():
      runprobs['min:'+str(timeleft)] = runprobs['min:'+str(timeleft)] + 1
      #else:
      #  runprobs['min:'+str(timeleft)] = 1
     
      if down == "1":
        runprobs['1st'] = runprobs['1st'] + 1
      elif down == "2": 
        runprobs['2nd'] = runprobs['2nd'] + 1
      elif down == "3":
        runprobs['3rd'] = runprobs['3rd'] + 1
      elif down == "4":
        runprobs['4th'] = runprobs['4th'] + 1

      if dist != '':
        if int(dist) <= 10:
          runprobs[dist] = runprobs[dist] + 1
        elif int(dist) <= 20:
          runprobs['11-20'] = runprobs['11-20'] + 1 
        else:
          runprobs['20+'] = runprobs['20+'] + 1
        """
        elif int(dist) <= 15:
          runprobs['11-15'] = runprobs['11-15'] + 1
        elif int(dist) <= 20:
          runprobs['16-20'] = runprobs['16-20'] + 1
        """
      else:
        runprobs['2'] = runprobs['2'] + 1

      lineint = 0
      yrdinfo = yrdline.split(" ")
      if team in yrdline:
        lineint = int(yrdinfo[1])
        lineint = lineint // 10
        if (lineint == 0):
          runprobs['yd0'] = runprobs['yd0'] + 1
        elif (lineint == 1):
          runprobs['yd1'] = runprobs['yd1'] + 1
        elif (lineint == 2):
          runprobs['yd2'] = runprobs['yd2'] + 1
        elif (lineint == 3):
          runprobs['yd3'] = runprobs['yd3'] + 1
        else:
          runprobs['yd4'] = runprobs['yd4'] + 1
      else:
        first = yrdinfo[0]
        if first == '50':
          runprobs['yd5'] = runprobs['yd5'] + 1
        elif first == '':
          runprobs['yd2PT'] = runprobs['yd2PT'] + 1
        else:
          lineint = int(yrdinfo[1])
          if (lineint >= 45):
            runprobs['yd5'] = runprobs['yd5'] + 1
          elif (lineint >= 40):
            runprobs['yd6'] = runprobs['yd6'] + 1
          elif (lineint >= 35):
            runprobs['yd7'] = runprobs['yd7'] + 1
          elif (lineint >= 30):
            runprobs['yd8'] = runprobs['yd8'] + 1
          elif (lineint >= 25):
            runprobs['yd9'] = runprobs['yd9'] + 1
          elif (lineint >= 20):
            runprobs['yd10'] = runprobs['yd10'] + 1
          elif (lineint >= 15):
            runprobs['yd11'] = runprobs['yd11'] + 1
          elif (lineint >= 10):
            runprobs['yd12'] = runprobs['yd12'] + 1
          elif (lineint >= 5):
            runprobs['yd13'] = runprobs['yd13'] + 1
          else:
            runprobs['yd14'] = runprobs['yd14'] + 1

      scorediff = 0
      homescore = int(homescr)
      awayscore = int(awyscr)
      if (home == "True"):
        scorediff = homescore - awayscore
      else:
        scorediff = awayscore - homescore
      if (scorediff <= -15):
        runprobs['diff-5'] = runprobs['diff-5'] + 1
      elif (scorediff <= -11):
        runprobs['diff-4'] = runprobs['diff-4'] + 1
      elif (scorediff <= -8):
        runprobs['diff-3'] = runprobs['diff-3'] + 1
      elif (scorediff <= -4):
        runprobs['diff-2'] = runprobs['diff-2'] + 1
      elif (scorediff <= -1):
        runprobs['diff-1'] = runprobs['diff-1'] + 1
      elif (scorediff == 0):
        runprobs['diff0'] = runprobs['diff0'] + 1
      elif (scorediff <= 3):
        runprobs['diff1'] = runprobs['diff1'] + 1
      elif (scorediff <= 7):
        runprobs['diff2'] = runprobs['diff2'] + 1
      elif (scorediff <= 10):
        runprobs['diff3'] = runprobs['diff3'] + 1
      elif (scorediff <= 14):
        runprobs['diff4'] = runprobs['diff4'] + 1
      else: 
        runprobs['diff5'] = runprobs['diff5'] + 1
      
              
  totalplays = len(examples)
  passprobability = numpasses / float(totalplays)
  runprobability = numruns / float(totalplays)
  fgprobability = numfgs / float(totalplays)
  puntprobability = numpunts / float(totalplays) 

  for key, value in passprobs.iteritems():
    divisor = float(numpasses)
    if "min" in key:
      divisor += (16 * laplace)
    elif ("1st" == key) or ("2nd" == key) or ("3rd" == key) or ("4th" == key):
      divisor += (4 * laplace)
    elif "yd" in key:
      divisor += (16 * laplace)
    elif "diff" in key:
      divisor += (11 * laplace)
    else:
      divisor += (12 * laplace)
    value = value / divisor
    passprobs[key] = value
  for key, value in runprobs.iteritems():
    divisor = float(numruns)
    if "min" in key:
      divisor += (16 * laplace)
    elif ("1st" == key) or ("2nd" == key) or ("3rd" == key) or ("4th" == key):
      divisor += (4 * laplace)
    elif "yd" in key:
      divisor += (16 * laplace)
    elif "diff" in key:
      divisor += (11 * laplace)
    else:
      divisor += (12 * laplace)
    value = value / divisor
    runprobs[key] = value
  for key, value in fgprobs.iteritems():
    divisor = float(numfgs)
    if "min" in key:
      divisor += (16 * laplace)
    elif ("1st" == key) or ("2nd" == key) or ("3rd" == key) or ("4th" == key):
      divisor += (4 * laplace)
    elif "yd" in key:
      divisor += (16 * laplace)
    elif "diff" in key:
      divisor += (11 * laplace)
    else:
      divisor += (12 * laplace)
    value = value / divisor
    fgprobs[key] = value
  for key, value in puntprobs.iteritems():
    divisor = float(numpunts)
    if "min" in key:
      divisor += (16 * laplace)
    elif ("1st" == key) or ("2nd" == key) or ("3rd" == key) or ("4th" == key):
      divisor += (4 * laplace)
    elif "yd" in key:
      divisor += (16 * laplace)
    elif "diff" in key:
      divisor += (11 * laplace)
    else:
      divisor += (12 * laplace)
    value = value / divisor
    puntprobs[key] = value

  print "Read %d examples from %s" % (len(examples), path)
  return (passprobability, runprobability, fgprobability, puntprobability, passprobs, runprobs, fgprobs, puntprobs)

def predictExamples(validation, probabilities, team, home):
  examples = []
  passprobability = probabilities[0]
  runprobability = probabilities[1]
  fgprobability = probabilities[2]
  puntprobability = probabilities[3]
  passprobs = probabilities[4]
  runprobs = probabilities[5]
  fgprobs = probabilities[6]
  puntprobs = probabilities[7]
  
  for line in validation:
    if ("extra point" not in line) and ("kicks off" not in line):
      if not line.startswith(",,,,,"):
        if (not line.startswith("Quarter")) and (not line.startswith("Overtime")):
          if not line.startswith("\n"): 
            if ",Penalty" not in line:
                line = line + "," + str(home)
                x = line
                if ("spiked" in line) or ("pass incomplete" in line) or ("pass complete" in line) or ("sacked" in line):
                  y = "pass"
                elif ("field goal" in line):
                  y = "field goal"
                elif ("punt" in line):
                  y = "punt"
                else:
                  y = "run"
                examples.append((x, y))
        else:
          if "Detail,"+team in line:
            home = False
          else:
            home = True 
  
  numright = 0
  for x, y in examples:
    characteristics = []
    quarter, time, down, dist, yrdline, play, awyscr, homescr, epb, epa, home = x.split(",")
    
    minute = time.split(":")
    timeleft = 0
    if quarter == "1":
      timeleft = 45
    elif quarter == "2":
      if int(minute[0]) <= 5:
        timeleft = 30 + int(minute[0])
      else: timeleft = 36
    elif quarter == "3":
      timeleft = 15
    else:
      if (minute[0] != ''):
        if int(minute[0]) <= 5:
          timeleft = int(minute[0])
        else: timeleft = 6
    characteristics.append("min:"+str(timeleft))
    
    if down == "1":
      characteristics.append("1st")
    elif down == "2":
      characteristics.append("2nd")
    elif down == "3":
      characteristics.append("3rd")
    else:
      characteristics.append("4th")
    
    if dist != '':
      if int(dist) <= 10:
        characteristics.append(dist)
      elif int(dist) <= 20:
        characteristics.append("11-20")
      else:
        characteristics.append("20+")
      """
      elif int(dist) <= 15:
        characteristics.append("11-15")
      elif int(dist) <= 20:
        characteristics.append("16-20")
      """
    else: characteristics.append("2")
    
    lineint = 0
    yrdinfo = yrdline.split(" ")
    if team in yrdline:
      lineint = int(yrdinfo[1])
      lineint = lineint // 10
      if (lineint == 0):
        characteristics.append('yd0')  
      elif (lineint == 1):
        characteristics.append('yd1')  
      elif (lineint == 2):
        characteristics.append('yd2')  
      elif (lineint == 3):
        characteristics.append('yd3')  
      else:
        characteristics.append('yd4')  
    else:
      first = yrdinfo[0]
      if first == '50':
        characteristics.append('yd5')  
      elif first == '':
        characteristics.append('yd2PT')  
      else:
        lineint = int(yrdinfo[1])
        if (lineint >= 45):
          characteristics.append('yd5')  
        elif (lineint >= 40):
          characteristics.append('yd6')  
        elif (lineint >= 35):
          characteristics.append('yd7')  
        elif (lineint >= 30):
          characteristics.append('yd8')  
        elif (lineint >= 25):
          characteristics.append('yd9')  
        elif (lineint >= 20):
          characteristics.append('yd10')  
        elif (lineint >= 15):
          characteristics.append('yd11')  
        elif (lineint >= 10):
          characteristics.append('yd12')  
        elif (lineint >= 5):
          characteristics.append('yd13')  
        else:
          characteristics.append('yd14')  
 
    scorediff = 0
    homescore = int(homescr)
    awayscore = int(awyscr)
    if (home == "True"):
      scorediff = homescore - awayscore
    else:
      scorediff = awayscore - homescore
    if (scorediff <= -15):
      characteristics.append('diff-5')  
    elif (scorediff <= -11):
      characteristics.append('diff-4')  
    elif (scorediff <= -8):
      characteristics.append('diff-3')  
    elif (scorediff <= -4):
      characteristics.append('diff-2')  
    elif (scorediff <= -1):
      characteristics.append('diff-1')  
    elif (scorediff == 0):
      characteristics.append('diff0')  
    elif (scorediff <= 3):
      characteristics.append('diff1')  
    elif (scorediff <= 7):
      characteristics.append('diff2')  
    elif (scorediff <= 10):
      characteristics.append('diff3')  
    elif (scorediff <= 14):
      characteristics.append('diff4')  
    else: 
      characteristics.append('diff5')  
 

    ppass = 0
    prun = 0
    pfg = 0
    ppunt = 0
    if characteristics[0] in passprobs.keys():
      ppass = passprobability * passprobs[characteristics[0]] * passprobs[characteristics[1]] * passprobs[characteristics[2]] * passprobs[characteristics[3]] * passprobs[characteristics[4]]
    if characteristics[0] in runprobs.keys():
      prun = runprobability * runprobs[characteristics[0]] * runprobs[characteristics[1]] * runprobs[characteristics[2]] * runprobs[characteristics[3]] * runprobs[characteristics[4]]
    if characteristics[0] in fgprobs.keys():
      pfg = fgprobability * fgprobs[characteristics[0]] * fgprobs[characteristics[1]] * fgprobs[characteristics[2]] * fgprobs[characteristics[3]] * fgprobs[characteristics[4]]
    if characteristics[0] in puntprobs.keys():
      ppunt = puntprobability * puntprobs[characteristics[0]] * puntprobs[characteristics[1]] * puntprobs[characteristics[2]] * puntprobs[characteristics[3]] * puntprobs[characteristics[4]]
    
    classification = "none"
    currmax = 0
    if ppass >= 0:
      classification = "pass"
      currmax = ppass
    if prun > currmax:
      classification = "run"
      currmax = prun
    if pfg > currmax:
      classification = "field goal"
      currmax = pfg
    if ppunt > currmax:
      classification = "punt"
   
    if classification == y:
      numright += 1
    else:
      print x
      print "pass:" + str(ppass)
      print "run:" + str(prun)
      print "fg:" + str(pfg)
      print "punt:" + str(ppunt)
  pctcorrect = numright / float(len(examples))
  print pctcorrect  



def runLearner(module, args):
  # Parse command-line arguments
  from optparse import OptionParser
  parser = OptionParser()
  def default(str):
    return str + ' [Default: %default]'
  parser.add_option('-p', '--predict', dest='predict', type='string',
                    help=default('Which predictor to use (SGD with heuristics = sgd, Naive Bayes = bayes, multiple binary classifiers = pivot)'), default="sgd")
  parser.add_option('-z', '--laplace', dest='laplace', type='int',
                    help=default('Number to use for Laplace smoothing for Naive Bayes classifier'), default="0")
  parser.add_option('-t', '--team', dest='team', type='string',
                    help=default('Which team to predict for (SFO, PHI)'), default="SFO")
  parser.add_option('-a', '--approach', dest='approach', type='string',
                    help=default('Which approach to use for multiple-classifier classification (ova, ava)'), default="ova")
  parser.add_option('-1', '--single', dest='single', type='string',
                    help=default('Whether to predict for a single play (yes, no)'), default="no")
  parser.add_option('-l', '--loss', dest='loss', type='string',
                    help=default('Which loss function to use (logistic, hinge, or squared)'), default="logistic")
  parser.add_option('-i', '--initStepSize', dest='initStepSize', type='float',
                    help=default('the initial step size'), default=1)
  parser.add_option('-s', '--stepSizeReduction', dest='stepSizeReduction', type='float',
                    help=default('How much to reduce the step size [0, 1]'), default=0.5)
  parser.add_option('-R', '--numRounds', dest='numRounds', type='int',
                    help=default('Number of passes over the training data'), default=10)
  parser.add_option('-r', '--regularization', dest='regularization', type='float',
                    help=default('The lambda in L2 regularization'), default=2.0)
  parser.add_option('-v', '--verbose', dest='verbose', type='int',
                    help=default('Verbosity level'), default=0)
  options, extra_args = parser.parse_args(args)
  if len(extra_args) != 0:
    print "Ignoring extra arguments:", extra_args

  team = options.team
  if options.single == 'no':
    if options.predict == 'sgd':
      # Read data
      gamedata = open('gamedata'+team+'.txt', 'U')
      validation = open('gamedata_validation'+team+'.txt', 'U')
      trainExamples, trainKickingExamples = readExamples(gamedata, team)
      validationExamples, validationKickingExamples = readExamples(validation, team)


      # Set the loss
      loss = None
      lossGradient = None
      if options.loss == 'squared':
        loss, lossGradient = module.squaredLoss, module.squaredLossGradient
      elif options.loss == 'logistic':
        loss, lossGradient = module.logisticLoss, module.logisticLossGradient
      elif options.loss == 'hinge':
        loss, lossGradient = module.hingeLoss, module.hingeLossGradient
      else:
        raise "Unknown loss function: " + options.loss

      # Set the feature extractor
      featureExtractor =  module.basicFeatureExtractor

      # Learn a model and evaluate
      learner = module.StochasticGradientLearner(featureExtractor)
      learner.learn(trainExamples, validationExamples, trainKickingExamples, validationKickingExamples, loss, lossGradient, options)
      return (learner, options)

    elif options.predict == 'basic':
      gamedata = open('gamedata'+team+'.txt', 'U')
      trainExamples = readPivotExamples(gamedata, team) 
      passcount = 0
      runcount = 0
      fgcount = 0
      puntcount = 0
      for x,y in trainExamples:
        if y == "pass": passcount += 1
        elif y == "run": runcount += 1
        elif y == "field goal": fgcount += 1
        else: puntcount += 1
      prediction = "pass"
      maxcount = passcount
      if runcount > maxcount:
        prediction = "run"
        maxcount = runcount
      if fgcount > maxcount:
        prediction = "field goal"
        maxcount = fgcount
      if puntcount > maxcount:
        prediction = "punt"
        maxcount = puntcount
      validation = open('gamedata_validation'+team+'.txt', 'U')
      validationExamples = readPivotExamples(validation, team)
      numRight = 0
      print prediction
      for x,y in validationExamples:
        if (y == prediction): numRight += 1
      print numRight / float(len(validationExamples))
      
    elif options.predict == 'bayes':
      gamedata = open('gamedata'+team+'.txt', 'U')
      validation = open('gamedata_validation'+team+'.txt', 'U')
      probabilities = buildBayesProbability(gamedata, team, options.laplace)
      predictExamples(validation, probabilities, team, "True")
    elif options.predict == 'pivot':
      gamedata = open('gamedata'+team+'.txt', 'U')
      validation = open('gamedata_validation'+team+'.txt', 'U')
      trainExamples = readPivotExamples(gamedata, team)
      validationExamples = readPivotExamples(validation, team)
      
      loss = None
      lossGradient = None
      if options.loss == 'squared':
        loss, lossGradient = module.squaredLoss, module.squaredLossGradient
      elif options.loss == 'logistic':
        loss, lossGradient = module.logisticLoss, module.logisticLossGradient
      elif options.loss == 'hinge':
        loss, lossGradient = module.hingeLoss, module.hingeLossGradient
      else:
        raise "Unknown loss function: " + options.loss
      
      featureExtractor =  module.pivotFeatureExtractor
      featureExtractor2 = module.basicFeatureExtractor

      # Learn a model and evaluate
      learner = module.StochasticGradientLearner(featureExtractor)
      learner2 = module.StochasticGradientLearner(featureExtractor2)
      passfgexamples = []
      passpuntexamples = []
      passrunexamples = []
      runfgexamples = []
      runpuntexamples = []
      puntfgexamples = []
      for x,y in trainExamples:
        if y == "pass":
          passfgexamples.append((x,y))
          passpuntexamples.append((x,y))
          passrunexamples.append((x,y))
        elif y == "punt":
          passpuntexamples.append((x,y))
          runpuntexamples.append((x,y))
          puntfgexamples.append((x,y))
        elif y == "run":
          passrunexamples.append((x,y))
          runpuntexamples.append((x,y))
          runfgexamples.append((x,y))
        else:
          passfgexamples.append((x,y))
          runfgexamples.append((x,y))
          puntfgexamples.append((x,y))
      if options.approach == "ova":
        wfg = learner.learnPivot(trainExamples, validationExamples, "field goal", loss, lossGradient, options)
        wpunt = learner.learnPivot(trainExamples, validationExamples, "punt", loss, lossGradient, options)
        wrun = learner.learnPivot(trainExamples, validationExamples, "run", loss, lossGradient, options)
        wpass = learner.learnPivot(trainExamples, validationExamples, "pass", loss, lossGradient, options)   

        numMistakes = 0 
        for x,y in validationExamples:
          featx = featureExtractor(x)
          """
          print featx * wfg
          print featx * wpunt
          print featx * wrun
          sumk = exp(featx * wfg) + exp(featx * wpunt) + exp(featx * wrun)
          ppass = 1 / (float)(1 + sumk)
          pfg = exp(featx * wfg) * ppass
          ppunt = exp(featx * wpunt) * ppass
          prun = exp(featx * wrun) * ppass
          """
          pfg = featx * wfg
          ppunt = featx * wpunt
          prun = featx * wrun
          ppass = featx * wpass
          pnum = pfg
          prediction = "field goal"
          if (ppunt > pnum):
            pnum = ppunt
            prediction = "punt"
          if (prun > pnum):
            pnum = prun
            prediction = "run"
          if (ppass > pnum):
            pnum = ppass
            prediction = "pass"
          if (prediction != y):
            numMistakes += 1
            print prediction
            print x
            print y
     
        pctcorr = (len(validationExamples) - numMistakes) / float(len(validationExamples))
        print "Percent correct: " + str(pctcorr)
 
      elif options.approach == "ava":
        wpassfg = learner.learnPivot(passfgexamples, validationExamples, "pass", loss, lossGradient, options)
        wpassrun = learner2.learnPivot(passrunexamples, validationExamples, "pass", loss, lossGradient, options)
        wpasspunt = learner.learnPivot(passpuntexamples, validationExamples, "pass", loss, lossGradient, options)
        wrunfg = learner.learnPivot(runfgexamples, validationExamples, "run", loss, lossGradient, options)
        wrunpunt = learner.learnPivot(runpuntexamples, validationExamples, "run", loss, lossGradient, options)
        wpuntfg = learner.learnPivot(puntfgexamples, validationExamples, "punt", loss, lossGradient, options)
        
        numMistakes = 0 
        for x,y in validationExamples:
          featx = featureExtractor(x)
          featx2 = featureExtractor2(x)
          v1 = featx * wpassfg
          v2 = featx2 * wpassrun
          v3 = featx * wpasspunt
          v4 = featx * wrunfg
          v5 = featx * wrunpunt
          v6 = featx * wpuntfg
          passvotes = 0
          runvotes = 0
          fgvotes = 0
          puntvotes = 0
          if v1 >= 0:
            passvotes += 1
          else:
            fgvotes += 1
          if v2 >= 0:
            passvotes += 1
          else:
            runvotes += 1
          if v3 >= 0:
            passvotes += 1
          else:
            puntvotes += 1
          if v4 >= 0:
            runvotes += 1
          else:
            fgvotes += 1
          if v5 >= 0:
            runvotes += 1
          else:
            puntvotes += 1
          if v6 >= 0:
            puntvotes += 1
          else:
            fgvotes += 1
        
          mostvotes = passvotes
          prediction = "pass"
          if (fgvotes > mostvotes):
            mostvotes = fgvotes
            prediction = "field goal"
          if (puntvotes > mostvotes):
            mostvotes = puntvotes
            prediction = "punt"
          if (runvotes > mostvotes):
            mostvotes = runvotes
            prediction = "run"
          if (prediction != y):
            numMistakes += 1
            print prediction
            print y
            print x
            print passvotes
            print runvotes
            print fgvotes
            print puntvotes
     
        pctcorr = (len(validationExamples) - numMistakes) / float(len(validationExamples))
        print "Percent correct: " + str(pctcorr)
         
      else:
        print "unknown"
    elif options.predict == 'perceptron':
      gamedata = open('gamedata'+team+'.txt', 'U')
      validation = open('gamedata_validation'+team+'.txt', 'U')
      featureExtractor =  module.basicFeatureExtractor
      trainExamples, trainKickingExamples = readExamples(gamedata, team)
      validationExamples, validationKickingExamples = readExamples(validation, team)
      weights = Counter()
      for i in range(0, options.numRounds):
        for x,y in trainExamples:
          featx = featureExtractor(x)
          wx = weights * featx
          prediction = 1
          if (wx < 0): prediction = -1
          if y != prediction:
            weights += featx * y
          print weights
      totalRight = 0
      for x, y in validationExamples:
        featx = featureExtractor(x)
        wx = weights * featx
        prediction = 1
        if (wx < 0): prediction = -1
        if y != prediction:
          if options.verbose != 0: 
            print x
            print wx
        else: totalRight += 1
      for x,y in validationKickingExamples:
        quarter, time, down, dist, yrdline, play, awyscr, homescr, epb, epa, home, team = x.split(",")
        prediction = "field goal"
        if (down == "4"):
          if team in yrdline:
            prediction = "punt"
          else:
            yrdinfo = yrdline.split(" ")
            first = yrdinfo[0]
            if first == "50": prediction = "punt"
            else:
              if int(yrdinfo[1]) >= 40:
                prediction = "punt"
          scorediff = 0
          if home == "True":
            scorediff = int(homescr) - int(awyscr)
          else:
            scorediff = int(awyscr) - int(homescr)
          if (scorediff < -3) and (scorediff >= -14):
            if (quarter == "4"):
              minute = time.split(":")
              if minute:
                if minute[0] <= 3:
                  prediction = "pass"

        if prediction != y:
          if options.verbose != 0:
            print x
            print prediction
            print y
        else: totalRight += 1
         
      pctCorrect = totalRight / float(len(validationExamples) + len(validationKickingExamples))
      print pctCorrect
    else:
      print "no" 
 
  else:       
    if options.predict == 'sgd':
      # Read data
      gamedata = open('gamedata'+team+'.txt', 'U')
      trainExamples, trainKickingExamples = readExamples(gamedata, team)


      # Set the loss
      loss = None
      lossGradient = None
      if options.loss == 'squared':
        loss, lossGradient = module.squaredLoss, module.squaredLossGradient
      elif options.loss == 'logistic':
        loss, lossGradient = module.logisticLoss, module.logisticLossGradient
      elif options.loss == 'hinge':
        loss, lossGradient = module.hingeLoss, module.hingeLossGradient
      else:
        raise "Unknown loss function: " + options.loss

      # Set the feature extractor
      featureExtractor =  module.basicFeatureExtractor
      
      quarter = raw_input("Quarter: ")
      time = raw_input("Time: ")
      down = raw_input("Down: ")
      dist = raw_input("Distance: ")
      yrdline = raw_input("Yard line (SFO 20, OPP 35, etc.): ")
      home = raw_input("Is team home? (y/n): ")
      if home == "y" or home == "Y":
        home = "True"
      else: home = "False"
      team = options.team
      epb = "0"
      epa = "0"
      awyscr = raw_input("Away score: ")
      homescr = raw_input("Home score: ")
      play = "dummy"
      line = quarter + ',' + time + ',' + down + ',' + dist + ',' + yrdline + ',' + play + ',' + awyscr + ',' + homescr + ',' + epb + ',' + epa + ',' + home + ',' + team
      validationExamples = []
      validationKickingExamples = []
      if down == "4":
        validationKickingExamples.append((line, "dummy"))
      else:
        validationExamples.append((line, "dummy"))

      # Learn a model and evaluate
      learner = module.StochasticGradientLearner(featureExtractor)
      learner.learn(trainExamples, validationExamples, trainKickingExamples, validationKickingExamples, loss, lossGradient, options)
         

############################################################

# Return a version of a single function f which memoizes based on ID.
def memoizeById(f):
  cache = {}
  def memf(x):
    i = id(x)
    if i not in cache:
      y = cache[i] = f(x)
    return cache[i]
  return memf

def raiseNotDefined():
  print "Method not implemented: %s" % inspect.stack()[1][3]    
  sys.exit(1)

class Counter(dict):
  """
  A counter keeps track of counts for a set of keys.
  
  The counter class is an extension of the standard python
  dictionary type.  It is specialized to have number values  
  (integers or floats), and includes a handful of additional
  functions to ease the task of counting data.  In particular, 
  all keys are defaulted to have value 0.  Using a dictionary:
  
  a = {}
  print a['test']
  
  would give an error, while the Counter class analogue:
    
  >>> a = Counter()
  >>> print a['test']
  0

  returns the default 0 value. Note that to reference a key 
  that you know is contained in the counter, 
  you can still use the dictionary syntax:
    
  >>> a = Counter()
  >>> a['test'] = 2
  >>> print a['test']
  2
  
  This is very useful for counting things without initializing their counts,
  see for example:
  
  >>> a['blah'] += 1
  >>> print a['blah']
  1
  
  The counter also includes additional functionality useful in implementing
  the classifiers for this assignment.  Two counters can be added,
  subtracted or multiplied together.  See below for details.  They can
  also be normalized and their total count and arg max can be extracted.
  """
  def __getitem__(self, idx):
    self.setdefault(idx, 0)
    return dict.__getitem__(self, idx)

  def incrementAll(self, keys, count):
    """
    Increments all elements of keys by the same count.
    
    >>> a = Counter()
    >>> a.incrementAll(['one','two', 'three'], 1)
    >>> a['one']
    1
    >>> a['two']
    1
    """
    for key in keys:
      self[key] += count
  
  def argMax(self):
    """
    Returns the key with the highest value.
    """
    if len(self.keys()) == 0: return None
    all = self.items()
    values = [x[1] for x in all]
    maxIndex = values.index(max(values))
    return all[maxIndex][0]
  
  def sortedKeys(self):
    """
    Returns a list of keys sorted by their values.  Keys
    with the highest values will appear first.
    
    >>> a = Counter()
    >>> a['first'] = -2
    >>> a['second'] = 4
    >>> a['third'] = 1
    >>> a.sortedKeys()
    ['second', 'third', 'first']
    """
    sortedItems = self.items()
    compare = lambda x, y:  sign(y[1] - x[1])
    sortedItems.sort(cmp=compare)
    return [x[0] for x in sortedItems]
  
  def totalCount(self):
    """
    Returns the sum of counts for all keys.
    """
    return sum(self.values())
  
  def normalize(self):
    """
    Edits the counter such that the total count of all
    keys sums to 1.  The ratio of counts for all keys
    will remain the same. Note that normalizing an empty 
    Counter will result in an error.
    """
    total = float(self.totalCount())
    if total == 0: return
    for key in self.keys():
      self[key] = self[key] / total
      
  def divideAll(self, divisor):
    """
    Divides all counts by divisor
    """
    divisor = float(divisor)
    for key in self:
      self[key] /= divisor

  def copy(self):
    """
    Returns a copy of the counter
    """
    return Counter(dict.copy(self))
  
  def __mul__(self, y):
    if not isinstance(y, Counter):
      # Return the scalar y multiplied by every element of result.
      result = Counter()
      for key in self:
        result[key] = y * self[key]
      return result

    """
    Multiplying two counters gives the dot product of their vectors where
    each unique label is a vector element.
    
    >>> a = Counter()
    >>> b = Counter()
    >>> a['first'] = -2
    >>> a['second'] = 4
    >>> b['first'] = 3
    >>> b['second'] = 5
    >>> a['third'] = 1.5
    >>> a['fourth'] = 2.5
    >>> a * b
    14
    """
    sum = 0
    x = self
    if len(x) > len(y):
      x,y = y,x
    for key in x:
      if key not in y:
        continue
      sum += x[key] * y[key]      
    return sum
      
  def __radd__(self, y):
    """
    Adding another counter to a counter increments the current counter
    by the values stored in the second counter.
    
    >>> a = Counter()
    >>> b = Counter()
    >>> a['first'] = -2
    >>> a['second'] = 4
    >>> b['first'] = 3
    >>> b['third'] = 1
    >>> a += b
    >>> a['first']
    1
    """ 
    for key, value in y.items():
      self[key] += value   
      
  def __add__( self, y ):
    """
    Adding two counters gives a counter with the union of all keys and
    counts of the second added to counts of the first.
    
    >>> a = Counter()
    >>> b = Counter()
    >>> a['first'] = -2
    >>> a['second'] = 4
    >>> b['first'] = 3
    >>> b['third'] = 1
    >>> (a + b)['first']
    1
    """
    addend = Counter()
    for key in self:
      if key in y:
        addend[key] = self[key] + y[key]
      else:
        addend[key] = self[key]
    for key in y:
      if key in self:
        continue
      addend[key] = y[key]
    return addend
    
  def __sub__( self, y ):
    """
    Subtracting a counter from another gives a counter with the union of all keys and
    counts of the second subtracted from counts of the first.
    
    >>> a = Counter()
    >>> b = Counter()
    >>> a['first'] = -2
    >>> a['second'] = 4
    >>> b['first'] = 3
    >>> b['third'] = 1
    >>> (a - b)['first']
    -5
    """      
    addend = Counter()
    for key in self:
      if key in y:
        addend[key] = self[key] - y[key]
      else:
        addend[key] = self[key]
    for key in y:
      if key in self:
        continue
      addend[key] = -1 * y[key]
    return addend
