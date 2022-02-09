# Towards effective assessment of steady state performance in Java software: Are we there yet?

Replication package of the work ‟*Towards effective assessment of steady state performance in Java software: Are we there yet?* ”.

**Requirements**
- Python 3.6
- R 4.0


Use the following command to install Python dependencies
```
pip install --upgrade pip
pip install -r requirements.txt
```

### Microbenchmarks
The complete list of benchmarks considered in our empirical study is available in `data/subjects.csv`.
Each row reports (for a particular benchmark): the benchmark signature (i.e., the name of the JMH benchmark method), the Java system, the parameterization used in our experiments, and the JMH configuration defined by software developers.
In particular, each JMH configuration is constituted by: *warmup iteration time* (w), *measurement iteration time* (r), *warmup iterations* (wi), *measurement iterations* (i), and *forks* (f).


### Performance measurements
We keep performance measurements used in our empirical study in a [separate repository](https://doi.org/10.5281/zenodo.5961018).
In order to replicate our results, the dataset (i.e., `jmh.tar.gz`) must be downloaded from the [repo](https://doi.org/10.5281/zenodo.5961018), and unpacked in the `data` folder as follows:

<pre><code>tar -zxvf <i>path</i>/jmh.tar.gz -C data</code></pre>

Each json file in the `data/jmh` folder reports JMH results of an individual benchmark.
The json filename denotes the considered benchmark using the following format:
<pre><code><i>system</i>#<i>benchmark</i>#<i>parameterization</i>.json</code></pre>
where `system` denotes the Java system name, `benchmark` denotes the benchmark method signature, and `parameterization` specifies benchmark parameters values.


### Steady state analysis
Steady state analysis can be performed through the following command:
```
python steadystate.py
```
Results of steady state analysis can be found in the `data/classification` folder.
Each json file in the folder reports whether (and when) a given benchmark reaches a steady state of performance.
Specifically, the file reports the classification of each benchmark (<i>steady state</i>, <i>no steady state</i> or <i>inconsistent</i>) and fork (<i>steady state</i> or <i>no steady state</i>), and the JMH iterations in which the steady state is reached (-1 indicates <i>no steady state</i>).<br> 
The set of changepoints found by the PELT algorithm is reported in the `data/changepoints` folder.

### Developer configurations
The following command maps the JMH configurations defined by software developers to our performance data.
In particular, it identifies for each fork the last warmup iteration and the last measurement iteration.
Results are stored in the `data/devconfig` folder, and are later used to derive the estimated warmup time ( <i>wt</i> ) and the set of performance measurements considered by software developers ( <i>M <sup>conf</sup></i> ).
```
python create_devconfigs.py
```

### Dynamic reconfiguration
In order to run dynamic reconfiguration techniques, the [replication package](https://doi.org/10.6084/m9.figshare.11944875) of Laaber et al. must be first downloaded and configured (following the instructions in the `README.md` file). Then, the environment variable `$REPLICATIONPACKAGE_PATH` must be set with the path of the replication package folder.<br>
The following command performs JMH reconfiguration.
```
bash create_dynconfigs.py
```
Similarly to developer configurations, the script identifies, for each fork, the last warmup iteration and the last measurement iteration.
Results are stored in the `data/dynconfig` folder, and are later used to derive the estimated warmup time ( <i>wt</i> ) and the set of performance measurements identified by dynamic reconfiguration techniques ( <i>M <sup>conf</sup></i> ).</br>

## Developer/dynamic configurations analysis
The following command computes for each fork and developer/dynamic configuration the information needed to compute (i) the <i>Warmup Estimation Error</i>, (ii) the <i>time waste</i> and (iii) the Absolute Relative Performance Change.<br>
Results are stored in `data/cfg_assessment.csv` file.
```
python configuration_analysis.py
```

### RQ<sub>1</sub> - Steady state evaluation
The following command generates Figures 4a and 4b, i.e., forks and benchmark classifications.
```
python analysis/rq1.py
```
The following command generates Figure 5, i.e., percentages of no steady state forks within each benchmark.
```
python analysis/rq1_within_benchmark.py
```

(In order to run both `rq1.py`and `rq1_within_benchmark.py`, you should first run `steadystate.py`)

### RQ<sub>2</sub> and RQ<sub>3</sub> - Developer/Dynamic configurations assessment
The following command generates Figures 6, 7, 8, 9, i.e., plots for developer configuration assessment  and dynamic reconfiguration assessment.
```
python analysis/rq2_rq3.py
```
(Note that you should first run `steadystate.py`, `create_devconfigs.py`, `bash create_dynconfigs.py` and `configurations_assessment.py`)

### RQ<sub>4</sub> - Dynamic <i>vs</i> Developer configurations 
The following command generates Figures 10, 11 and 12 ( i.e., summaries of WEE/wt/ARPC comparisons), and Tables 2, 3 and 4 (i.e., detailed results of WEE/wt/ARPC comparisons).
```
python analysis/rq4.py
```
(Note that you should first run `steadystate.py`, `create_devconfigs.py`, `bash create_dynconfigs.py` and `configurations_assessment.py`)
