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

    scenarioDf = pd.DataFrame(data={'Regular Replacement Duration': nValues,
                                    'Average Total Cost': np.zeros(len(nValues)),
                                    'Average Number of Compressors in Queue': np.zeros(len(nValues)),
                                    'Number of Scheduled Replacements': np.zeros(len(nValues)),
                                    'Number of Part Failures': np.zeros(len(nValues)),
                                    'Probability of Crowded Queue': np.zeros(len(nValues))})

    for idx, n in enumerate(nValues):

        scenarioStartTime = time.time()

        simDf = pd.DataFrame(data={'Total Cost': np.zeros(numberOfIterations),
                                   'Average Number Of Compressors in Queue': np.zeros(numberOfIterations),
                                   'Number of Scheduled Replacements': np.zeros(numberOfIterations),
                                   'Number of Part Failures': np.zeros(numberOfIterations),
                                   'Number of Crowded Days': np.zeros(numberOfIterations)})

        for iteration in range(numberOfIterations):

            totalCost = 0
            numberOfCompressorsInQueue = 0
            dayOfUse = 0

            df = pd.DataFrame(data={'Day of Use': np.zeros(numberOfDays),
                                    'Did Part Fail': - 1 * np.ones(numberOfDays),
                                    'Scheduled Replacement': - 1 * np.ones(numberOfDays),
                                    'Number of Compressors in Queue': np.zeros(numberOfDays)})

            for day in range(numberOfDays):
                dayOfUse += 1
                compressorsReceived = np.random.poisson(poissonMean, 1)
                numberOfCompressorsInQueue += compressorsReceived
                didPartFail = np.random.binomial(1, probabilityOfPartFailure[min(dayOfUse, 7)])
                scheduledReplacement = 0

                df.loc[day, 'Day of Use'] = dayOfUse
                df.loc[day, 'Did Part Fail'] = didPartFail

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

                df.loc[day, 'Scheduled Replacement'] = scheduledReplacement
                df.loc[day, 'Number of Compressors in Queue'] = numberOfCompressorsInQueue

            # One iteration (100-day) is complete

            df['Is Queue Crowded'] = np.zeros((numberOfDays, 1))
            df.loc[df['Number of Compressors in Queue'] >= queueCrowdLimit, 'Is Queue Crowded'] = 1

            simDf.loc[iteration, 'Total Cost'] = totalCost
            simDf.loc[iteration, 'Average Number Of Compressors in Queue'] = df['Number of Compressors in Queue'].mean()
            simDf.loc[iteration, 'Number of Scheduled Replacements'] = df['Scheduled Replacement'].sum()
            simDf.loc[iteration, 'Number of Part Failures'] = df['Did Part Fail'].sum()
            simDf.loc[iteration, 'Number of Crowded Days'] = df['Is Queue Crowded'].sum()

        # One scenario (1000-iteration) is complete

        scenarioDf.loc[idx, 'Regular Replacement Duration'] = n
        scenarioDf.loc[idx, 'Average Total Cost'] = simDf['Total Cost'].mean()
        scenarioDf.loc[idx, 'Average Number of Compressors in Queue'] = simDf[
            'Average Number Of Compressors in Queue'].mean()
        scenarioDf.loc[idx, 'Number of Scheduled Replacements'] = simDf['Number of Scheduled Replacements'].mean()
        scenarioDf.loc[idx, 'Number of Part Failures'] = simDf['Number of Part Failures'].mean()
        scenarioDf.loc[idx, 'Probability of Crowded Queue'] = simDf['Number of Crowded Days'].mean() / numberOfDays

        scenarioEndTime = time.time()
        print(f'Scenario {idx} took {scenarioEndTime - scenarioStartTime} seconds')

    endTime = time.time()
    print(f'Total Elapsed Time: {endTime - startTime} seconds')

    timeStr = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')
    xlsFilePath = os.path.join(outputFolder, 'engine_compressors_' + timeStr + '.xlsx')
    excelWriter = pd.ExcelWriter(xlsFilePath)
    scenarioDf.to_excel(excelWriter, 'Scenarios')
    excelWriter.save()


if __name__ == '__main__':
    main('Engine Compressors Replacement Simulation')
