#!/usr/bin/perl
package BQPhytomorph::RootTipModule;

use warnings;
use strict;

use Cwd 'abs_path';
use File::Basename;
use File::Copy;
use Getopt::Long;
use XML::LibXML;
use XML::Simple;
use POSIX qw/strftime/;
use Log::Log4perl;

use BQPhytomorph;

our $EXEC          = "./araGT";

my $log = Log::Log4perl::get_logger('roottip');
#########################################
## Argument handling
my ($help, $image_url, $mex, $user, $password, $userpass, $staging_path, $token);
my $debug = 0;
my $dryrun = 0;

usage() if ( ! GetOptions('help|?' => \$help,
                          'debug|d' => \$debug,
                          'dryrun|n' => \$dryrun,
                          'mex_url=s' => \$mex,
                          'image_url=s' => \$image_url,
                          'staging_path=s'=>\$staging_path,
                          'user=s' => \$user,
                          'password=s' => \$password,
                          'token=s' => \$token)
          or defined $help );

my $options = { debug=> $debug, dryrun => $dryrun };
my $command  = shift;

usage()  if (!defined $command);

if ($user && $password) {
  $userpass = $user . ':' . $password;
}

#usage() if (!defined ($mex) ||  ($command ne 'start' && $command ne 'finished'));

print "command is " . $command . "\n";

my $ret=0;
$ret = command_setup() if ($command eq 'setup');
$ret = command_teardown() if ($command eq 'teardown');
$ret = command_start() if ($command eq 'start');

exit($ret);


sub usage {
  print "Unknown option: @_\n" if ( @_ );
  print "usage: RootTip [--mex=URL] [--userpass=USER:PASS] [--image_url=IMAGE] [--staging=PATH] [--debug] [--help]  [start|setup|teardown] \n";
  exit 1;
}



sub command_setup {

  my $bq = new BQPhytomorph(mex_url  => $mex,
                            userpass => $userpass,
                            token    => $token,
                            options  => $options,
                           );

  $bq->begin_mex("initializing");
  $bq->fetchImagePlanes ($image_url,  $staging_path);

  $bq->update_mex("scheduling");
  return 0;
}

sub command_start {
  my $bq = new BQPhytomorph(mex_url => $mex, userpass => $userpass,
                            token=> $token, options=>$options );

  $bq->update_mex('running');

  return system ($EXEC,  "$staging_path/");
}


### This command is called by Condor
sub command_teardown {
  my $bq = new BQPhytomorph(mex_url => $mex, userpass => $userpass,
                            token=> $token, options=>$options );
  # Collect the condor logs and determine the status
  # Collect results, process and save
  my $tips = './tips.csv';
  my $angles = './angle.csv';
  my $gr     = './gr.csv';
  my $tags;
  if (-f $gr && -f $angles && -f $tips ) {
    eval {
      $tags = saveTipsAndAngles ($bq, $image_url, $tips, $angles, $gr ) ;
      1;
    } or do {
      $log->error("problems while saving data $@");
      $bq->finish_mex(status=>"FAILED", msg=>$@);
      return 1;
    }
  }
  # Update the MEX with state
  $bq->finish_mex ( status => "FINISHED", tags=>$tags);
  return 0;
}

sub saveTipsAndAngles {
  my ($bq, $image, $tips, $angles, $growth) = @_;

  open (TIPS, "<$tips") or die "No $tips";
  my @t = <TIPS>;
  chomp @t;
  close(TIPS);
  open (ANG, "<$angles") or die "No $angles";
  my @a = <ANG>;
  chomp @a;
  close(ANG);
  open (GROWTH, "<$growth") or die "No $angles";
  my @g = <GROWTH>;
  chomp @g;
  close(GROWTH);


  my $imagedoc = $bq->fetchxml ($image);
  my $xsize = $imagedoc->findnodes ('//image/@x')->to_literal->value;


  #print "TIPS".Dumper(@tips);
  #print "ANG".Dumper(@a);

  my $xs = new XML::Simple(RootName => undef);

  #<gobject type=tipangle>
  #   <point x= y=  t=plane>
  #   <tag name="angle" value="" />
  #<gobject>
  my @gobs ;
  my $count = @a;
  for (my $i=0; $i < $count; $i++) {
    #print "$i $a[$i]\n";
    my ($y,$x) = split(/,/, $t[$i]);
    push @gobs, { type=>"tipangle",
		   point =>  {   vertex => [ { x=> $xsize - $x, y=>$y, t=> $i} ]  },
		   tag   => [ { name=>"angle", value=> $a[$i]},
			      { name=>"growth", value=> $g[$i]}]
		 };


  }
  my $gentime = strftime ("%d-%b-%Y %H:%M", localtime);
  #my $req = {request => {gobject => [  { name => "RootTip $gentime",
  #                                       gobject => \@gobs } ]
  #}
  #};


  # my $content =  $xs->XMLout($req);
  # my $gurl    = "";
  # my $doc;
  # if ( ! $dryrun ) {
  #   $doc = $bq->postxml ($image . "/gobjects", $content);
  #   die "post failed:" . $image . "/gobjects" unless defined $doc;
  #   $gurl = $doc->findnodes('//gobject/@uri')->to_literal->value;
  # }
  # if ( $debug ) {
  #   print "GOB $gurl\n";
  #   print "GOB => $content";
  # }

  # $req = { request => { tag =>  [ { name => "RootTip",
  #   			    tag => [ { name=>"gobjects_url", type=>"link", value => $gurl},
  #   				     { name=>"mex_url", type=>"link", value => $mex} ]}]}};

  #$content =  $xs->XMLout($req);

#  if (! $dryrun ) {
#    $doc = $bq->postxml ($image . "/tags", $content);
#    die "post failed:" . $image . "/tags" unless defined $doc;
#  }
#  if ( $debug ) {
#    print "TAG => $content";
#  }

  #my $mextags = [ {name=>"gobjects_url", type=>"link", value=>$gurl} ];
  my $mextags = [ {name=>"outputs", 
                   gobject => [ { name => "RootTip $gentime",
                                  gobject => \@gobs } ]} ];
  return $mextags;
}






