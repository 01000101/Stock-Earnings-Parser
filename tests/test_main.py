'''Tests'''
import datetime
import json
import os.path

from unittest import TestCase
import mock
import pytest

from stock_earnings_parser.main import main

# pylint: disable=R0201


@pytest.mark.online
def test_empty_argument():
    '''Run test without CLI arguments'''
    # it can't be run if pytest is run with other flags.
    main()


def read_sample(filename):
    '''read sample in files folder for testing'''
    script_folder = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(script_folder, 'files', filename)
    with open(filepath) as fdata:
        data = json.load(fdata)
    return data


def get_report_details_side_effect(url):
    '''create function to mock get_nasdaq_report_details side effect'''
    example_details_data = read_sample('detail_data.json')
    for details in example_details_data:
        if details[0] == url:
            return details[1]
    return None


@mock.patch('stock_earnings_parser.main.pprint')
@mock.patch('stock_earnings_parser.main.get_nasdaq_report_details',
            side_effect=get_report_details_side_effect)
@mock.patch('stock_earnings_parser.main.get_nasdaq_report_links',
            return_value=read_sample('reports_meta_example.json'))
class MainFuncTest(TestCase):
    '''Test harness'''

    def test_mock_external(self,
                           mock_get_report_links,
                           mock_get_report_details,
                           mock_pprint):
        '''Test with mock data'''
        # example data
        example_details_data = read_sample('detail_data.json')
        tommorow_date = datetime.date.today() + datetime.timedelta(days=1)
        # convert date to datetime, because the mock_gets_report_links
        # receives datetime as default
        tommorow_date = datetime.datetime.combine(
            tommorow_date, datetime.datetime.min.time())
        # run tests
        main()
        # check results
        mock_get_report_links.assert_called_once_with(tommorow_date)
        assert len(mock_get_report_details.mock_calls) == 23
        for data in example_details_data:
            # data is a tuple (url, report)
            mock_get_report_details.assert_any_call(data[0])
        assert len(mock_pprint.mock_calls) == 11

    def test_surprise_delta_min(self,
                                mock_get_report_links,
                                mock_get_report_details,
                                mock_pprint):
        '''Test --surprise-delta-min'''
        main(['--surprise-delta-min', '5.0'])
        assert len(mock_pprint.mock_calls) == 7

    def test_premarket(self,
                       mock_get_report_links,
                       mock_get_report_details,
                       mock_pprint):
        '''test premarket flag.'''
        # test premarket flag
        main(['--premarket'])
        assert len(mock_pprint.mock_calls) == 6
        # reset mock
        mock_pprint.reset_mock()
        # test no-premarket flag
        main(['--no-premarket'])
        assert len(mock_pprint.mock_calls) == 5
        # test both premarket flags called
        with pytest.raises(SystemExit):
            main(['--no-premarket', '--premarket'])
