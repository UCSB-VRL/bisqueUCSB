#!/usr/bin/perl
package BQPhytomorph::RootTipMulti;

use warnings;
use strict;

use Cwd 'abs_path';
use File::Basename;
use File::Copy;
use Getopt::Long;
use XML::LibXML;
use XML::Simple;
use Data::Dumper;
use POSIX qw/strftime/;
use URI::Escape;
use Log::Log4perl;

use BQPhytomorph;

our $EXEC          = "./maizeG";
my $log = Log::Log4perl::get_logger('roottipmulti');

#########################################
## Argument handling
my ($help, $image, $mex, $user, $password, $userpass, $staging_path, $token);
my $debug = 0;
my $dryrun = 0;

usage() if ( ! GetOptions('help|?' => \$help,
                          'debug|d' => \$debug,
                          'dryrun|n' => \$dryrun,
                          'mex_url=s' => \$mex,
                          'image_url=s' => \$image,
                          'staging_path=s'=>\$staging_path,
                          'user=s' => \$user,
                          'password=s' => \$password,
                          'token=s'=>\$token,
                         )
          or defined $help );
my $options = { debug=> $debug, dryrun => $dryrun };
my $command  = shift;

usage() if (!defined $command);


if ($user && $password) {
  $userpass = $user . ':' . $password;
}
print "command is " . $command . "\n";

my $ret=0;
$ret=command_setup() if ($command eq 'setup');
$ret=command_teardown() if ($command eq 'teardown');
$ret=command_start() if ($command eq 'start');

exit($ret);


sub usage {
  print "Unknown option: @_\n" if ( @_ );
  print "usage: RootTip [--mex=URL] [--userpass=USER:PASS] [--image_url=IMAGE] [--staging=PATH] [--debug] [--help]  [start|setup|teardown] \n";
  exit 1;
}

sub command_fetch {
  my $bq = new BQPhytomorph(mex => $mex, userpass => $userpass ) if ( $mex) ;
  fetchGObjectsAsCSV($bq, $mex, $staging_path);
}


sub command_setup {
  print "SETUP\n";
  my $bq = new BQPhytomorph(mex_url => $mex, userpass => $userpass,
                            token=> $token, options=>$options );
  $bq->update_mex("initializing");

  $bq->fetchImagePlanes ($image,  $staging_path);
  fetchGObjectsAsCSV($bq, $mex, $staging_path);

  $bq->update_mex('scheduling');
  return 0;
}

sub command_start {
  print "START $EXEC $staging_path/ \n";
  my $bq = new BQPhytomorph(mex_url => $mex, userpass => $userpass,
                            token=> $token, options=>$options );

  $bq->update_mex("running");
  return system ($EXEC,  "$staging_path/");
}


### This command is called by Condor
sub command_teardown {
  print "TEARDOWN\n";

  my $bq = new BQPhytomorph(mex_url => $mex, userpass => $userpass,
                            token=> $token, options=>$options );

  # Collect the condor logs and determine the status

  # Collect results, process and save
  my $tips = './tips.csv';
  my $angles = './angles.csv';
  my $tags;
  if (-f $tips && -f $angles ) {
    eval {
      $tags = saveTipsAndAngles ($bq, $mex, $image, $tips, $angles ) ;
      1;
    } or do {
      $bq->finish_mex ( status=>"FAILED", msg=>$@  );
      return 1;
    }
  }
  # Update the MEX with state
  $bq->finish_mex ( status=>"FINISHED",  tags=>$tags);
  return 0;
}

sub fetchGObjectsAsCSV {
  my ($bq, $mexurl, $staging) = @_;

  # Parse the gobject creating a CSV

  my @tips;
  my $count = 0;

  my $mexdoc = $bq->fetchxml ($mexurl."?view=deep");
  die "fetch failed:" . $mexurl unless defined $mexdoc;

  my @vertices = $mexdoc->findnodes ('//vertex');
  for my $v (@vertices) {
    my $x = int ($v->getAttribute('x'));
    my $y = int ($v->getAttribute('y'));
    push (@tips ,  "$y, $x");
    #print "$y, $x";
  }
  if (scalar @tips == 0) {
      die "Can't get input points from mex" ;
  }

  my $tipout = abs_path ($staging .'/inputtips.csv');

  open(TIPS, ">$tipout");
  foreach my $tip (@tips) { 
    print TIPS "$tip\n";
  }
  close(TIPS);
}


