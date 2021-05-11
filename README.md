# solar-data-tools

<table>
<tr>
  <td>Latest Release</td>
  <td>
    <a href="https://pypi.org/project/solar-data-tools/">
    <img src="https://img.shields.io/pypi/v/solar-data-tools.svg" alt="latest release" />
    </a>
    <a href="https://anaconda.org/slacgismo/solar-data-tools">
    <img src="https://anaconda.org/slacgismo/solar-data-tools/badges/version.svg" />
    </a>
    <a href="https://anaconda.org/slacgismo/solar-data-tools">
    <img src="https://anaconda.org/slacgismo/solar-data-tools/badges/latest_release_date.svg" />
    </a>
</tr>
<tr>
  <td>License</td>
  <td>
    <a href="https://github.com/slacgismo/solar-data-tools/blob/master/LICENSE">
    <img src="https://img.shields.io/pypi/l/solar-data-tools.svg" alt="license" />
    </a>
</td>
</tr>
<tr>
  <td>Build Status</td>
  <td>
    <a href="https://solar-data-tools.readthedocs.io/en/stable/">
    <img src="https://readthedocs.org/projects/solar-data-tools/badge/?version=stable" alt="documentation build status" />
    </a>
    <a href="https://app.circleci.com/pipelines/github/slacgismo/solar-data-tools">
      <img src="https://circleci.com/gh/slacgismo/solar-data-tools.svg?style=svg" alt="CircleCi build status" />
    </a>
  </td>
</tr>
<!-- <tr>
  <td>Code Quality</td>
  <td>
    <a href="https://lgtm.com/projects/g/pvlib/pvlib-python/context:python">
    <img src="https://img.shields.io/lgtm/grade/python/g/pvlib/pvlib-python.svg?logo=lgtm&logoWidth=18" alt="lgtm quality grade" />
    </a>
    <a href="https://lgtm.com/projects/g/pvlib/pvlib-python/alerts">
    <img src="https://img.shields.io/lgtm/alerts/g/pvlib/pvlib-python.svg?logo=lgtm&logoWidth=18" alt="lgtm alters" />
    </a>
  </td>
</tr>
<tr>
  <td>Coverage</td>
  <td>
    <a href="https://coveralls.io/r/pvlib/pvlib-python">
    <img src="https://img.shields.io/coveralls/pvlib/pvlib-python.svg" alt="coveralls coverage" />
    </a>
    <a href="https://codecov.io/gh/pvlib/pvlib-python">
    <img src="https://codecov.io/gh/pvlib/pvlib-python/branch/master/graph/badge.svg" alt="codecov coverage" />
    </a>
  </td>
</tr>
<tr>
  <td>Publications</td>
  <td>
    <a href="https://doi.org/10.5281/zenodo.3762635">
    <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.3762635.svg" alt="zenodo reference">
    </a>
    <a href="http://joss.theoj.org/papers/41187535cad22dd4b076c89b72f874b1">
    <img src="http://joss.theoj.org/papers/41187535cad22dd4b076c89b72f874b1/status.svg" alt="JOSS reference" />
    </a>
  </td>
</tr> -->
<tr>
  <td>Downloads</td>
  <td>
    <a href="https://pypi.org/project/solar-data-tools/">
    <img src="https://img.shields.io/pypi/dm/solar-data-tools" alt="PyPI downloads" />
    </a>
    <a href="https://anaconda.org/conda-forge/solar-data-tools">
    <img src="https://anaconda.org/slacgismo/solar-data-tools/badges/downloads.svg" alt="conda-forge downloads" />
    </a>
  </td>
</tr>
</table>

Tools for performing common tasks on solar PV data signals. These tasks include finding clear days in
a data set, common data transforms, and fixing time stamp issues. These tools are designed to be
automatic and require little if any input from the user. Libraries are included to help with data IO
and plotting as well.

