# pytest conftest.py functions from https://docs.pytest.org/en/latest/example/simple.html

import pytest
import sys
import os

import pandas as pd
from pandas.compat import StringIO

import pyamps


def pytest_cmdline_preparse(args):
    """use #cpu's-1 for testing if pytest-xdist installed"""
    if 'xdist' in sys.modules:
        import multiprocessing
        num = max(multiprocessing.cpu_count()-1, 1)
        args[:] = ["-n", str(num)] + args


def pytest_runtest_makereport(item, call):
    """determine if previous function under fixture pytest.mark.incremental failed"""
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    """set expected failure when prevous function failed"""
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed (%s)" % previousfailed.name)


# Fixtures for test functions

@pytest.fixture(scope="function")
def model_coeff():
    """Generate test data similar in form to AMPS model coefficients"""
    fake_data = """ n,  m,  tor_c_const,    tor_s_const,    pol_c_const,    pol_s_const,    tor_c_sinca,    tor_s_sinca,    pol_c_sinca,    pol_s_sinca,    tor_c_cosca,    tor_s_cosca,    pol_c_cosca,    pol_s_cosca,    tor_c_epsilon,  tor_s_epsilon,  pol_c_epsilon,  pol_s_epsilon,  tor_c_epsilon_sinca,    tor_s_epsilon_sinca,    pol_c_epsilon_sinca,    pol_s_epsilon_sinca,    tor_c_epsilon_cosca,    tor_s_epsilon_cosca,    pol_c_epsilon_cosca,    pol_s_epsilon_cosca,    tor_c_tilt, tor_s_tilt, pol_c_tilt, pol_s_tilt, tor_c_tilt_sinca,   tor_s_tilt_sinca,   pol_c_tilt_sinca,   pol_s_tilt_sinca,   tor_c_tilt_cosca,   tor_s_tilt_cosca,   pol_c_tilt_cosca,   pol_s_tilt_cosca,   tor_c_tilt_epsilon, tor_s_tilt_epsilon, pol_c_tilt_epsilon, pol_s_tilt_epsilon, tor_c_tilt_epsilon_sinca,   tor_s_tilt_epsilon_sinca,   pol_c_tilt_epsilon_sinca,   pol_s_tilt_epsilon_sinca,   tor_c_tilt_epsilon_cosca,   tor_s_tilt_epsilon_cosca,   pol_c_tilt_epsilon_cosca,   pol_s_tilt_epsilon_cosca,   tor_c_tau,  tor_s_tau,  pol_c_tau,  pol_s_tau,  tor_c_tau_sinca,    tor_s_tau_sinca,    pol_c_tau_sinca,    pol_s_tau_sinca,    tor_c_tau_cosca,    tor_s_tau_cosca,    pol_c_tau_cosca,    pol_s_tau_cosca,    tor_c_tilt_tau, tor_s_tilt_tau, pol_c_tilt_tau, pol_s_tilt_tau, tor_c_tilt_tau_sinca,   tor_s_tilt_tau_sinca,   pol_c_tilt_tau_sinca,   pol_s_tilt_tau_sinca,   tor_c_tilt_tau_cosca,   tor_s_tilt_tau_cosca,   pol_c_tilt_tau_cosca,   pol_s_tilt_tau_cosca,   tor_c_f107, tor_s_f107, pol_c_f107, pol_s_f107
                    1,  0,  -0.1,           ,               -0.3,           0.4,            -0.5,           0.6,            -0.7,           0.8,            -0.9,           1.0,            -1.1,           1.2,            -1.3,           1.4,            -1.5,           1.6,            -1.7,                   1.8,                    -1.9,                   2.0,                    -2.1,                   2.2,                    -2.3,                   2.4,                    -2.5,       2.6,        -2.7,       2.8,        -2.9,               3.0,                -3.1,               3.2,                -3.3,               3.4,                -3.5,               3.6,                -3.7,               3.8,                -3.9,               4.0,                -4.1,                       4.2,                        -4.3,                       4.4,                        -4.5,                       4.6,                        -4.7,                       4.8,                        -4.9,       5.0,        -5.1,       5.2,        -5.3,               5.4,                -5.5,               5.6,                -5.7,               5.8,                -5.9,               6.0,                -6.1,           6.2,            -6.3,           6.4,            -6.5,                   6.6,                    -6.7,                   6.8,                    -6.9,                   7.0,                    -7.1,                   7.2,                    -7.3,       7.4,        -7.5,       7.6
                    1,  1,  -0.1,           ,               -0.3,           0.4,            -0.5,           0.6,            -0.7,           0.8,            -0.9,           1.0,            -1.1,           1.2,            -1.3,           1.4,            -1.5,           1.6,            -1.7,                   1.8,                    -1.9,                   2.0,                    -2.1,                   2.2,                    -2.3,                   2.4,                    -2.5,       2.6,        -2.7,       2.8,        -2.9,               3.0,                -3.1,               3.2,                -3.3,               3.4,                -3.5,               3.6,                -3.7,               3.8,                -3.9,               4.0,                -4.1,                       4.2,                        -4.3,                       4.4,                        -4.5,                       4.6,                        -4.7,                       4.8,                        -4.9,       5.0,        -5.1,       5.2,        -5.3,               5.4,                -5.5,               5.6,                -5.7,               5.8,                -5.9,               6.0,                -6.1,           6.2,            -6.3,           6.4,            -6.5,                   6.6,                    -6.7,                   6.8,                    -6.9,                   7.0,                    -7.1,                   7.2,                    -7.3,       7.4,        -7.5,       7.6
                    2,  0,  -0.1,           ,               -0.3,           0.4,            -0.5,           0.6,            -0.7,           0.8,            -0.9,           1.0,            -1.1,           1.2,            -1.3,           1.4,            -1.5,           1.6,            -1.7,                   1.8,                    -1.9,                   2.0,                    -2.1,                   2.2,                    -2.3,                   2.4,                    -2.5,       2.6,        -2.7,       2.8,        -2.9,               3.0,                -3.1,               3.2,                -3.3,               3.4,                -3.5,               3.6,                -3.7,               3.8,                -3.9,               4.0,                -4.1,                       4.2,                        -4.3,                       4.4,                        -4.5,                       4.6,                        -4.7,                       4.8,                        -4.9,       5.0,        -5.1,       5.2,        -5.3,               5.4,                -5.5,               5.6,                -5.7,               5.8,                -5.9,               6.0,                -6.1,           6.2,            -6.3,           6.4,            -6.5,                   6.6,                    -6.7,                   6.8,                    -6.9,                   7.0,                    -7.1,                   7.2,                    -7.3,       7.4,        -7.5,       7.6
                    2,  1,  -0.1,           ,               -0.3,           0.4,            -0.5,           0.6,            -0.7,           0.8,            -0.9,           1.0,            -1.1,           1.2,            -1.3,           1.4,            -1.5,           1.6,            -1.7,                   1.8,                    -1.9,                   2.0,                    -2.1,                   2.2,                    -2.3,                   2.4,                    -2.5,       2.6,        -2.7,       2.8,        -2.9,               3.0,                -3.1,               3.2,                -3.3,               3.4,                -3.5,               3.6,                -3.7,               3.8,                -3.9,               4.0,                -4.1,                       4.2,                        -4.3,                       4.4,                        -4.5,                       4.6,                        -4.7,                       4.8,                        -4.9,       5.0,        -5.1,       5.2,        -5.3,               5.4,                -5.5,               5.6,                -5.7,               5.8,                -5.9,               6.0,                -6.1,           6.2,            -6.3,           6.4,            -6.5,                   6.6,                    -6.7,                   6.8,                    -6.9,                   7.0,                    -7.1,                   7.2,                    -7.3,       7.4,        -7.5,       7.6
                    2,  2,  -0.1,           ,               -0.3,           0.4,            -0.5,           0.6,            -0.7,           0.8,            -0.9,           1.0,            -1.1,           1.2,            -1.3,           1.4,            -1.5,           1.6,            -1.7,                   1.8,                    -1.9,                   2.0,                    -2.1,                   2.2,                    -2.3,                   2.4,                    -2.5,       2.6,        -2.7,       2.8,        -2.9,               3.0,                -3.1,               3.2,                -3.3,               3.4,                -3.5,               3.6,                -3.7,               3.8,                -3.9,               4.0,                -4.1,                       4.2,                        -4.3,                       4.4,                        -4.5,                       4.6,                        -4.7,                       4.8,                        -4.9,       5.0,        -5.1,       5.2,        -5.3,               5.4,                -5.5,               5.6,                -5.7,               5.8,                -5.9,               6.0,                -6.1,           6.2,            -6.3,           6.4,            -6.5,                   6.6,                    -6.7,                   6.8,                    -6.9,                   7.0,                    -7.1,                   7.2,                    -7.3,       7.4,        -7.5,       7.6
    """.replace(" ", "")
    true_name = pyamps.model_utils.coeff_fn
    ext = os.path.splitext(true_name)[1]
    if ext == 'txt':
        fake_data = fake_data.replace(",,", ",NaN,").replace(",", " ")
    fake_name = os.path.abspath("test_fake_model%s" % ext)

    pyamps.model_utils.coeffs = pd.read_csv(StringIO(fake_data), index_col=('n', 'm'))
    yield true_name, fake_name
    pyamps.model_utils.coeffs = pd.read_csv(true_name, index_col=('n', 'm'))