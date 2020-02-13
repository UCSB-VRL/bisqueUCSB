package BQPhytomorph;

use warnings;
use strict;

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
use XML::Simple;

use Log::Log4perl qw(:easy);
use Getopt::Long;

# Logging at DEBUG, INFO, WARN, ERROR, FATAL
Log::Log4perl->easy_init($INFO);
my $logger = get_logger('bqcondor');


=head1 NAME

BQPhytomorph - The great new BQPhytomorph!

=head1 VERSION

Version 0.01

=cut

our $VERSION = '0.01';


=head1 SYNOPSIS

The BQPhytomorph interface library for moving data between 
Bisque and BQPhytomorph

Perhaps a little code snippet.

    use BQPhytomorph;

    my $bq = BQPhytomorph->new(mex => "http://somehost/ds/mex/12");
    $bq->authorize("user:pass");
    ...

=head1 EXPORT

A list of functions that can be exported.  You can delete this section
if you don't export anything, such as for a purely object-oriented module.

=head1 FUNCTIONS

=head2 new
=cut

sub new {
  my($class, %args) = @_;
  my $self = bless({}, $class);

  $self->{mex} = exists $args{mex}? $args{mex} : undef;
  $self->{ua} = LWP::UserAgent->new();
  $self->{parser} = XML::LibXML->new();
  $self->{mexdoc}= exists $args{mexdoc}? $self->{parser}->parse_string($args{mexdoc}) : undef;
  
  if (exists $args{userpass}) {
    $self->authorize($args{userpass});
  }

  return $self;
}


=head2 fetch
  Fetch the url
=cut
# Fetch the url returning the xml document
sub fetch  {
  my $self = shift;
  my $url = shift;
  my $response = $self->{ua}->request (GET $url, authorization => $self->{auth} );
  return $response->content;

}
=head2 fetchxml
   Fetch the url and parse the resulting XML
=cut
sub fetchxml  {
  my $self = shift;
  my $url = shift;
  my $response = $self->{ua}->request (GET $url, authorization => $self->{auth} );
  my $doc       = $self->{parser}->parse_string($response->content);
  return $doc;
}

=head2 postxml
   Fetch the url and parse the resulting XML
=cut
sub postxml  {
  my $self = shift;
  my $url = shift;
  my $content = shift;

  my $response = $self->{ua}->request (POST $url, 
                                       authorization => $self->{auth},
                                       Content_Type=>"text/xml",
                                       Content => $content);
  my $doc       = $self->{parser}->parse_string($response->content);
  return $doc;
}



=head2 authorize
  Setup the bascic authentication
=cut

sub authorize {
  my $self = shift; 
  my $userpass = shift;
  $self->{auth} = "Basic "  . encode_base64($userpass);
}


=head2 fetchImagePlanes
  Fetch a multiplane image into a directory as seperate planes
  $bq->fetchImagePlanes ("http://host/ds/images/12", "imagedir");
=cut

sub fetchImagePlanes { 
#  Fetch all images planes and map to local file space
  my $self = shift; 
  my $imageurl = shift;
  my $localdir = shift // '.';

  my $imagedoc = $self->fetchxml ($imageurl);

  print "IMAGE=$imageurl ", $imagedoc->toString();

  my $no_planes =  int ($imagedoc->findnodes('//image/@t')->to_literal->value);
  my $imgsrc = $imagedoc->findnodes('//image/@src')->to_literal->value;
  print "Planes = $no_planes  src=$imgsrc\n";

  die "no planes" if ($no_planes == 0);

  my @filepaths;
  for (my $plane = 0; $plane < $no_planes; $plane++) {

    my $pathdoc = $self->fetchxml($imgsrc . "?slice=,,,$plane&format=tiff&localpath");

    # Extract the list of files from the doc

    my $filepath = $pathdoc->findnodes ('/resource/@src')->to_literal->value;
    # Strip expected file:
    push (@filepaths, uri_unescape(substr $filepath, 5));
  }

  # Link filepath into local dir.

  my $count = 0;
  foreach my $p (@filepaths) {
    symlink $p,  sprintf ("%s/%.5d.TIF", $localdir,$count) or print "BAD SYMLINK $p\n";
    $count ++;
  }
}


