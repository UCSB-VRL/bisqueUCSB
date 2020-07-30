#!/usr/bin/env perl
#
# Demonstrate perl operations for finding images, uploading files
# and tagging.



# Setup some paramaters for your local installation
my $BQ="https://loup.ece.ucsb.edu/";
my $USER = "kgk";
my $PASS = "testme";
my $TAG_QUERY='experiment:"growth parameters"';


use HTTP::Request::Common;
use LWP::UserAgent;
use MIME::Base64;
use URI::Escape;
use XML::LibXML;
use Log::Log4perl qw(:easy);

# Logging at DEBUG, INFO, WARN, ERROR, FATAL
Log::Log4perl->easy_init($INFO);
my $logger = get_logger('bqfetch');

# Use basic authentication for now
my $auth = "Basic " . encode_base64 ("$USER:$PASS");
# Derived globals
my $DS="$BQ/ds/";
my $CS="$BQ/bisquik/";
my $IMAGES="$DS/images/";
my $ua = LWP::UserAgent->new;


### Get XML list of available images
#
#my $req = HTTP::Request->new (GET => $IMAGES );
#$req->header (authorization => $auth);
#my $response = $ua->request($req);
#my $response = $ua->get ($IMAGES, authorization =>$auth);
#open(DUMP, '>>dump.xml');
#print $response->content;

### Get XML list of available images with TAG experiment="growth parameters"

my $req = HTTP::Request->new (GET => $IMAGES . "?tag_query=$TAG_QUERY");
$req->header (authorization => $auth);
my $response = $ua->request($req);
$logger->debug ("content = ".  $response->content);

### find the URIs of the returned images

my $parser = XML::LibXML->new();
my $doc    = $parser->parse_string($response->content);
my $uris   = $doc->findnodes ('//image/@uri');

# Show the URI
my $image_uri;
foreach my $image_node ($uris) {
  $image_uri = $image_node->to_literal;
  $logger->info('URI ='. $image_uri);

}


### Add the new RESULT CSV to the server 
my $csv = "name, val1, val2
a, 1, 2
b, 2, 3
c, 3, 5
";

# Tricky stuff here.. see
# http://search.cpan.org/~gaas/libwww-perl/lib/HTTP/Request/Common.pm
# We are faking a file upload using the string $csv
my $response = $ua->request(POST $CS . '/upload_files',
                       authorization => $auth,
                       Content_Type => 'form-data',
                       # f1 is like <input type="file" name="f1" />
                       # The Content value is spec'ed out in the URL above.
                       Content => [ f1 => [ undef, 'csv_data.csv',
                                            Content => $csv ] ]);
#$response = $ua->request($req);

my $parser = XML::LibXML->new();
my $doc = $parser->parse_string($response->content);
my $file_url  = $doc->findnodes ('//resource[@type="file"]/@src');

$logger->info ("uploaded file to ".$file_url->to_literal);

### Check for a results TAG on the image

my $response = $ua->request (GET $image_uri . '?tag_query=results&view=deep',
                             authorization => $auth );

$logger->info ("content is ".$response->content);
my $doc       = $parser->parse_string($response->content);
my ($tag_uri) = $doc->findnodes ('//tag[@name="results"]/@uri')->to_literal->value;

$logger->info ('taguri is '. $tag_uri);

### Send a new TAG to the image containing the file url.

my $tag_xml = '<tag name="results" type="file" value="'.$file_url->to_literal.'" />';
if ($tag_uri eq '' ) {
  # No pre-exsiting tag available
  my $resp = $ua->request(POST $image_uri.'/tags',
                          authorization => $auth,
                          Content_Type => 'application/xml',
                          Content => $tag_xml
                          );
  $logger->info ("new TAG " . $resp->content);
} else {
  my $resp = $ua->request(PUT $tag_uri,
                          authorization => $auth,
                          Content_Type => 'application/xml',
                          Content => $tag_xml
                          );

  $logger->info ("updated TAG " . $resp->content);
}

1;
