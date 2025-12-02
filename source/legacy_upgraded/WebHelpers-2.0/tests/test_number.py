from nose.tools import eq_

from webhelpers.number import *

class TestFormatNumber(object):
    def test_positive(self):
        eq_(format_number(1234567.89), "1,234,567.89")
        eq_(format_number(1234567), "1,234,567")
        eq_(format_number(123456), "123,456")
        eq_(format_number(12345), "12,345")
        eq_(format_number(1234), "1,234")
        eq_(format_number(123), "123")
        eq_(format_number(12), "12")
        eq_(format_number(1), "1")
        eq_(format_number(123.4), "123.4")

    def test_negative(self):
        eq_(format_number(-1234567.89), "-1,234,567.89")
        eq_(format_number(-1234567), "-1,234,567")
        eq_(format_number(-123456), "-123,456")
        eq_(format_number(-12345), "-12,345")
        eq_(format_number(-1234), "-1,234")
        eq_(format_number(-123), "-123")
        eq_(format_number(-12), "-12")
        eq_(format_number(-1), "-1")
        
    def test_other(self):
        eq_(format_number(1234.5, " ", ","), "1 234,5")
        eq_(format_number(1234.5, ".", ","), "1.234,5")
        eq_(format_number(-1234.5, ".", ","), "-1.234,5")


class TestFormatDataSize(object):
    def test_bytes(self):
        eq_(  format_byte_size(1),  '1 B')

    def test_kibibytes(self):
        eq_(  format_byte_size(1000, binary=True),  '1000 B')
        eq_(  format_byte_size(1024, 0, True),  '1 KiB')
        eq_(  format_byte_size(1024, 2, True),  '1.00 KiB')

    def test_kilobytes(self):
        eq_(  format_byte_size(1000),  '1.0 kB')
        eq_(  format_byte_size(1024, 0, False),  '1 kB')
        eq_(  format_byte_size(1024, 2, False),  '1.02 kB')
        eq_(  format_byte_size(1024, 0, False, True),  '1 kilobytes')
        eq_(  format_byte_size(1024, 2, False, True),  '1.02 kilobytes')

    def test_kilobits(self):
        eq_(  format_bit_size(1024, 0, False, False),  '1 kb')
        eq_(  format_bit_size(1024, 2, False, False),  '1.02 kb')
        eq_(  format_bit_size(1024, 0, False, True),  '1 kilobits')
        eq_(  format_bit_size(1024, 2, False, True),  '1.02 kilobits')

    def test_megabytes(self):
        eq_(  format_byte_size(12345678, 2, True),  '11.77 MiB')
        eq_(  format_byte_size(12345678, 2, False),  '12.35 MB')

    def test_terabytes(self):
        eq_(  format_byte_size(12345678901234, 2, True),  '11.23 TiB')
        eq_(  format_byte_size(12345678901234, 2, False),  '12.35 TB')

    def test_zettabytes(self):
        eq_(  format_byte_size(1234567890123456789012, 2, True),  '1.05 ZiB')
        eq_(  format_byte_size(1234567890123456789012, 2, False),  '1.23 ZB')

    def test_yottabytes(self):
        eq_(  format_byte_size(123456789012345678901234567890, 2, True),  
            '102121.06 YiB')
        eq_(  format_byte_size(123456789012345678901234567890, 2, False),  
            '123456.79 YB')