=head2 fetch_dataset 
  $bq->fetch_dataset ($dataset_url, '/tmp');
=cut

sub fetch_dataset { 
  my $self = shift; 
  my $url = shift;
  my $localdir = shift // '.';

  my $doc = $self->fetchxml ($url . "?view=deep");
  print "DATASET=$url ", $doc->toString();
  my @members = $doc->findnodes('//resource[@type="image"]');

  my @filepaths;
  foreach my $img (@members) {
    # Fetch the XML image descriptor
    my $imguri = $img->getAttribute('uri');
    my $imgdoc = $self->fetchxml($imguri);
    # Find the src attribute of the imgsrv
    my $imgsrc = $imgdoc->findnodes('//image/@src')->to_literal->value;
    # Ask for the local path
    my $pathdoc = $self->fetchxml($imgsrc . "?format=tiff&localpath");
    # Extract the path
    my $filepath = $pathdoc->findnodes ('/resource/@src')->to_literal->value;
    # Strip expected file:
    push (@filepaths, uri_unescape(substr $filepath, 5));
  }

  my $count = 0;
  foreach my $p (@filepaths) {
    symlink $p,  sprintf ("%s/%.5d.TIF", $localdir,$count) or die "BAD SYMLINK $p";
    $count ++;
  }

}


=head2 begin_mex
  $bq->begin_mex (status => "initializing" );
  $bq->update_mex (status => "30%" );
  $bq->finish_mex (status => "FINISHED" );

=cut
sub begin_mex {
  my $self = shift;
  my $status = shift;

  return $self->update_mex($status);
}


sub finish_mex {
  my $self = shift; 
  my $status = shift;
  my $msg    = shift;

  if (! defined $self->{mexdoc}) {
    $self->{mexdoc} = $self->fetchxml($self->{mex});
    my @nodes = $self->{mexdoc}->findnodes('//mex');
    $self->{mexbody}= $nodes[0];
  }

  if ($status ne "FINISHED") {
    my $tag = $self->{mexdoc}->createElement('tag');
    $tag->setAttribute('name', 'message');
    $tag->setAttribute('value', $msg);
  }
  return $self->update_mex($status);
}

sub update_mex {
  my $self = shift;
  my $status = shift;

  if (! defined $self->{mexdoc}) {
    $self->{mexdoc} = $self->fetchxml($self->{mex});
    my @nodes = $self->{mexdoc}->findnodes('//mex');
   $self->{mexbody}= $nodes[0];
  }

  if (defined $self->{mexdoc}) {
    $self->{mexbody}->setAttribute("status", $status);
    return $self->postxml($self->{mex}, $self->{mexbody}->toString());
  }
}


=head1 AUTHOR

CBI, C<< <bisque-dev at biodev.ece.ucsb.edu> >>

=head1 BUGS

Please report any bugs or feature requests to C<bug-bqphytomorph at rt.cpan.org>, or through
the web interface at L<http://rt.cpan.org/NoAuth/ReportBug.html?Queue=BQPhytomorph>.  I will be notified, and then you'll
automatically be notified of progress on your bug as I make changes.




=head1 SUPPORT

You can find documentation for this module with the perldoc command.

    perldoc BQPhytomorph


You can also look for information at:

=over 4

=item * RT: CPAN's request tracker

L<http://rt.cpan.org/NoAuth/Bugs.html?Dist=BQPhytomorph>

=item * AnnoCPAN: Annotated CPAN documentation

L<http://annocpan.org/dist/BQPhytomorph>

=item * CPAN Ratings

L<http://cpanratings.perl.org/d/BQPhytomorph>

=item * Search CPAN

L<http://search.cpan.org/dist/BQPhytomorph>

=back


=head1 ACKNOWLEDGEMENTS


=head1 COPYRIGHT & LICENSE

Copyright 2010 CBI, all rights reserved.

This program is free software; you can redistribute it and/or modify it
under the same terms as Perl itself.


=cut

1; # End of BQPhytomorph
