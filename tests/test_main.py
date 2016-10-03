import datetime
import json
import os
from unittest import TestCase

import mock
import pytest

from stock_earnings_parser.main import main


@pytest.mark.online
def test_empty_argument():
    """run main func without argument."""
    # it can't be run if pytest is run with other flags.
    main()


def read_sample(filename):
    """read sampel in files folder for testing."""
    script_folder = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(script_folder, 'files', filename)
    with open(filepath) as f:
        data = json.load(f)
    return data

def get_report_details_side_effect():
    """create function to mock get_nasdaq_report_details side effect."""
    example_details_data = read_sample('detail_data.json')
    return lambda y: filter(lambda x: x[0] == y, example_details_data)[0][1]

@mock.patch('stock_earnings_parser.main.pprint')
@mock.patch('stock_earnings_parser.main.get_nasdaq_report_details',
    side_effect=get_report_details_side_effect())
@mock.patch('stock_earnings_parser.main.get_nasdaq_report_links',
    return_value=read_sample('reports_meta_example.json'))
class MainFuncTest(TestCase):

    def test_mock_external(self, mock_get_report_links, mock_get_report_details, mock_pprint):
        """test with example data."""
        # example data
        example_details_data = read_sample('detail_data.json')

        tommorow_date  = datetime.date.today() + datetime.timedelta(days=1)
        # convert date to datetime, because mock_get_report_links receive datetime as default
        tommorow_date = datetime.datetime.combine(tommorow_date, datetime.datetime.min.time())

        # run func.
        main()

        # check result
        mock_get_report_links.assert_called_once_with(tommorow_date)
        assert len(mock_get_report_details.mock_calls) == 23
        for data in example_details_data:
            # data is a tuple
            # (url, report)
            mock_get_report_details.assert_any_call(data[0])
        assert len(mock_pprint.mock_calls) == 11

    def test_surprise_delta_min(self, mock_get_report_links, mock_get_report_details, mock_pprint):
        """test surprise delta min."""
        main(['--surprise-delta-min', '5.0'])

        assert len(mock_pprint.mock_calls) == 7
