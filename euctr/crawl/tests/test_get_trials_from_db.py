from unittest import TestCase
import os
import pandas as pd
import numpy as np
import pandas.util.testing as pdt
import euctr.management.commands.get_trials_from_db

class GetTrialsFromDbTestCase(TestCase):
    def test_cleanup_dataset(self):
        df_input = pd.read_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)),'test_cleanup_dataset-input.csv'))
        df_output = pd.read_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)),'test_cleanup_dataset-output.csv'), parse_dates=['date_of_the_global_end_of_the_trial'])

        euctr.management.commands.get_trials_from_db.cleanup_dataset(df_input)
        df_test_output = df_input

        # use the old 0.19.2 pandas undocumented function
        # rather than the 0.20 public function with a similar name
        pdt.assert_frame_equal(df_output, df_test_output)
