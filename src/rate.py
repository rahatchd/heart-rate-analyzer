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
    return (x[len(x) / 2 + 1] + even * x[len(x) / 2]) / (even + 1.)


def analyze(raw, patient, age, shell):
    """
    Perform analysis on heart rate data and store analysis in a csv

    :param raw: heart rate data
    :param patient: patient ID
    :param age: patient age
    :param shell: terminal in which program is being run
    :return: none
    """
    progress = Progress(len(raw), shell)
    interval = dt.timedelta(minutes=10)
    pred = 220 - age
    high = 0.8 * pred
    mid = 0.6 * pred
    low = 0.4 * pred

    today = raw[0, 0].date()

    datum = []
    data = []

    start = raw[0, 0]
    end = raw[0, 0]

    rate = raw[0, 1]
    band = (rate >= high) * 0 + (mid <= rate < high) * 1 + (low <= rate < mid) * 2 + (rate < low) * 3

    bout = [[], [], [], []]
    bouts = [{'time': dt.timedelta(), 'rates': [], 'count': 0}, {'time': dt.timedelta(), 'rates': [], 'count': 0},
             {'time': dt.timedelta(), 'rates': [], 'count': 0}, {'time': dt.timedelta(), 'rates': [], 'count': 0}]

    stats = ['Date', 'Number of Data Points', 'Mean HR Overall', 'Median HR Overall', 'Min HR Overall',
             'Max HR Overall',
             'Number of Bouts at HR >= 80%', 'Total Time Spent at HR >= 80%', 'Mean HR for Time Spent at HR >= 80%',
             'Median HR for Time Spent at HR >= 80%', 'Min HR for Time Spent at HR >= 80%',

             'Number of Bouts at HR >= 60%', 'Total Time Spent at HR >= 60%', 'Mean HR for Time Spent at HR >= 60%',
             'Median HR for Time Spent at HR >= 60%', 'Min HR for Time Spent at HR >= 60%',

             'Number of Bouts at HR >= 40%', 'Total Time Spent at HR >= 40%', 'Mean HR for Time Spent at HR >= 40%',
             'Median HR for Time Spent at HR >= 40%', 'Min HR for Time Spent at HR >= 40%',

             'Number of Bouts at HR < 40%', 'Total Time Spent at HR < 40%', 'Mean HR for Time Spent at HR < 40%',
             'Median HR for Time Spent at HR < 40%', 'Min HR for Time Spent at HR < 40%']

    print 'analyzing data...'

    for day, rate in raw:
        if day.date() == today:
            datum.append(rate)
            if band == 0:
                if rate >= high:
                    bout[0].append(rate)
                    end = day
                elif end - start < interval:
                    if len(bout[0]) > 0:
                        bout[0] = []
                    start = day
                    end = day
                else:
                    bouts[band]['time'] += (end - start)
                    bouts[band]['rates'].extend(bout[0])
                    bouts[band]['count'] += 1

                    bout[0] = []
                    start = day
                    end = day
            elif band == 1:
                if mid <= rate < high:
                    bout[1].append(rate)
                    end = day
                elif end - start < interval:
                    if len(bout[1]) > 0:
                        bout[1] = []
                    start = day
                    end = day
                else:
                    bouts[band]['time'] += (end - start)
                    bouts[band]['rates'].extend(bout[1])
                    bouts[band]['count'] += 1

                    bout[1] = []
                    start = day
                    end = day
            elif band == 2:
                if low <= rate < mid:
                    bout[2].append(rate)
                    end = day
                elif end - start < interval:
                    if len(bout[2]) > 0:
                        bout[2] = []
                    start = day
                    end = day
                else:
                    bouts[band]['time'] += (end - start)
                    bouts[band]['rates'].extend(bout[2])
                    bouts[band]['count'] += 1

                    bout[2] = []
                    start = day
                    end = day
            elif band == 3:
                if rate < low:
                    bout[3].append(rate)
                    end = day
                elif end - start < interval:
                    if len(bout[3]) > 0:
                        bout[3] = []
                    start = day
                    end = day
                else:
                    bouts[band]['time'] += (end - start)
                    bouts[band]['rates'].extend(bout[3])
                    bouts[band]['count'] += 1

                    bout[3] = []
                    start = day
                    end = day

            band = (rate >= high) * 0 + (mid <= rate < high) * 1 + (low <= rate < mid) * 2 + (rate < low) * 3

        else:
            datum = sorted(datum)
            bout_times = [x['time'].total_seconds() for x in bouts]
            row = {'Date': today,
                   'Number of Data Points': len(datum),
                   'Mean HR Overall': float(sum(datum)) / len(datum),
                   'Median HR Overall': median(datum),
                   'Min HR Overall': datum[0],
                   'Max HR Overall': datum[-1]}

            if len(bouts[0]['rates']) > 0:
                row.update({
                    'Number of Bouts at HR >= 80%': bouts[0]['count'],
                    'Total Time Spent at HR >= 80%': '{} hours {} minutes'.format(bout_times[0] // 3600,
                                                                                  (bout_times[0] % 3600) // 60),
                    'Mean HR for Time Spent at HR >= 80%': sum(bouts[0]['rates']) / len(bouts[0]['rates']),
                    'Median HR for Time Spent at HR >= 80%': median(sorted(bouts[0]['rates'])),
                    'Min HR for Time Spent at HR >= 80%': min(bouts[0]['rates'])})
            else:
                row.update({'Number of Bouts at HR >= 80%': 'NO DATA',
                            'Total Time Spent at HR >= 80%': 'NO DATA',
                            'Mean HR for Time Spent at HR >= 80%': 'NO DATA',
                            'Median HR for Time Spent at HR >= 80%': 'NO DATA',
                            'Min HR for Time Spent at HR >= 80%': 'NO DATA'})

            if len(bouts[1]['rates']) > 0:
                row.update({
                    'Number of Bouts at HR >= 60%': bouts[1]['count'],
                    'Total Time Spent at HR >= 60%': '{} hours {} minutes'.format(bout_times[1] // 3600,
                                                                                  (bout_times[1] % 3600) // 60),
                    'Mean HR for Time Spent at HR >= 60%': sum(bouts[1]['rates']) / len(bouts[1]['rates']),
                    'Median HR for Time Spent at HR >= 60%': median(sorted(bouts[1]['rates'])),
                    'Min HR for Time Spent at HR >= 60%': min(bouts[1]['rates'])})
            else:
                row.update({'Number of Bouts at HR >= 60%': 'NO DATA',
                            'Total Time Spent at HR >= 60%': 'NO DATA',
                            'Mean HR for Time Spent at HR >= 60%': 'NO DATA',
                            'Median HR for Time Spent at HR >= 60%': 'NO DATA',
                            'Min HR for Time Spent at HR >= 60%': 'NO DATA'})

            if len(bouts[2]['rates']) > 0:
                row.update({
                    'Number of Bouts at HR >= 40%': bouts[2]['count'],
                    'Total Time Spent at HR >= 40%': '{} hours {} minutes'.format(bout_times[2] // 3600,
                                                                                  (bout_times[2] % 3600) // 60),
                    'Mean HR for Time Spent at HR >= 40%': sum(bouts[2]['rates']) / len(bouts[2]['rates']),
                    'Median HR for Time Spent at HR >= 40%': median(sorted(bouts[2]['rates'])),
                    'Min HR for Time Spent at HR >= 40%': min(bouts[2]['rates'])})

            else:
                row.update({'Number of Bouts at HR >= 40%': 'NO DATA',
                            'Total Time Spent at HR >= 40%': 'NO DATA',
                            'Mean HR for Time Spent at HR >= 40%': 'NO DATA',
                            'Median HR for Time Spent at HR >= 40%': 'NO DATA',
                            'Min HR for Time Spent at HR >= 40%': 'NO DATA'})

            if len(bouts[3]['rates']) > 0:
                row.update({
                    'Number of Bouts at HR < 40%': bouts[3]['count'],
                    'Total Time Spent at HR < 40%': '{} hours {} minutes'.format(bout_times[3] // 3600,
                                                                                 (bout_times[3] % 3600) // 60),
                    'Mean HR for Time Spent at HR < 40%': sum(bouts[3]['rates']) / len(bouts[3]['rates']),
                    'Median HR for Time Spent at HR < 40%': median(sorted(bouts[3]['rates'])),
                    'Min HR for Time Spent at HR < 40%': min(bouts[3]['rates'])
                })
            else:
                row.update({'Number of Bouts at HR < 40%': 'NO DATA',
                            'Total Time Spent at HR < 40%': 'NO DATA',
                            'Mean HR for Time Spent at HR < 40%': 'NO DATA',
                            'Median HR for Time Spent at HR < 40%': 'NO DATA',
                            'Min HR for Time Spent at HR < 40%': 'NO DATA'})

            data.append(row)

            datum = []
            today = day.date()

            bout = [[], [], [], []]
            start = day
            end = day

            bouts = [{'time': dt.timedelta(), 'rates': [], 'count': 0}, {'time': dt.timedelta(), 'rates': [], 'count': 0},
             {'time': dt.timedelta(), 'rates': [], 'count': 0}, {'time': dt.timedelta(), 'rates': [], 'count': 0}]

        progress.step()
        sys.stdout.write('{}\r'.format(progress))
        sys.stdout.flush()

    datum = sorted(datum)
    bout_times = [x['time'].total_seconds() for x in bouts]
    row = {'Date': today,
           'Number of Data Points': len(datum),
           'Mean HR Overall': float(sum(datum)) / len(datum),
           'Median HR Overall': median(datum),
           'Min HR Overall': datum[0],
           'Max HR Overall': datum[-1]}

    if len(bouts[0]['rates']) > 0:
        row.update({
            'Number of Bouts at HR >= 80%': bouts[0]['count'],
            'Total Time Spent at HR >= 80%': '{} hours {} minutes'.format(bout_times[0] // 3600,
                                                                          (bout_times[0] % 3600) // 60),
            'Mean HR for Time Spent at HR >= 80%': sum(bouts[0]['rates']) / len(bouts[0]['rates']),
            'Median HR for Time Spent at HR >= 80%': median(sorted(bouts[0]['rates'])),
            'Min HR for Time Spent at HR >= 80%': min(bouts[0]['rates'])})
    else:
        row.update({'Number of Bouts at HR >= 80%': 'NO DATA',
                    'Total Time Spent at HR >= 80%': 'NO DATA',
                    'Mean HR for Time Spent at HR >= 80%': 'NO DATA',
                    'Median HR for Time Spent at HR >= 80%': 'NO DATA',
                    'Min HR for Time Spent at HR >= 80%': 'NO DATA'})

    if len(bouts[1]['rates']) > 0:
        row.update({
            'Number of Bouts at HR >= 60%': bouts[1]['count'],
            'Total Time Spent at HR >= 60%': '{} hours {} minutes'.format(bout_times[1] // 3600,
                                                                          (bout_times[1] % 3600) // 60),
            'Mean HR for Time Spent at HR >= 60%': sum(bouts[1]['rates']) / len(bouts[1]['rates']),
            'Median HR for Time Spent at HR >= 60%': median(sorted(bouts[1]['rates'])),
            'Min HR for Time Spent at HR >= 60%': min(bouts[1]['rates'])})
    else:
        row.update({'Number of Bouts at HR >= 60%': 'NO DATA',
                    'Total Time Spent at HR >= 60%': 'NO DATA',
                    'Mean HR for Time Spent at HR >= 60%': 'NO DATA',
                    'Median HR for Time Spent at HR >= 60%': 'NO DATA',
                    'Min HR for Time Spent at HR >= 60%': 'NO DATA'})

    if len(bouts[2]['rates']) > 0:
        row.update({
            'Number of Bouts at HR >= 40%': bouts[2]['count'],
            'Total Time Spent at HR >= 40%': '{} hours {} minutes'.format(bout_times[2] // 3600,
                                                                          (bout_times[2] % 3600) // 60),
            'Mean HR for Time Spent at HR >= 40%': sum(bouts[2]['rates']) / len(bouts[2]['rates']),
            'Median HR for Time Spent at HR >= 40%': median(sorted(bouts[2]['rates'])),
            'Min HR for Time Spent at HR >= 40%': min(bouts[2]['rates'])})

    else:
        row.update({'Number of Bouts at HR >= 40%': 'NO DATA',
                    'Total Time Spent at HR >= 40%': 'NO DATA',
                    'Mean HR for Time Spent at HR >= 40%': 'NO DATA',
                    'Median HR for Time Spent at HR >= 40%': 'NO DATA',
                    'Min HR for Time Spent at HR >= 40%': 'NO DATA'})

    if len(bouts[3]['rates']) > 0:
        row.update({
            'Number of Bouts at HR < 40%': bouts[3]['count'],
            'Total Time Spent at HR < 40%': '{} hours {} minutes'.format(bout_times[3] // 3600,
                                                                         (bout_times[3] % 3600) // 60),
            'Mean HR for Time Spent at HR < 40%': sum(bouts[3]['rates']) / len(bouts[3]['rates']),
            'Median HR for Time Spent at HR < 40%': median(sorted(bouts[3]['rates'])),
            'Min HR for Time Spent at HR < 40%': min(bouts[3]['rates'])
        })
    else:
        row.update({'Number of Bouts at HR < 40%': 'NO DATA',
                    'Total Time Spent at HR < 40%': 'NO DATA',
                    'Mean HR for Time Spent at HR < 40%': 'NO DATA',
                    'Median HR for Time Spent at HR < 40%': 'NO DATA',
                    'Min HR for Time Spent at HR < 40%': 'NO DATA'})

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
