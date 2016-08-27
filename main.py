'''
    Web scraper for NASDAQ earnings reports
'''
from pprint import pprint
from datetime import datetime, timedelta
import time
import re
from lxml import html
import requests


NASDAQ_CALENDAR_URL = \
    'http://www.nasdaq.com/earnings/earnings-calendar.aspx?date=%s'
XPATH_REPORTS = \
    '//table[@id="ECCompaniesTable"]//tr/td[2]/a/@href'
XPATH_REPORT_TEXT = \
    '//div[@id="reportdata-div"]/p/span/text()'
XPATH_REPORT_TABLE_ROWS = \
    '//div[@id="showdata-div"]//div[@class="genTable"]/table//tr'
REPORT_PREFIX = \
    'http://www.nasdaq.com/earnings/report/'
REGEX_REPORT_TEXT_ANALYSTS = \
    r'based\s+on\s+(\d*)\s+analysts\''
REGEX_REPORT_TEXT_PRICE = \
    r'\s+EPS\s+forecast\s+for\s+the\s+quarter\s+is\s+\$([\-\+]?\d*\.\d*)'
REGEX_REPORT_TEXT_OPEN = \
    r'\s+before\s+market\s+open\.'


def utc_to_local():
    '''Convert UTC to local'''
    utc = datetime.utcnow()
    epoch = time.mktime(datetime.utcnow().timetuple())
    offset = datetime.fromtimestamp(epoch) - datetime.utcfromtimestamp(epoch)
    return utc + offset


def nasdaq_date(date=utc_to_local()):
    '''Gets a NASDAQ-formatted date string'''
    return date.strftime('%Y-%b-%d')


def get_nasdaq_report_links(date):
    '''Gets a list of earnings reports for a date'''
    req = requests.get(NASDAQ_CALENDAR_URL % nasdaq_date(date))
    tree = html.fromstring(req.text)
    return [{
        'symbol': x.split(REPORT_PREFIX)[1].upper(),
        'url': x
    } for x in tree.xpath(XPATH_REPORTS)]


def get_nasdaq_report_details(url):
    '''Gets report-specific info'''
    req = requests.get(url)
    tree = html.fromstring(req.text)
    # Get the expected earnings / analysts
    text = tree.xpath(XPATH_REPORT_TEXT)
    if len(text) == 1:
        # Get the forecast estimated price
        rgx = re.compile(REGEX_REPORT_TEXT_PRICE)
        res = rgx.search(text[0])
        if not res:
            return None
        estimated = float(res.group(1))
        # Get the number of analysts that have contributed
        rgx = re.compile(REGEX_REPORT_TEXT_ANALYSTS)
        res = rgx.search(text[0])
        analysts = 0
        if res:
            analysts = int(res.group(1))
        # Check if the event is pre-market or after-hours
        rgx = re.compile(REGEX_REPORT_TEXT_OPEN)
        res = rgx.search(text[0])
        premarket = True if res else False
    # Get the earnings
    earnings = list()
    rows = tree.xpath(XPATH_REPORT_TABLE_ROWS)
    for row in rows:
        cols = row.xpath('td/text()')
        if len(cols) < 5:
            continue
        if cols[0].startswith('\r\n'):
            continue
        try:
            earnings.append({
                'quarter': cols[0],
                'reported': cols[1],
                'actual': float(cols[2]),
                'expected': float(cols[3]),
                'surprise': float(cols[4])
            })
        except ValueError:
            return None
    if not earnings:
        return None
    return {
        'estimated': estimated,
        'analysts': analysts,
        'premarket': premarket,
        'history': earnings
    }


def main():
    '''Entry point'''
    # Set our target date to tomorrow
    req_date = utc_to_local() + timedelta(days=1)
    print 'date: %s' % nasdaq_date(req_date)
    # Request the main calendar for the day
    reports = list()
    reports_meta = get_nasdaq_report_links(req_date)
    for meta in reports_meta:

        report = get_nasdaq_report_details(meta['url'])
        print '%s: %s [%s]' % (
            meta['symbol'],
            meta['url'],
            'OK' if report else 'SKIP')
        if not report:
            continue
        report['meta'] = meta
        reports.append(report)
    for report in reports:
        if report['estimated'] > report['history'][0]['actual']:
            tag = '== %s ==' % report['meta']['symbol']
            print '%s\n%s\n%s' % (
                '=' * len(tag),
                tag,
                '=' * len(tag))
            pprint(report, indent=2)


if __name__ == '__main__':
    main()
