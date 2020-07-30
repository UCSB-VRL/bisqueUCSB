package BQPhytomorph::Condor;

use warnings;
use strict;


use POSIX qw/strftime/;
use Cwd qw/abs_path getcwd/;
use File::Path qw/rmtree/;
use Data::Dumper;

=head1 NAME

BQPhytomorph::Condor - The great new BQPhytomorph::Condor!

=head1 VERSION

Version 0.01

=cut

our $VERSION = '0.01';

=head1 SYNOPSIS
Provide interface functions for Condor 

Perhaps a little code snippet.

    use BQPhytomorph::Condor;

    my $bc = BQPhytomorph::Condor->new({staging=> A shared directory });
    $bc->start ()

    or

    my $bc = BQPhytomorph::Condor->new({staging=> A shared directory, series_id = "asasa" });
    my $status =  $bc->finish ()
    $bc->cleanup();

=head1 EXPORT

A list of functions that can be exported.  You can delete this section
if you don't export anything, such as for a purely object-oriented module.

#Declare Constants 
our $STAGINGPATH = "/cluster/home/bqphytomorph/staging/"; 
our $MATLABLAUNCHERNAME = "doextract.pl"; 
our $MATLABLAUNCHER = "/home/bqphytomorph/condorscripts/" . $MATLABLAUNCHERNAME; 
our $POSTSCRIPT = "/home/bqphytomorph/condorscripts/postjob.pl"; 



=head1 FUNCTIONS

=head2 new

   my $bc= new BQPhytomorph::Condor(
                                      staging =>  A directory to stage the executable in
                                      script => The executable script path
                                    );
   $bc -> start ();

   ....

=cut

sub new {
  my($class, %args) = @_;
  my $self = bless({}, $class);

  #print Dumper(%args);
  
  $self->{staging} = exists $args{staging}? $args{staging} : undef;
  $self->{series_id}  = exists $args{series_id}? $args{series_id} : undef;

  $self->{script} = exists $args{script}? $args{script} : '';
  $self->{script_args} = exists $args{script_args}? $args{script_args} : '';
  
  $self->{post_exec} = exists $args{post_exec}? $args{post_exec} : '';
  $self->{post_args} = exists $args{post_args}? $args{post_args} : '';

  $self->{transfers} = exists $args{transfers}? $args{transfers} : '';
  $self->{debug} = exists $args{debug}? $args{debug} : 0;
  $self->{dryrun} = exists $args{drynrun}? $args{dryrun} : 0;

  $self->{cmd_extra} = exists $args{cmd_extra}? $args{cmd_extra} : '';
  $self->{requirements} = exists $args{requirements}? $args{requirements}:'';



  unless ( $self->{series_id} ) {
    $self->{series_id} = strftime("%Y%m%d.%H%M%S", localtime);
  }
  $self->{path} = "$self->{staging}/$self->{series_id}/";
  unless (-d $self->{path}) {
    mkdir $self->{path} or die;
  }
  $self->{path} =  abs_path("$self->{path}");
  $self->{logdir} = $self->{path};


  return $self;
}




sub _construct_dag {
  my $self = shift;
  my $dag = <<END;
JOB $self->{series_id}  ./$self->{series_id}.cmd
CONFIG ./$self->{series_id}.dag.config 
SCRIPT POST $self->{series_id} $self->{post_exec} $self->{post_args}
RETRY $self->{series_id} 5
END

  my $f = "$self->{path}/$self->{series_id}.dag"; 
  print "Creating $f\n"   if ($self->{debug} > 0);

  open(CDAG,">$f")
    or die "Can not write dag file<$f>:$!\n";
  print CDAG $dag;
  close(CDAG);
}



#################
# Construct  DAG.config
#
sub _construct_dag_config {
  my $self = shift;

  my $f = "$self->{path}/$self->{series_id}.dag.config";
  print "Creating $f\n" if ($self->{debug} > 0);

  open(CDAGC,">$f") 
    or die "Can not write dag file<$f>:$!\n";
  print CDAGC "DAGMAN_LOG_ON_NFS_IS_ERROR = FALSE \n";
  close(CDAGC);

}