sub saveTipsAndAngles {
  my ($bq, $mex, $image, $tips, $angles) = @_;

  open (TIPS, "<$tips") or die "No $tips";
  my @t = <TIPS>;
  chomp @t;
  close(TIPS);
  open (ANG, "<$angles") or die "No $angles";
  my @a = <ANG>;
  chomp @a;
  close(ANG);
#   open (GROWTH, "<$growth") or die "No $angles";
#   my @g = <GROWTH>;
#   chomp @g;
#   close(GROWTH);

  #print "TIPS".Dumper(@tips);
  #print "ANG".Dumper(@a);

  my $xs = new XML::Simple(RootName => undef);

  my $imagedoc = $bq->fetchxml ($image);
  die "fetch failed:" . $image unless defined $imagedoc;

  my $xsize = $imagedoc->findnodes ('//image/@x')->to_literal->value;
  my $ysize = $imagedoc->findnodes ('//image/@y')->to_literal->value;

  # <gobject name="Tip 1" >
  #    <gobject type=tipangle>
  #      <point x= y=  t=1..N  >
  #      <tag name="angle" value="" />
  #    <gobject>
  #    ...
  # </gobject>
  # <gobject name="Tip 2" >
  #
  my $count = @a;
  my @gobs ;
  my @angles = split (/,/, $a[0]);
  my $tip_count = @angles;
  for (my $i=0; $i<$tip_count ; $i++){
    push @gobs, [];
  }

  for (my $i=0; $i < $count; $i++) {
    #print "$i $a[$i]\n";
    #my ($x,$y) = split(/,/, $t[$i]);
    my @points = split(/,/, $t[$i]);
    my @angles = split(/,/, $a[$i]);
    #my @growths = split(/,/, $g[$i]);

    for (my $g=0; $g<$tip_count; $g++){
      push @{$gobs[$g]}, 
	{ type=>"tipangle",
	  point =>  {   vertex => [ { x=> $points[$g*2], y=> $points[$g*2+1], t=> $i} ]  },
	  tag   => [ { name=>"angle", value=> $angles[$g]},
		     #				      { name=>"growth", value=> $growths[$g]}
		   ]
	};
    }
  }

  my $gentime = strftime ("%Y-%m-%d %H:%M:%S", localtime);
  my $req = {request => {  gobject =>
			   [{ name => "RootTip  $gentime",
			      gobject => [] } ]
                        }
            };

  for (my $g=0; $g<$tip_count; $g++){
    push @{$req->{request}->{gobject}[0]->{gobject}}, { name => "Tip-" . ($g+1),
							gobject=>\@{$gobs[$g]}};
  }


  my $content =  $xs->XMLout($req);
  #print $content;
  my $gurl    = "";
  my $doc;
  if ( ! $dryrun ) {
    $doc = $bq->postxml ($image . "/gobjects", $content);
    die "post failed:" . $image . "/gobjects" unless defined $doc;
    $gurl = $doc->findnodes('//gobject/@uri')->to_literal->value;
  }

  if ( $debug ) {
    print "GOB $gurl\n";
    print "GOB => $content";
  }

  my $xpath="";
  for (my $g=0; $g<$tip_count; $g++){
    if (! $xpath) {
      $xpath = "&xpath=";
    } else { 
      $xpath .= "&xpath" . ($g).'=';
    }
    $xpath .= uri_escape('//gobject[@name="' . "Tip-" . ($g+1) . '"]//tag[@name="angle"]');
  }

  $req = { request => 
           { tag =>  
             [ { name => "RootTip",
                 tag => [ { name=>"gobjects_url", type=>"link", value=>$gurl},
                          { name=>"mex_url", type=>"link", value=>$mex},
                          { name=>'date_time', value=> $gentime },
                          { name=>"area-histogram", type=>"statistics",
                            value => ("http:/stats?url=" . uri_escape($gurl)
                                      .$xpath
                                      ."&xmap=".uri_escape("tag-value-number")
                                      ."&xreduce=vector&run=true")},
                        ]}]}};





  $content =  $xs->XMLout($req);

  if (! $dryrun ) {
    $doc = $bq->postxml ($image . "/tags", $content);
    die "post failed:" . $image . "/tags" unless defined $doc;
  }
  if ( $debug ) {
    print "TAG => $content";
  }

  my $mextags = [ {name=>"gobjects_url", type=>"link", value=>$gurl} ];
  return $mextags;
}
