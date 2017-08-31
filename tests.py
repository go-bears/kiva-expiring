import unittest

from nose.tools import assert_true
from data import raw_json_response
from kiva_expiring_loans import *


# variables and data needed for mocking a tests so results don't keep changing

# TODO: research and figure out how these become fixtures?
# Why do all tests fail if I put them inside the class?
now = parser.parse("2017-08-30 02:05:38.734405+00:00")

# tests make calls on archived data from a graphql query so math 
# can be double checked
post_process = preprocess_json(raw_json_response)
test_post_process = post_process[0]
filtered_24 = filter_loans_24_hrs(post_process, now)
test_total = calculate_total_fundraising_needed(filtered_24)


#TODO: finish writing doc strings for tests
class KivaExpiringTest(unittest.TestCase):

    def test_kiva_api_query(self):
        """Send a request to the API server and store the response."""
        test_response = requests.get(GRAPHQL_ENDPOINT + query_loans_expiring_24hrs)
        assert_true(test_response.ok)

    def test_preprocess_json(self):
        # post_process = preprocess_json(raw_json_response)
        self.assertTrue(type(preprocess_json(raw_json_response)), list)

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
        self.assertTrue(len(filter_loans_24_hrs(post_process, now))
                        < len(post_process))

    def test_filter_loans_24_hrs_type(self):
        self.assertTrue(type(filter_loans_24_hrs(post_process, now)), list)

    def test_datetime_diff(self):
        self.assertLessEqual((filter_loans_24_hrs(post_process, now)[0][
                             'plannedExpirationDate'] - now), timedelta(hours=24))

    def test_calculate_totalFundraisingNeeded(self):
        self.assertEqual(calculate_total_fundraising_needed(filtered_24), 21425.0)

    def test_show_total_fundraising_needed(self):
        self.assertEqual(type(show_total_fundraising_needed(test_total)), str)
    
    # this test will print links and amount raised & can be
    # compared to output in data.py
    def test_show_expiring_loans(self):
        self.assertFalse(show_expiring_loans(filtered_24))

if __name__ == '__main__':
    unittest.main()
