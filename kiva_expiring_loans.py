"""Create a script that queries the GraphQL API for loans. 
Filter for loans that have a status of fundRaising and a plannedExpirationDate 
in the next 24 hours. Use the loan amount property on those loans to determine 
the total dollar amount it would take to fund all of these loans and return or display that as a result. 
Show also a link to each loan and the amount it has left to fundraise.

Bonus: Write a test that mocks Kiva's API response and proves out that your 
code does the right calculation and returns the right values.
"""

__author__ = "melissa fabros"
__license__ = "BSD"
__version__ = "0.1"
__status__ = "Prototype"


import requests
import pytz

from datetime import timedelta, datetime
from dateutil import parser
from functools import lru_cache

GRAPHQL_ENDPOINT = 'https://api.kivaws.org/graphql?query='
LEND_TAB_URL_BASE = 'https://www.kiva.org/lend/'
NOW = datetime.now(pytz.utc)


query_loans_expiring_24hrs = """
{ loans (
  	limit: 500
		filters: {expiringSoon: true, status: fundRaising}
    ) 
  {
  totalCount
  values {
    id
    loanAmount
    loanFundraisingInfo {
      fundedAmount
      reservedAmount
    }
    plannedExpirationDate
    location {
      geocode{
        latitude
        longitude
      }
    }
  }
	}
}
"""

# TODO: refactor--separate the api query from the transformation, break into 2 functions

def call_kivaapi(query):
    """takes in graphql style query as a string
    return JSON response of loan data as list of dictionaries
    """

    try:
        response = requests.get(GRAPHQL_ENDPOINT + query, timeout=10)
        print("OK: status {}.".format(response.status_code))

        data = response.json()
        loans_data = data['data']['loans']['values']

        return loans_data

    except requests.exceptions.HTTPError as err:
        print (err)


def preprocess_json(json_response_list):
    """Takes list of loan data from raw response of GraphQL query
    return list with converted values and new key-values for links to loans
    and amount left to fundraise
    """

    if not json_response_list:
        raise ValueError("list is empty")

    for loan in json_response_list:
        loan['loanAmount'] = float(loan['loanAmount'])
        loan['loanFundraisingInfo']['fundedAmount'] = float(
            loan['loanFundraisingInfo']['fundedAmount'])
        loan['link'] = LEND_TAB_URL_BASE + str(loan['id'])
        loan['amtLeftToFundraise'] = loan['loanAmount'] - \
            loan['loanFundraisingInfo']['fundedAmount']

        if isinstance(loan['plannedExpirationDate'], str):
            loan['plannedExpirationDate'] = parser.parse(
                loan['plannedExpirationDate'])

    return json_response_list


def filter_loans_24_hrs(processed_json_list):
    """takes in list of cleaned data and returns subset list
    of loans that expire within 24 hours of current date/time
    """

    delta = timedelta(hours=24)

    if not processed_json_list:
        raise ValueError("list is empty")

    sorted_loans = []

    for loan in processed_json_list:
        planned_expiration = loan['plannedExpirationDate']

        if planned_expiration - NOW <= delta:
            sorted_loans.append(loan)
        else:
            continue

    return sorted_loans


def calculate_total_fundraising_needed(subset_24_hrs_list):
    """takes in list of filtered loan data and displays
    float of total for all loans needing funding that expire in 
    24 hours
    """

    if not subset_24_hrs_list:
        raise ValueError("list is empty")

    total = 0

    if subset_24_hrs_list:
        for loan in subset_24_hrs_list:
            if loan['amtLeftToFundraise'] > 0:
                total += loan['amtLeftToFundraise']
            else:
                print("This loan id {} is reporting negative value {}:".format(loan['id'],
                                                                               loan['amtLeftToFundraise']))
                continue

    return total

def show_total_fundraising_needed(total_sum):
    msg = "Total amount needed to fund loans expiring within 24 hours: {0:.2f} \n".format(total_sum)
    
    return msg


def show_expiring_loans(subset_24_hrs_list):
    """takes in list of filtered loan data and displays links and amount remaining
        left to fund        
    """

    if not subset_24_hrs_list:
        raise ValueError("list is empty")

    if len(subset_24_hrs_list) < 2:
        print('This loan needs your help! : \n')
    else:
        print('These loans need your help! : \n')

    for loan in subset_24_hrs_list:
        if loan['amtLeftToFundraise'] > 0:
            print (loan['link'], "amount left to raise: {0:.2f}".format(
                loan['amtLeftToFundraise']))

        else:
            print("This loan id {} is reporting negative value {}:".format(loan['id'],
                                                                           loan['amtLeftToFundraise']))
            continue


def main():
    """runs all functions for execution and testing
    """
    # print(call_kivaapi.cache_info())
    loans = call_kivaapi(query_loans_expiring_24hrs)
    print(len(loans))
    test_loans = loans
    # print(len(test_loans))
    test1 = preprocess_json(test_loans)
    # print (len(test1))
    test2 = filter_loans_24_hrs(test1)
    # print(len(test2))
    total = calculate_total_fundraising_needed(test2)
    msg = show_total_fundraising_needed(total)
    print (msg)
    show_expiring_loans(test2)

if __name__ == '__main__':
    main()
