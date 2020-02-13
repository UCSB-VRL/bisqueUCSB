#!perl -T

use Test::More tests => 1;
use BQPhytomorph;
use BQPhytomorph::Condor;

BEGIN {
	use_ok( 'BQPhytomorph' );
}

diag( "Testing BQPhytomorph $BQPhytomorph::VERSION, Perl $], $^X" );
