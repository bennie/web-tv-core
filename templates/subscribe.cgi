#!/usr/bin/perl -I/var/www/html/web-tv-core/

use CGI;
use DBI;
use Data::Dumper;
use HTML::Template;
use strict;

my $cgi = new CGI;
my $tmpl = HTML::Template->new(filename => '/var/www/html/web-tv-core/templates/subscribe-template.tmpl');

my $user = $LocalAuth::TV_USER;
my $pass = $LocalAuth::TV_PASS;
my $dsn = "DBI:mysql:database=".$LocalAuth::TV_DB;
my $dbh = DBI->connect($dsn, $user, $pass);

my $username = 'bennie';

if ( $cgi->param('number') ) {
  my $number = $cgi->param('number');
  my $name   = $cgi->param('name');

  print $cgi->header;

  my $body = $cgi->p("Adding the number '$number' as '$name'");
  
  my $clean_number = clean_phone($number);
  my $clean_name   = clean_name($name);
  my %db           = get_sms_list();

  if ( not defined $clean_number or $clean_number eq '' ) {
    $body .= $cgi->p("'$number' ($clean_number) does not appear to be a valid phone number.");
  } elsif ( defined $db{$clean_number} and length $db{$clean_number} ) {
    $body .= $cgi->p("'$clean_number' is already subscribed.");
  } else {
    my $ret = set_phone($clean_number,$clean_name);
    print $cgi->p("Creating phone entry: $ret");
    $ret = verify_phone($clean_number);
    print $cgi->p("Verifying phone entry: $ret");
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

sub get_sms_list {
  my $sth = $dbh->prepare('select phone, name from sms where username=? and verified is true');
  my $ret = $sth->execute($username);
  my %list;
  while ( my $ref = $sth->fetchrow_arrayref ) {
    $list{$ref->[0]} = $ref->[1];
  }
  return %list;
}

sub set_phone {
  my $phone = shift @_;
  my $name  = shift @_;

  my $sth = $dbh->prepare('insert into sms (username,phone,name,verified) values (?,?,?,false)');
  my $ret = $sth->execute($username,$phone,$name);

  return $ret;
}

sub verify_phone {
  my $phone = shift @_;

  my $sth = $dbh->prepare('update sms set verified=true where username=? and phone=?');
  my $ret = $sth->execute($username,$phone);

  return $ret;
}