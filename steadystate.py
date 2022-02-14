from create_timeseries import create_timeseries
from filter_outliers import filter_outliers
from changepoint_analysis import changepoint_analysis
from classify_runs import classify_runs


if __name__ == '__main__':
    create_timeseries()
    filter_outliers()
    changepoint_analysis()
    classify_runs()
