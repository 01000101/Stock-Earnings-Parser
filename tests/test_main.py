import datetime
import json
import os

import mock
import pytest

from stock_earnings_parser.main import main


def test_empty_argument():
    """run main func without argument."""
    # it can't be run if pytest is run with other flags.
    main()


@mock.patch('stock_earnings_parser.main.pprint')
@mock.patch('stock_earnings_parser.main.get_nasdaq_report_details')
@mock.patch('stock_earnings_parser.main.get_nasdaq_report_links')
def test_mock_external(mock_get_report_links, mock_get_report_details, mock_pprint):
    """test with example data."""
    # preparation
    script_folder = os.path.dirname(os.path.realpath(__file__))

    example_meta_reports_file = os.path.join(script_folder, 'files', 'reports_meta_example.json')
    with open(example_meta_reports_file) as f:
        example_meta_reports = json.load(f)

    example_meta_reports_file = os.path.join(script_folder, 'files', 'detail_data.json')
    with open(example_meta_reports_file) as f:
        example_details_data = json.load(f)

    mock_get_report_links.return_value = example_meta_reports
    mock_get_report_details.side_effect = lambda y: filter(
        lambda x: x[0] == y,
        example_details_data
    )[0][1]
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
