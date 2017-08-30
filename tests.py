import unittest

from nose.tools import assert_true
from data import raw_json_response
from kiva_expiring_loans import *

now = parser.parse("2017-08-30 02:05:38.734405+00:00")
post_process = preprocess_json(raw_json_response)
test_post_process = post_process[0]

filtered_24 = filter_loans_24_hrs(post_process)
total = calculate_total_fundraising_needed(filtered_24)


class KivaExpiringTest(unittest.TestCase):

    def test_kiva_api(self):
        """Send a request to the API server and store the response."""
        test_response = requests.get(GRAPHQL_ENDPOINT + "{loans {totalCount}}")
        assert_true(test_response.ok)

    def test_preprocess_json(self):
        # post_process = preprocess_json(raw_json_response)
        self.assertTrue(type(post_process), list)

    def test_str_to_float_loanAmount(self):
        self.assertTrue(type(test_post_process['loanAmount']), float)

    def test_str_to_float_fundedAmount(self):
        self.assertTrue(
            type(test_post_process['loanFundraisingInfo']['fundedAmount']), float)

    def test_create_url(self):
        self.assertTrue(type(test_post_process['link']), str)

    def test_amountLeftToFundraise(self):
        self.assertTrue(type(test_post_process['amtLeftToFundraise']), float)

    def test_filter_loans_24_hrs_subset(self):
        self.assertTrue(len(filter_loans_24_hrs(post_process))
                        < len(post_process))

    def test_filter_loans_24_hrs_type(self):
        self.assertTrue(type(filter_loans_24_hrs(post_process)), list)

    def test_datetime_diff(self):
        self.assertLessEqual((filter_loans_24_hrs(post_process)[0][
                             'plannedExpirationDate'] - now), timedelta(hours=24))

    def test_calculate_totalFundraisingNeeded(self):
        self.assertEqual(calculate_total_fundraising_needed(filtered_24), 31425.0)

    def test_show_total_fundraising_needed(self):
        self.assertEqual(type(show_total_fundraising_needed(total)), str)
    
    def test_show_expiring_loans(self):
        self.assertFalse(show_expiring_loans(filtered_24))

if __name__ == '__main__':
    unittest.main()
