"""
WESTPA Run Analysis
===================

"""

__all__ = ['config', 'tools']

#setting this manually at the moment, not sure how to get this
w_env = '/home/edis/anaconda3/envs/westpa/westpa-2020.05/westpa.sh'
from . import config
# Build the environment!
config.set_west_environment(w_env)

del w_env
