import numpy as np
import pandas as pd
import time
import datetime
import os


def main(name):
    print(name)

    nValues = [2, 3, 4, 5, 6, 7]
    numberOfIterations = 1000
    numberOfDays = 100
    probabilityOfPartFailure = {1: 0.02, 2: 0.05, 3: 0.10, 4: 0.12, 5: 0.15, 6: 0.20, 7: 0.25}
    poissonMean = 8.2
    costPerCompressorPerDay = 80
    partReplacementCost = 500
    queueCrowdLimit = 15

    outputFolder = '/home/bgunyel/Output/monte_carlo/'

    startTime = time.time()

    scenarioDf = {'Regular Replacement Duration': nValues,
                  'Average Total Cost': np.zeros(len(nValues)),
                  'StdDev Total Cost': np.zeros(len(nValues)),
                  'Average Number of Compressors in Queue': np.zeros(len(nValues)),
                  'StdDev Number of Compressors in Queue': np.zeros(len(nValues)),
                  'Average Number of Scheduled Replacements': np.zeros(len(nValues)),
                  'StdDev Number of Scheduled Replacements': np.zeros(len(nValues)),
                  'Average Number of Part Failures': np.zeros(len(nValues)),
                  'StdDev Number of Part Failures': np.zeros(len(nValues)),
                  'Probability of Crowded Queue': np.zeros(len(nValues))}

    iterationDf = {'Day of Use': np.zeros(numberOfDays),
                   'Did Part Fail': - 1 * np.ones(numberOfDays),
                   'Scheduled Replacement': - 1 * np.ones(numberOfDays),
                   'Number of Compressors in Queue': np.zeros(numberOfDays),
                   'Is Queue Crowded': np.zeros(numberOfDays)}

    simDf = {'Total Cost': np.zeros(numberOfIterations),
             'Average Number Of Compressors in Queue': np.zeros(numberOfIterations),
             'Number of Scheduled Replacements': np.zeros(numberOfIterations),
             'Number of Part Failures': np.zeros(numberOfIterations),
             'Number of Crowded Days': np.zeros(numberOfIterations)}

    for idx, n in enumerate(nValues):

        scenarioStartTime = time.time()

        for iteration in range(numberOfIterations):

            totalCost = 0
            numberOfCompressorsInQueue = 0
            dayOfUse = 0

            for day in range(numberOfDays):
                dayOfUse += 1
                compressorsReceived = np.random.poisson(poissonMean, 1)
                numberOfCompressorsInQueue += compressorsReceived
                didPartFail = np.random.binomial(1, probabilityOfPartFailure[min(dayOfUse, 7)])
                scheduledReplacement = 0

                iterationDf['Day of Use'][day] = dayOfUse
                iterationDf['Did Part Fail'][day] = didPartFail

                numberOfRepairedCompressors = -1
                if didPartFail:
                    numberOfRepairedCompressors = np.random.randint(low=0, high=10)
                    totalCost += partReplacementCost
                    dayOfUse = 0
                else:
                    numberOfRepairedCompressors = 10

                    if dayOfUse == n:  # Regular Replacement
                        dayOfUse = 0
                        totalCost += partReplacementCost
                        scheduledReplacement = 1

                numberOfRepairedCompressors = min(numberOfCompressorsInQueue, numberOfRepairedCompressors)
                numberOfCompressorsInQueue = numberOfCompressorsInQueue - numberOfRepairedCompressors
                totalCost += numberOfCompressorsInQueue * costPerCompressorPerDay

                iterationDf['Scheduled Replacement'][day] = scheduledReplacement
                iterationDf['Number of Compressors in Queue'][day] = numberOfCompressorsInQueue

            # One iteration (100-day) is complete

            iterationDf['Is Queue Crowded'] = np.zeros((numberOfDays, 1))
            iterationDf['Is Queue Crowded'][iterationDf['Number of Compressors in Queue'] >= queueCrowdLimit] = 1

            simDf['Total Cost'][iteration] = totalCost
            simDf['Average Number Of Compressors in Queue'][iteration] = iterationDf[
                'Number of Compressors in Queue'].mean()
            simDf['Number of Scheduled Replacements'][iteration] = iterationDf['Scheduled Replacement'].sum()
            simDf['Number of Part Failures'][iteration] = iterationDf['Did Part Fail'].sum()
            simDf['Number of Crowded Days'][iteration] = iterationDf['Is Queue Crowded'].sum()

        # One scenario (1000-iteration) is complete

        scenarioDf['Regular Replacement Duration'][idx] = n
        scenarioDf['Average Total Cost'][idx] = simDf['Total Cost'].mean()
        scenarioDf['StdDev Total Cost'][idx] = simDf['Total Cost'].std()
        scenarioDf['Average Number of Compressors in Queue'][idx] = simDf['Average Number Of Compressors in Queue'].mean()
        scenarioDf['StdDev Number of Compressors in Queue'][idx] = simDf[
            'Average Number Of Compressors in Queue'].std()
        scenarioDf['Average Number of Scheduled Replacements'][idx] = simDf['Number of Scheduled Replacements'].mean()
        scenarioDf['StdDev Number of Scheduled Replacements'][idx] = simDf['Number of Scheduled Replacements'].std()
        scenarioDf['Average Number of Part Failures'][idx] = simDf['Number of Part Failures'].mean()
        scenarioDf['StdDev Number of Part Failures'][idx] = simDf['Number of Part Failures'].std()
        scenarioDf['Probability of Crowded Queue'][idx] = simDf['Number of Crowded Days'].mean() / numberOfDays

        scenarioEndTime = time.time()
        print(f'Scenario {idx} took {scenarioEndTime - scenarioStartTime} seconds')

    endTime = time.time()
    print(f'Total Elapsed Time: {endTime - startTime} seconds')

    scenarioTable = pd.DataFrame(data=scenarioDf)
    timeStr = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')
    xlsFilePath = os.path.join(outputFolder, 'engine_compressors_' + timeStr + '.xlsx')
    excelWriter = pd.ExcelWriter(xlsFilePath)
    scenarioTable.to_excel(excelWriter, 'Scenarios')
    excelWriter.save()


if __name__ == '__main__':
    main('Engine Compressors Replacement Simulation')
