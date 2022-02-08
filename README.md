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
The complete list of the benchmarks considered in our empirical study is available in `data/subjects.csv`.
Each row of the csv file reports the benchmark signature (i.e., the name of the JMH benchmark method), the system the benchmark belongs to, the parameterization used during execution, and the JMH configuration defined by software developers.
Each JMH configuration is constituted by: *warmup iteration time* (w), *measurement iteration time* (r), *warmup iterations* (wi), *measurement iterations* (i), and *forks* (f).


### Performance measurements
We keep performance measurements used in our empirical study in a [separate repository](https://doi.org/10.5281/zenodo.5961018).
In order to replicate our results, the dataset (i.e., `jmh.tar.gz`) must be first downloaded from the [repo](https://doi.org/10.5281/zenodo.5961018), and then unpacked in the `data` folder as follows:

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
Results can be found in the `data/classification` folder.
Each json file in the folder reports whether (and when) a given benchmark reaches a steady state of performance.
Specifically, the file reports the classification of each benchmark (<i>steady state</i>, <i>no steady state</i> or <i>inconsistent</i>) and fork (<i>steady state</i> or <i>no steady state</i>), and the JMH iterations in which steady states are reached (-1 indicates <i>no steady state</i>).