###########################
# Construct do_extract
#
sub _construct_submit {
  my $self = shift;

  if ($self->{requirements} ne '') {
    $self->{requirements} = "&& $self->{requirements}";
  }


  my $submit = <<END;

universe = vanilla
executable = $self->{script}
error = ./launcher.err
output = ./launcher.out
log = ./launcher.log
match_list_length = 5
requirements = (Arch == "x86_64") && (TARGET.Name =!= LastMatchName1) && (OpSys == "LINUX") $self->{requirements}
on_exit_remove = (ExitBySignal == False)&&(ExitCode == 0)
#periodic_remove = (ImageSize >= 2000000) || (((JobStatus == 2)&&(JobUniverse == 5)&&((CurrentTime - JobCurrentStartDate) > (60 * 60 * 8))) =?= TRUE)
should_transfer_files = YES
when_to_transfer_output = ON_EXIT_OR_EVICT
arguments = $self->{script_args}
initialdir = $self->{path}
Notification = never
transfer_input_files = $self->{transfers}
$self->{cmd_extra}

queue
END


  #write submit
  my $cmd = "$self->{path}/$self->{series_id}.cmd";
  print "Creating $cmd \n"   if ($self->{debug} > 0);

  open(CSUB,">$cmd") 
     or die "Can not write submit file<$cmd>:$!\n"; 
  print CSUB $submit;
  close(CSUB);
}


sub _submit_condor {
  my $self = shift;


  #if using dbq
  #system("condor_submit_dag -no_submit -usedagdir $imageDir/$seriesID.dag");
  #system("/home/bqphytomorph/condor_dbq.pl --dbinfodir=/home/bqphytomorph/dbinfo --submit=$imageDir/$seriesID.dag.condor.sub");
  
  ###############
  # Submit Job
  if ($self->{debug} > 0) {
    print "condor_submit_dag $self->{path}/$self->{series_id}.dag\n";
  }
  if (! $self->{dryrun}) {
    my $dir = getcwd();
    chdir $self->{path};

    if ($self->{post_exec} ne '') {
      system("condor_submit_dag $self->{path}/$self->{series_id}.dag");
    }else {
      system("condor_submit $self->{path}/$self->{series_id}.cmd");
    }
    chdir $dir;
  }
}

=head2 staging_dir

=cut

sub staging_dir {
  my $self = shift;
  return $self->{path};

}
=head2 find_file
=cut

sub find_file {
  my $self = shift;
  my $filename = shift;

  if (-f "$self->{path}/$filename") {
    return "$self->{path}/$filename";
  }
}

=head2 start
   Start a condor job
=cut
sub submit {
  my ($self, %args ) = @_;

  # Update the variabiles with any arguments passed in
  foreach my $k (keys %args ) {
     $self->{$k} = $args{$k};
  }

  if ($self->{post_exec} ne '' ) {
    $self->_construct_dag();
    $self->_construct_dag_config ();
  }
  $self->_construct_submit();
  $self->_submit_condor();
}


=head2 finish
   Finish  a condor job and return the status
=cut

sub finish {
  my $self = shift;

  if (-f "RETRY") {
    #print "Job never finished. RETRY\n";
    system("rm -rf RETRY");
    return "FAILURE";
  }

  return "FINISHED";
}


=head2 cleanup
   Cleanup the staging directory
=cut

sub cleanup {
  my $self = shift;

  # Remove the tree with all staging data
  ####  rmtree $self->{path};

}


=head1 AUTHOR

CBI, C<< <bisque-dev at biodev.ece.ucsb.edu> >>

=head1 BUGS

Please report any bugs or feature requests to C<bug-bqphytomorph-condor at rt.cpan.org>, or through
the web interface at L<http://rt.cpan.org/NoAuth/ReportBug.html?Queue=BQPhytomorph-Condor>.  I will be notified, and then you'll
automatically be notified of progress on your bug as I make changes.




=head1 SUPPORT

You can find documentation for this module with the perldoc command.

    perldoc BQPhytomorph::Condor


You can also look for information at:

=over 4

=item * RT: CPAN's request tracker

L<http://rt.cpan.org/NoAuth/Bugs.html?Dist=BQPhytomorph-Condor>

=item * AnnoCPAN: Annotated CPAN documentation

L<http://annocpan.org/dist/BQPhytomorph-Condor>

=item * CPAN Ratings

L<http://cpanratings.perl.org/d/BQPhytomorph-Condor>

=item * Search CPAN

L<http://search.cpan.org/dist/BQPhytomorph-Condor>

=back


=head1 ACKNOWLEDGEMENTS


=head1 COPYRIGHT & LICENSE

Copyright 2010 CBI, all rights reserved.

This program is free software; you can redistribute it and/or modify it
under the same terms as Perl itself.


=cut

1; # End of BQPhytomorph::Condor
