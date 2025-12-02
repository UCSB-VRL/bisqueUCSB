from util import WebHelpersTestCase
import unittest
from datetime import datetime
from datetime import timedelta
import time

from webhelpers.date import *

class TestDateHelper(WebHelpersTestCase):
    
    def test_distance_of_time_in_words(self):
        from_time = datetime(2000, 1, 1, 0, 0, 0, 0, None) # Midnight, Jan 1 2000 UTC

        # Test that if integers are supplied they are interpreted as seconds from now
        self.assertEqual("1 second", distance_of_time_in_words(1))
        # The following two tests test the span from "now" to "a year from
        # now".  Depending on when the test is run, the interval may include a
        # leap year.  The 'try' assumes it's not a leap year, the 'except'
        # tries it again as a leap year.
        try:
            self.assertEqual("1 year", distance_of_time_in_words(0, 31536000))
            self.assertEqual("1 year", distance_of_time_in_words(1, 31536001))
        except AssertionError:  # If the intervening year contains February 29th
            self.assertEqual("11 months and 30 days", distance_of_time_in_words(0, 31536000))
            self.assertEqual("11 months and 30 days", distance_of_time_in_words(1, 31536001))
         
        # Granularity is invalid
        self.assertRaises(Exception, distance_of_time_in_words, 0, 1, 'blah')
        
        # February 2nd 2007 to March 1 2007 is 27 days because February is shorter month in the year
        self.assertEqual('27 days', distance_of_time_in_words(datetime(2007,2,2), datetime(2007, 3, 1)))
        
        # February 2nd 2008 to March 1 2008 is 28 days because it's a leap year 
        self.assertEqual('28 days', distance_of_time_in_words(datetime(2008,2,2), datetime(2008, 3, 1)))

        # Should get the same values going forward and backward
        to_time = datetime(1980, 5, 6, 12, 32, 40, 0, None) # 12:32pm, May 5, 1980
        self.assertEqual(distance_of_time_in_words(from_time, to_time), 
                         distance_of_time_in_words(to_time, from_time))
        self.assertEqual(distance_of_time_in_words(from_time, to_time, 'month'), 
                         distance_of_time_in_words(to_time, from_time, 'month'))
        self.assertEqual(distance_of_time_in_words(from_time, to_time, 'year'), 
                         distance_of_time_in_words(to_time, from_time, 'year'))
        
        # Ensure we get the correct granularity when the times are the same
        self.assertEqual("0 seconds", distance_of_time_in_words(from_time, from_time, 'second'))
        self.assertEqual("0 days", distance_of_time_in_words(from_time, from_time, 'day'))
        self.assertEqual("0 centuries", distance_of_time_in_words(from_time, from_time, 'century'))

        # We are not over the finest granularity
        self.assertEqual("less than 1 hour", distance_of_time_in_words(1, granularity='hour'))
        self.assertEqual("less than 1 day", distance_of_time_in_words(86399, granularity='day'))
        
        # Round up if the granularity after the supplied granularity is high enough
        self.assertEqual("1 day", distance_of_time_in_words(86399, round=True, granularity='day'))
        self.assertEqual("5 minutes", distance_of_time_in_words(290, round=True, granularity='minute'))
        self.assertEqual("1 day and 5 minutes", distance_of_time_in_words(86689, round=True, granularity='minute'))
        
        # Rounding at the second value makes no difference
        self.assertEqual(distance_of_time_in_words(to_time, from_time, granularity='second'),
                         distance_of_time_in_words(to_time, from_time, granularity='second', round=True))
        
        # Pluralization
        self.assertEquals(distance_of_time_in_words(datetime(200, 1,1), datetime(300, 1, 1)), "1 century")
        self.assertEquals(distance_of_time_in_words(datetime(200, 1,1), datetime(500, 1, 1)), "3 centuries")
        
        self.assertEquals(distance_of_time_in_words(datetime(2000, 1,1), datetime(2000, 2, 1)), "1 month")
        self.assertEquals(distance_of_time_in_words(datetime(2000, 1,1), datetime(2000, 5, 1)), "4 months")
        
        # Spot checks
        from_time = datetime(200, 2, 2, 0, 12, 12, 0, None) # 12 minutes, 12 seconds past midnight on Feb 2 200AD
        to_time = datetime(1981, 3, 31, 7, 31, 0, 0, None) # 7:31 am, March 31, 1981
        self.assertEqual(distance_of_time_in_words(from_time, to_time), 
             "17 centuries, 8 decades, 1 year, 1 month, 29 days, 7 hours, 18 minutes and 48 seconds")
        self.assertEqual(distance_of_time_in_words(from_time, to_time, granularity = 'hour'), 
             "17 centuries, 8 decades, 1 year, 1 month, 29 days and 7 hours")
        self.assertEqual(distance_of_time_in_words(from_time, to_time, granularity = 'hour', round=True), 
             "17 centuries, 8 decades, 1 year, 1 month, 29 days and 7 hours")
        self.assertEqual(distance_of_time_in_words(from_time, to_time, granularity = 'month'), 
             "17 centuries, 8 decades, 1 year and 1 month")
        self.assertEqual(distance_of_time_in_words(from_time, to_time, granularity = 'month', round=True), 
             "17 centuries, 8 decades, 1 year and 2 months")
        
        from_time = datetime(200, 2, 2, 12, 30, 30, 0, None) # 12:30:30, Feb 2, 200AD
        to_time = datetime(220, 3, 2, 12, 30, 31, 0, None) # 12:30:31, Mar 2, 220AD
        self.assertEqual(distance_of_time_in_words(from_time, to_time), 
             "2 decades, 1 month and 1 second")
        
if __name__ == '__main__':
    suite = [unittest.makeSuite(TestDateHelper)]
    for testsuite in suite:
        unittest.TextTestRunner(verbosity=1).run(testsuite)
