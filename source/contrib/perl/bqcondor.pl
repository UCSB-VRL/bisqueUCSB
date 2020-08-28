#!/usr/bin/env perl
#
# Code for Bisque Condor interoperation for multitip analysis
#
# Fetch the initial tip points and the individual planes of the the
# time series image placing all data the specified directory.
# Then launch the multitip analysis using the condor submit script.

use HTTP::Request::Common;
use LWP::UserAgent;
use MIME::Base64;
use URI::Escape;
use XML::LibXML;
use Log::Log4perl qw(:easy);
use Getopt::Long;

# Logging at DEBUG, INFO, WARN, ERROR, FATAL
Log::Log4perl->easy_init($INFO);
my $logger = get_logger('bqcondor');

my $ua = LWP::UserAgent->new;
my $parser = XML::LibXML->new();

my ($help, $imageurl, $mexurl, $userpass);
usage() if ( ! GetOptions('help|?' => \$help, 
                          'mex=s' => \$mexurl,
                          'image=s' => \$imageurl, 
                          'userpass=s' => \$userpass)
         or @ARGV < 1 or defined $help );
 
sub usage
{
  print "Unknown option: @_\n" if ( @_ );
  print "usage: bqcondor [--mex URL] [--userpass USER:PASS] [--help|-?]\n";
  exit;
}

# Fetch the url returning the xml document
sub fetch  {
  my $url = shift;
  my $response = $ua->request (GET $url, authorization => $auth );
  return $response->content;
}
sub fetchxml  {
  my $url = shift;
  my $response = $ua->request (GET $url, authorization => $auth );
  my $doc       = $parser->parse_string($response->content);
  return $doc;
}

#############################################
# Setup authorization
my $auth = "Basic " . encode_base64 ("$userpass");

#############################################
# Prepare local files based on Inputs


# Parse the gobject creating a CSV
my $mexdoc = fetchxml ($mexurl );
my $tipgob = $mexdoc->findnodes ('/mex/tag[@name="tip_points"]/@uri')->to_literal->value;
my $tipcsv = fetch( $tipgob . "?format=csv");
use Text::CSV;

my $csv = Text::CSV->new();

my @tips;
foreach my $line  (split( /^/, $tipcsv )){
  print $line;
  if ($csv->parse($line)) {
    my @cols = $csv->fields();
    print Dumper(@cols);
    if ($cols[0] eq 'vertex' ) {
      push (@tips ,  "$cols[3], $cols[4] ");
    }
  }else {
    my $err = $csv->error_input;
    print "Failed to parse line: $err";
  }
}
open(TIPS, ">tips.csv");
foreach my $tip (@tips) { 
  print TIPS "$tip\n";
}
close(TIPS);


#  Fetch all images planes and map to local file space
my $imagedoc = fetchxml ($imageurl);
my $no_planes =  $imagedoc->findnodes('//image/@t')->to_literal->value;
my $imgsrc = $imagedoc->findnodes('//image/@src')->to_literal->value;

my @filepaths;
for ($plane = 0; $plane < $no_planes; $plane++) {

  my $pathdoc = $fetchxml($imgsrc . "?slice=,,,$plane&format=tiff&localpath");

  # Extract the list of files from the doc

  my $filepath = $pathdoc->findnodes ('//resource/@src')->to_literal->value;
  # Strip expected file:///
  push (@filepaths, substr $filepath, 8);
}


#############################################
# Launch condor jobs with new info