There is close integration between this repository and the [Statistical Clear Sky](https://github.com/slacgismo/StatisticalClearSky) repository, which provides a "clear sky model" of system output, given only measured power as an input.

See [notebooks](/notebooks) folder for examples.

## Setup

### Recommended: Set up `conda` environment with provided `.yml` file

_Updated September 2020_

We recommend seting up a fresh Python virutal environment in which to use `solar-data-tools`. We recommend using the [Conda](https://docs.conda.io/projects/conda/en/latest/index.html) package management system, and creating an environment with the environment configuration file named `pvi-user.yml`, provided in the top level of this repository. This will install the `statistical-clear-sky` package as well.

Please see the Conda documentation page, "[Creating an environment from an environment.yml file](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file)" for more information.

### Installing this project as PIP package

```sh
$ pip install solar-data-tools
```

As of March 6, 2019, it fails because scs package installed as a dependency of cxvpy expects numpy to be already installed.
[scs issue 85](https://github.com/cvxgrp/scs/issues/85) says, it is fixed.
However, it doesn't seem to be reflected in its pip package.
Also, cvxpy doesn't work with numpy version less than 1.16.
As a work around, install numpy separatly first and then install this package.
i.e.
```sh
$ pip install 'numpy>=1.16'
$ pip install statistical-clear-sky
```

#### Solvers

By default, ECOS solver is used, which is supported by cvxpy because it is Open Source.

However, it is found that Mosek solver is more stable. Thus, we encourage you to install it separately as below and obtain the license on your own.

* [mosek](https://www.mosek.com/resources/getting-started/) - For using MOSEK solver.

    ```sh
    $ pip install -f https://download.mosek.com/stable/wheel/index.html Mosek
    ```

### Installing this project as Anaconda package

```sh
$ conda install -c slacgismo solar-data-tools
```

If you are using Anaconda, the problem described in the section for PIP package above doesn't occur since numpy is already installed. And during solar-data-tools installation, numpy is upgraded above 1.16.

#### Solvers

By default, ECOS solver is used, which is supported by cvxpy because it is Open Source.

However, it is found that Mosek solver is more stable. Thus, we encourage you to install it separately as below and obtain the license on your own.

* [mosek](https://www.mosek.com/resources/getting-started/) - For using MOSEK solver.

    ```sh
    $ conda install -c mosek mosek
    ```

### Using this project by cloning this GIT repository

From a fresh `python` environment, run the following from the base project folder:

```bash
$ pip install -r requirements.txt
```

As of March 6, 2019, it fails because scs package installed as a dependency of cxvpy expects numpy to be already installed.
[scs issue 85](https://github.com/cvxgrp/scs/issues/85) says, it is fixed.
However, it doesn't seem to be reflected in its pip package.
Also, cvxpy doesn't work with numpy version less than 1.16.
As a work around, install numpy separatly first and then install this package.
i.e.
```bash
$ pip install 'numpy>=1.16'
$ pip install -r requirements.txt
```

To test that everything is working correctly, launch

```bash
$ jupyter notebook
```

and run the two notebooks in the `notebooks/` folder.

## Usage

#### Clear Day Detection

This algorithm estimates the clear days in a data set two ways and then combines the estimates for the final estimations. The first estimate is based on the "smoothness" of each daily power signal. The second estimate is based on the seasonally adjusted daily energy output of the system.

```python
import numpy as np
from solardatatools.clear_day_detection import find_clear_days
from solardatatools.data_transforms import make_2d
from solardatatools.dataio import get_pvdaq_data

pv_system_data = get_pvdaq_data(sysid=35, api_key='DEMO_KEY', year=[2011, 2012, 2013])

power_signals_d = make_2d(pv_system_data, key='dc_power')

clear_days = find_clear_days(power_signals_d)
```

#### Time Shift Detection and Fixing

This algorithm determines if the time stamps provided with the data have "shifted" at any point and then corrects the shift if found. These shifts can often be caused by incorrect handling of daylight savings time, but can come from other sources as well.

```python
from solardatatools.data_transforms import fix_time_shifts, make_2d
from solardatatools.dataio import get_pvdaq_data
from solardatatools.plotting import plot_2d

pv_system_data = get_pvdaq_data(sysid=1199, year=[2015, 2016, 2017], api_key='DEMO_KEY')

power_signals_d = make_2d(pv_system_data, key='dc_power')

fixed_power_signals_d, time_shift_days_indices_ixs = fix_time_shifts(
    power_signals_d, return_ixs=True)
```

## Versioning

We use [Semantic Versioning](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/bmeyers/solar-data-tools/tags).

## Authors

* **Bennet Meyers** - *Initial work and Main research work* - [Bennet Meyers GitHub](https://github.com/bmeyers)

See also the list of [contributors](https://github.com/bmeyers/solar-data-tools/contributors) who participated in this project.

## License

This project is licensed under the BSD 2-Clause License - see the [LICENSE](LICENSE) file for details
