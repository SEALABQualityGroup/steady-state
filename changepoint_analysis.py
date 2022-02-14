from glob import glob
import os
from changepoint import changepoint

filtered_dirpath = './data/timeseries/filtered'
jmh_dirpath = './data/timeseries/all'
changepoints_dirpath = './data/changepoints'

def changepoint_analysis():
    if not os.path.exists(changepoints_dirpath):
        os.mkdir(changepoints_dirpath)

    for filtered_path in glob('{}/*.json'.format(filtered_dirpath)):

        print(filtered_path)
        filename = filtered_path.split('/')[-1]
        jmh_path = '{}/{}'.format(jmh_dirpath, filename)
        changepoints_path = '{}/{}'.format(changepoints_dirpath, filename)

        jmh_path, filtered_path, changepoints_path = [path for path in [jmh_path, filtered_path, changepoints_path]]
        if not os.path.exists(changepoints_path):
            print('Executing ', filename, '..')
            changepoint(jmh_path, filtered_path, changepoints_path)
        else:
            print(filename, 'already exists')


if __name__ == '__main__':
    changepoint_analysis()