#!/usr/bin/perl

use CGI;
use Data::Dumper;
use DB_File;
use HTML::Template;
use strict;

my $cgi = new CGI;
my $tmpl = HTML::Template->new(filename => 'template.tmpl');

if ( $cgi->param('number') ) {
  my $number = $cgi->param('number');
  my $name   = $cgi->param('name');

  print $cgi->header;

  my $body = $cgi->p("Adding the number '$number' as '$name'");
  
  my $clean_number = &clean_phone($number);
  my $clean_name = &clean_name($name);

  tie my %db, 'DB_File', 'subscribers.db'
    or die "Cannot create DB file: $!\n";

  if ( not defined $clean_number or $clean_number eq '' ) {
    $body .= $cgi->p("'$number' ($clean_number) does not appear to be a valid phone number.");
  } elsif ( defined $db{$clean_number} and length $db{$clean_number} ) {
    $body .= $cgi->p("'$clean_number' is already subscribed.");
  } else {
    $db{$clean_number} = $clean_name;
  }
  
  $tmpl->param( body => $body );

} else {
  print $cgi->header;
  my $body = $cgi->start_form()
           . $cgi->h3("Subscribe to Wolf TV! Get SMS alerts when a stream starts!")
           . $cgi->table(
             $cgi->Tr(
               $cgi->td($cgi->b('Phone:')),
               $cgi->td($cgi->textfield(-name=>'number'),'(with area code)')
             ),
             $cgi->Tr(
               $cgi->td($cgi->b('Fan Name:')),
               $cgi->td($cgi->textfield(-name=>'name'),'(optional, for Wolf\'s eyes only.)')
             )
           )
           . $cgi->br
           . $cgi->submit('Add your number!')
           . $cgi->end_form;
  $tmpl->param( body => $body );
}

print $tmpl->output();

### Subroutines

sub clean_name {
  return shift @_;
}

sub clean_phone {
  my $raw = shift @_;
  $raw =~ s/[^0-9+]//g; 

  my $num;
  
  if ( $raw =~ /^\+1\d{8,15}$/ ) {
    $num = $raw; # International
  }

  if ( $raw =~ /^1?(\d{10})$/ ) {
    $num = $1; # Domestic
  }
  
  return $num;
}