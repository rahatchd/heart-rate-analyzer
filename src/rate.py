from __future__ import division
import datetime as dt
import csv
import sys
from progress import Progress


def median(x):
    """
    Compute the median of a given list

    :param x: given list
    :return: median of list
    """
    if len(x) < 3:
        return x[0]
    x = sorted(x)
    even = len(x) % 2 == 0
    return (x[len(x) // 2 + 1] + even * x[len(x) // 2]) / (even + 1.)


def aggregate(datum, bouts, today, bands):
    """
    Aggregate data into a dict

    :param datum: list containing all heart rates
    :param bouts: list of lists containing different band bouts
    :param today: date of current datum
    :param bands: list of bands
    :return: data aggregated into a dict
    """
    datum = sorted(datum)
    bout_times = [x['time'].total_seconds() for x in bouts]
    row = {'Date': today,
           'Number of Data Points': len(datum),
           'Mean HR Overall': round(sum(datum) / len(datum), 1),
           'Median HR Overall': median(datum),
           'Min HR Overall': datum[0],
           'Max HR Overall': datum[-1]}

    for i in range(4):
        if len(bouts[i]['rates']) > 0:
            row.update({
                'Number of Bouts at HR {}'.format(bands[i]): bouts[i]['count'],
                'Total Time Spent (min) at HR {}'.format(bands[i]): round(bout_times[i] / 60, 1),
                'Mean HR for Time Spent (min) at HR {}'.format(bands[i]): round(
                    sum(bouts[i]['rates']) / len(bouts[i]['rates']),
                    1),
                'Median HR for Time Spent (min) at HR {}'.format(bands[i]): median(sorted(bouts[i]['rates'])),
                'Min HR for Time Spent (min) at HR {}'.format(bands[i]): min(bouts[i]['rates'])})
        else:
            row.update({'Number of Bouts at HR {}'.format(bands[i]): 'NO DATA',
                        'Total Time Spent (min) at HR {}'.format(bands[i]): 'NO DATA',
                        'Mean HR for Time Spent (min) at HR {}'.format(bands[i]): 'NO DATA',
                        'Median HR for Time Spent (min) at HR {}'.format(bands[i]): 'NO DATA',
                        'Min HR for Time Spent (min) at HR {}'.format(bands[i]): 'NO DATA'})
    return row


def analyze(raw, patient, age, shell):
    """
    Perform analysis on heart rate data and store analysis in a csv

    :param raw: heart rate data
    :param patient: patient ID
    :param age: patient age
    :param shell: program terminal
    :return: none
    """
    # constants
    interval = dt.timedelta(minutes=10)
    bands = ['>= 80%', '< 80% & >= 60% & < 80%', '>= 40% & < 60%', '< 40%']
    stats = ['Date', 'Number of Data Points', 'Mean HR Overall', 'Median HR Overall', 'Min HR Overall',
             'Max HR Overall',
             'Number of Bouts at HR {}'.format(bands[0]), 'Total Time Spent (min) at HR {}'.format(bands[0]),
             'Mean HR for Time Spent (min) at HR {}'.format(bands[0]),
             'Median HR for Time Spent (min) at HR {}'.format(bands[0]),
             'Min HR for Time Spent (min) at HR {}'.format(bands[0]),

             'Number of Bouts at HR {}'.format(bands[1]), 'Total Time Spent (min) at HR {}'.format(bands[1]),
             'Mean HR for Time Spent (min) at HR {}'.format(bands[1]),
             'Median HR for Time Spent (min) at HR {}'.format(bands[1]),
             'Min HR for Time Spent (min) at HR {}'.format(bands[1]),

             'Number of Bouts at HR {}'.format(bands[2]), 'Total Time Spent (min) at HR {}'.format(bands[2]),
             'Mean HR for Time Spent (min) at HR {}'.format(bands[2]),
             'Median HR for Time Spent (min) at HR {}'.format(bands[2]),
             'Min HR for Time Spent (min) at HR {}'.format(bands[2]),

             'Number of Bouts at HR {}'.format(bands[3]), 'Total Time Spent (min) at HR {}'.format(bands[3]),
             'Mean HR for Time Spent (min) at HR {}'.format(bands[3]),
             'Median HR for Time Spent (min) at HR {}'.format(bands[3]),
             'Min HR for Time Spent (min) at HR {}'.format(bands[3])]

    # patient heart rate params
    pred = 220 - age
    high = 0.8 * pred
    mid = 0.6 * pred
    low = 0.4 * pred
    bound = [[high, 1000], [mid, high], [low, mid], [-1, low]]

    data = []
    datum = []  # stores all heart rate data for one day
    bout = [[], [], [], []]  # stores bouts of heart rate data for each band
    bouts = [{'time': dt.timedelta(), 'rates': [], 'count': 0}, {'time': dt.timedelta(), 'rates': [], 'count': 0},
             {'time': dt.timedelta(), 'rates': [], 'count': 0}, {'time': dt.timedelta(), 'rates': [], 'count': 0}]

    # first row of data
    today = raw[0, 0].date()
    start = raw[0, 0]
    end = raw[0, 0]
    rate = raw[0, 1]
    band = (rate >= high) * 0 + (mid <= rate < high) * 1 + (low <= rate < mid) * 2 + (rate < low) * 3

    print 'analyzing data...'
    progress = Progress(len(raw), shell)

    for day, rate in raw:
        if day.date() == today:
            datum.append(rate)
            if bound[band][0] <= rate < bound[band][1]:
                bout[band].append(rate)
                end = day
            elif end - start < interval:
                if len(bout[band]) > 0:
                    bout[band] = []
                start = day
                end = day
            else:
                bouts[band]['time'] += (end - start)
                bouts[band]['rates'].extend(bout[band])
                bouts[band]['count'] += 1

                bout[band] = []
                start = day
                end = day

            band = (rate >= high) * 0 + (mid <= rate < high) * 1 + (low <= rate < mid) * 2 + (rate < low) * 3

        else:
            row = aggregate(datum, bouts, today, bands)
            data.append(row)

            datum = []
            today = day.date()

            bout = [[], [], [], []]
            start = day
            end = day

            bouts = [{'time': dt.timedelta(), 'rates': [], 'count': 0},
                     {'time': dt.timedelta(), 'rates': [], 'count': 0},
                     {'time': dt.timedelta(), 'rates': [], 'count': 0},
                     {'time': dt.timedelta(), 'rates': [], 'count': 0}]

        progress.step()
        sys.stdout.write('{}\r'.format(progress))
        sys.stdout.flush()

    row = aggregate(datum, bouts, today, bands)
    data.append(row)

    sys.stdout.write('{}\n'.format(progress))
    print '{s.bold}data analyzed{s.normal}'.format(s=shell)
    print ''

    progress = Progress(len(data), shell)
    print 'storing analysis in <analysis/{}>...'.format(patient + '.csv')
    with open('analysis/' + patient + '.csv', 'w+') as f:
        writer = csv.DictWriter(f, stats)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
            progress.step()
            sys.stdout.write('{}\r'.format(progress))
            sys.stdout.flush()

    sys.stdout.write('{}\n'.format(progress))
    print '{s.bold}analysis stored{s.normal}'.format(s=shell)
    print ''
