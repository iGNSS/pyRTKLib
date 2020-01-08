import matplotlib
import matplotlib.pyplot as plt
from termcolor import colored
import numpy as np
import os
import pandas as pd
import sys
import logging
from matplotlib.ticker import FixedLocator
from matplotlib.gridspec import GridSpec
from matplotlib import dates

from pandas.plotting import register_matplotlib_converters
from ampyutils import amutils
from plot import plot_utils

register_matplotlib_converters()

__author__ = 'amuls'


def plot_elev_distribution(dRtk: dict, df: pd.DataFrame, obs_name: str, logger: logging.Logger, showplot: bool = False):
    """
    plot_elev_distribution plots the distribution of CN0 or PRres as function of elevation bins
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')

    logger.info('{func:s}: creating {obs:s} distribution plot'.format(obs=obs_name, func=cFuncName))

    amutils.logHeadTailDataFrame(logger=logger, callerName=cFuncName, df=df, dfName=obs_name)

    # set up the plot
    plt.style.use('ggplot')

    # possible GNSS systems in df
    gnss_names = ('GAL', 'GPS')

    # go over the sat systems
    for gnss_name in gnss_names:
        gnss_cols = [col for col in df if col.startswith(gnss_name)]
        logger.debug('{func:s}: gnss_cols = {cols!s}'.format(cols=gnss_cols, func=cFuncName))

        # check whether this sat system is in the df
        if len(gnss_cols):
            logger.info('{func:s}: creating {obs:s} distribution plot for {syst:s}'.format(obs=obs_name, syst=gnss_name, func=cFuncName))
            # determine number of rows/cols for subplots
            nrCols = 3
            tmpValue = divmod(len(gnss_cols), nrCols)

            if (tmpValue[1] == 0):
                nrRows = tmpValue[0]
            else:
                nrRows = tmpValue[0] + 1

            fig, ax = plt.subplots(nrows=nrRows, ncols=nrCols, sharex=True, sharey=True, figsize=(20.0, 12.0))
            fig.suptitle('{syst:s} - {posf:s} - {date:s}: {obs:s} Statistics'.format(posf=dRtk['info']['rtkPosFile'], syst=gnss_name, date=dRtk['Time']['date'], obs=obs_name), fontsize='xx-large')

            # the indexes on the x-axis
            ind = np.arange(len(df.index))
            print('ind = {!s}'.format(ind))

            for axis, col in zip(ax.flat, gnss_cols):
                # create a filled area for domain [-1, 1] if PRres plot
                if obs_name == 'PRres':
                    # get index numbers for PRres between -2 and +2
                    tmpValue = divmod(df.shape[0], 2)
                    print('tmpValue {!s}'.format(tmpValue))
                    if tmpValue[1] == 0:
                        mid_prres = tmpValue[0] - 0.5
                    else:
                        mid_prres = tmpValue

                    axis.axvspan(mid_prres - 2, mid_prres + 2, alpha=0.2, color='green')

                # draw a bar plot
                axis.bar(ind, df[col], alpha=0.5, color='blue', edgecolor='none')

                # rotate the ticks on this axis
                idx = np.asarray([i for i in range(len(df.index))])
                axis.set_xticks(idx)
                axis.set_xticklabels(df.index.tolist(), rotation=65)

                # set the title for sub-plot
                axis.set_title(label='Elevation bin {bin:s}'.format(bin=col[3:]), fontsize='x-large')

            # save the plot in subdir png of GNSSSystem
            amutils.mkdir_p(os.path.join(dRtk['info']['dir'], 'png'))
            pngName = os.path.join(dRtk['info']['dir'], 'png', os.path.splitext(dRtk['info']['rtkPosFile'])[0] + '-{syst:s}-{obs:s}-dist.png'.format(syst=gnss_name, obs=obs_name))
            fig.savefig(pngName, dpi=fig.dpi)


            if showplot:
                plt.show(block=True)
            else:
                plt.close(fig)
