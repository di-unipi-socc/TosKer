#!/usr/bin/perl
use strict;
use warnings;

print "remote all containers..\n";
`./rm_containers.sh`;

my @files = <'./TOSCA/docker/*'>;

print "start tests..\n";

foreach my $i (@files){
  if (-d $i) {
    my @file = <"$i/*.yaml">;
    $i = $file[0];
  }
  print "$i\n";
  `python main.py $i run > /dev/null`;
  print "   run " . (($?==0) ? '✓' : '✗') . "\n";
  `python main.py $i stop > /dev/null`;
  print "   stop " . (($?==0) ? '✓' : '✗') . "\n";
  `python main.py $i delete > /dev/null`;
  print "   delete " . (($?==0) ? '✓' : '✗') . "\n";
}
