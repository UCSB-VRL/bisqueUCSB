#! /usr/bin/env perl
# This script sets up the environment for matlab scripts
#  moves to condor staging directory and runs the matlab executable.
use Cwd;


#get arguments
my $executable = shift;
my $thisStagingPath = shift;
# may only need if not transfering executables via condor.
#my $executablectf = shift;
#my $executableDir = shift;

my $oldcwd = getcwd();
chdir $thisStagingPath or die "Can't chdir to staging dir $thisStagingPath";


#open log file

my $LogFile = "$thisStagingPath/launchMatlab.out";

open(OLDOUT, ">&STDOUT");
open(OLDERR, ">&STDERR");
system("pwd");
open(STDOUT, ">$LogFile") or die "Could not open $LogFile: $!\n";
open(STDERR, ">&STDOUT");
select(STDERR); $| = 1;
select(STDOUT); $| = 1;

#setup matlab environment
$ENV{HOME} = ".";
$ENV{LD_LIBRARY_PATH} = "/cluster/home/MATLAB/MATLAB_Compiler_Runtime/v710/runtime/glnxa64:/cluster/home/MATLAB/MATLAB_Compiler_Runtime/v710/sys/os/glnxa64:/cluster/home/MATLAB/MATLAB_Compiler_Runtime/v710/bin/glnxa64:/cluster/home/MATLAB/MATLAB_Compiler_Runtime/v710/sys/java/jre/glnxa64/jre/lib/amd64/native_threads:/cluster/home/MATLAB/MATLAB_Compiler_Runtime/v710/sys/java/jre/glnxa64/jre/lib/amd64/server:/cluster/home/MATLAB/MATLAB_Compiler_Runtime/v710/sys/java/jre/glnxa64/jre/lib/amd64";
$ENV{XAPPLRESDIR}  = "/cluster/home/MATLAB/MATLAB_Compiler_Runtime/v710/X11/app-defaults";
$ENV{DISPLAY} = ":0.0";
$ENV{HOME} = ".";
$ENV{MATLAB_PREF} = ".";
#setup matlab environment

#Stuff for log
system("df -k");
system("pwd");
print "Running here: ";
system("hostname");
system("ls -la");
print "Look for access to runtime in /cluster/home/MATLAB/MATLAB_Compiler_Runtime/v710/runtime/glnxa64 \n";
system("ls /cluster/home/MATLAB/MATLAB_Compiler_Runtime/v710/runtime/glnxa64");

#dont do since we are transfering files

#system("cp $executablepath .");
#system("cp $executablectf .");

system("ls -la");
system("printenv");
print "Running $executable $thisStagingPath\n";
$res = system("$executable $thisStagingPath");
print "Done Running $executable in $thisStaginPath Result was <$res>\n";

chdir $oldcwd or die "Can't cd back to $oldcwd";

if($res != 0) {
	print "Non-zero job status so exit(1)....\n";
	system("touch FAILED");
	exit(1);
}


print "Results are:";
system("ls -l");
exit ($res);
