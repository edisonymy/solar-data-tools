""" Shade Module

This module is for analyzing shade losses in unlabeled power data

"""

import numpy as np
import pandas as pd
import cvxpy as cvx
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt


class ShadeAnalysis:
    def __init__(self, data_handler):
        self.dh = data_handler
        self.data_normalized = None
        self.data_transformed = None
        self.osd_problem = None
        self.daily_shade_loss = None
        self.daily_clear_energy = None
        self.avg_energy = None

    @property
    def has_run(self):
        state = np.alltrue([
            self.data_normalized is not None,
            self.data_transformed is not None,
            self.osd_problem is not None
        ])
        return state

    def run(self, power=8, solver='MOSEK', verbose=False):
        if not self.has_run:
            dn, dt = self.transform_data(power)
            self.data_normalized = dn
            self.data_transformed = dt
            self.osd_problem = self.make_osd_problem()
            self.osd_problem.solve(solver=solver, verbose=verbose)
        variable_dict = {v.name():v for v in self.osd_problem.variables()}
        self.clear_sky_component = variable_dict['clear-sky'].value
        self.shade_component = variable_dict['shade'].value

    def analyze_yearly_energy(self):
        if not self.has_run:
            self.run()

        # get scale factor for converting column sum to energy
        N = self.dh.data_sampling
        scale = N / 60
        # construct function to map from declination angle to total daily
        # integral of component
        f_loss = interp1d(self.data_transformed.index.values,
                          np.sum(self.shade_component, axis=1) * scale,
                          bounds_error=False, fill_value="extrapolate")
        f_clear = interp1d(self.data_transformed.index.values,
                           np.sum(
                               self.clear_sky_component, axis=1
                           ) * scale,
                           bounds_error=False, fill_value="extrapolate")

        avg_energy = pd.DataFrame(data=np.sum(self.dh.filled_data_matrix,
                                              axis=0),
                                  index=self.dh.day_index)
        avg_energy['doy'] = avg_energy.index.day_of_year
        avg_energy = avg_energy.loc[self.dh.daily_flags.clear]
        avg_energy = avg_energy.groupby('doy').mean() * scale

        self.daily_shade_loss = f_loss(delta_cooper(np.arange(365) + 1))
        self.daily_clear_energy = f_clear(delta_cooper(np.arange(365) + 1))
        self.daily_modeled_energy = (self.daily_clear_energy
                                     - self.daily_shade_loss)
        self.avg_energy = avg_energy

    def plot_yearly_energy_analysis(self, figsize=None):
        fig = plt.figure(figsize=figsize)
        plt.plot(self.daily_shade_loss, label='shade loss')
        plt.plot(self.daily_clear_energy,
                 label='predicted no shade')
        plt.plot(self.daily_clear_energy - self.daily_shade_loss,
                 label='modeled')
        plt.plot(self.avg_energy.index, self.avg_energy.values,
                 label='empirical', linewidth=.75)
        plt.xlabel('day of year')
        plt.ylabel('energy [kWh]')
        plt.title('Seasonal energy analysis')
        plt.legend()
        return fig

    def transform_data(self, power):
        normalized = batch_process(
            self.dh.filled_data_matrix,
            self.dh.boolean_masks.daytime,
            power=power
        )
        my_round = lambda x, c: c * np.round(x / c, 0)
        agg_by_azimuth = pd.DataFrame(data=normalized.T,
                                      index=np.arange(normalized.shape[1]),
                                      columns=np.linspace(0, 1, 2 ** power))
        agg_by_azimuth['delta'] = my_round(
            delta_cooper(self.dh.day_index.dayofyear.values), 1)
        # select only clear days
        agg_by_azimuth = agg_by_azimuth.iloc[self.dh.daily_flags.clear]
        agg_by_azimuth = agg_by_azimuth.groupby('delta').mean()
        agg_by_azimuth = agg_by_azimuth.iloc[::-1]
        return normalized, agg_by_azimuth

    def make_osd_problem(self):
        y = self.data_transformed.values
        x1 = cvx.Variable(y.shape, name='residual')
        x2 = cvx.Variable(y.shape, name='clear-sky')
        x3 = cvx.Variable(y.shape, name='shade')
        t = 0.85

        # phi1 = cvx.sum_squares(x1)
        phi1 = cvx.sum(0.5 * cvx.abs(x1) + (t - 0.5) * x1)
        phi2 = cvx.sum_squares(cvx.diff(x2, k=2, axis=0)) \
               + cvx.sum_squares(cvx.diff(x2, k=2, axis=1))
        phi3 = cvx.sum_squares(cvx.diff(x3, k=2, axis=0)) \
               + cvx.sum_squares(cvx.diff(x3, k=2, axis=1))
        phi4 = cvx.sum(x3)

        constraints = [
            y == x1 + x2 - x3,
            x2 >= 0,
            x2[:, 0] == 0,
            x2[:, -1] == 0,
            cvx.diff(x2, k=4, axis=1) <= 0,
            cvx.diff(x2, k=2, axis=0) <= 0,
            x3 >= 0
        ]

        objective = cvx.Minimize(
            20 * phi1 + 1e1 * phi2 + 1e2 * phi3 + 8e-1 * phi4)
        problem = cvx.Problem(objective, constraints)
        return problem


def batch_process(data, mask, power=8):
    """ Process an entire PV power matrix at once
    :return:
    """
    N = 2 ** power
    output = np.zeros((N, data.shape[1]))
    xs_new = np.linspace(0, 1, N)
    for col_ix in range(data.shape[1]):
        y = data[:, col_ix]
        energy = np.sum(y)
        msk = mask[:, col_ix]
        xs = np.linspace(0, 1, int(np.sum(msk)))
        interp_f = interp1d(xs, y[msk])
        resampled_signal = interp_f(xs_new)
        if np.sum(resampled_signal) > 0:
            output[:, col_ix] = resampled_signal * energy / np.sum(
                resampled_signal)
        else:
            output[:, col_ix] = 0
    return output

def undo_batch_process(data, mask):
    output = np.zeros_like(mask, dtype=float)
    xs_old = np.linspace(0, 1, data.shape[0])
    for col_ix in range(data.shape[1]):
        n_pts = np.sum(mask[:, col_ix])
        xs_new = np.linspace(0, 1, n_pts)
        interp_f = interp1d(xs_old, data[:, col_ix])
        resampled_signal = interp_f(xs_new)
        output[mask[:, col_ix], col_ix] = resampled_signal
    return output

def delta_cooper(day_of_year):
    """"
    Declination delta is estimated from equation (1.6.1a) in:
    Duffie, John A., and William A. Beckman. Solar engineering of thermal
    processes. New York: Wiley, 1991.
    """
    delta_1 = 23.45 * np.sin(np.deg2rad(360 * (284 + day_of_year) / 365))
    return delta_1