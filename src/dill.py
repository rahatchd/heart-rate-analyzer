import os
import pandas


def store(csv, pickle, shell):
    """
    Read csv data and store it in a pickle, parsing the 'Time' column strings into datetime objects -
    converting from 12 hour to 24 hour format.

    :param csv: file containing data
    :param pickle: file in which to store pickle
    :param shell: terminal in which program is running

    :return raw: numpy ndarray representation of data
    """

    if os.path.isfile('data/' + csv):
        print ''
        print 'reading data from <data/{}> ...'.format(csv)
        raw = pandas.read_csv('data/' + csv,
                              parse_dates=['Time'],
                              date_parser=lambda x: pandas.datetime.strptime(x, '%m/%d/%Y %I:%M:%S %p'),
                              usecols=['Time', 'Value']
                              ).as_matrix()
        print '{s.bold}data read{s.normal}'.format(s=shell)

        print ''
        print 'storing data in <data/{}.pkl> ...'.format(pickle)
        raw.dump('data/' + pickle + '.pkl')
        print '{s.bold}data stored{s.normal}'.format(s=shell)
        return raw
    else:
        return -1
