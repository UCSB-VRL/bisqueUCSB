
sub saveTipsAndAngles {
  my ($bq, $mexurl, $tips, $angles) = @_;

  my @tips, @angles;
  open (TIPS, "<$tips");
  my @tips = <TIPS>;
  close(TIPS);
  open (ANG, "<$angles");
  @angles = <ANG>;
  close(ANG);


#   my $doc = XML::LibXML::Document->new();
#   my $root=$doc->createElement('request');

#   for (my $i=0; i < @tips; $i++) {
#     my $gob = $doc->createElement ();
#     $root->appendChild ($gobject);
#   }    
  
  my $xs = new XML::Simple(RootName => undef);

  my $doc = {
    request => {
		gobject : []
	       } 
	    };
	     

  #<gobject type=tipangle>
  #   <point x= y=  t=plane>
  #   <tag name="angle" value="" />
  #<gobject>
  my $gobs = $doc{request}{gobject};
  for (my $i=0; i < @tips; $i++) {
    my $x,$y = split(/,/, $tips[i]);
    push @$gobs, { type=>"tipangle",
		   point => { x=> $x, y=>$y, t=> $i},
		   tag   => { name=>"angle", value=> $angles[i]}
		 };


  }
  print $xs->XMLout($doc);
  
}


\saveTipsAndAngles('tips.csv', 'angles.csv');

