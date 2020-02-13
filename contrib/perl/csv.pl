use strict;
use warnings;
use Text::CSV;
use Data::Dumper;

my $tipcsv  = <<END;
"type","name","value","x","y","z","t","ch"
resource,,
point,,
vertex,,,418.0,135.033,0.0,0.0,

point,,
vertex,,,415.0,124.033,0.0,0.0,

point,,
vertex,,,191.0,116.033,0.0,0.0,

point,,
vertex,,,101.0,118.033,0.0,0.0,

polyline,,
vertex,,,414.0,402.033,0.0,0.0,
vertex,,,778.0,254.033,0.0,0.0,

polyline,,
vertex,,,418.0,309.033,0.0,0.0,
vertex,,,382.0,150.033,0.0,0.0,
vertex,,,702.0,156.033,0.0,0.0,
END

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
1;
