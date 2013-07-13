#!/usr/bin/perl

use CGI;
use CGI::Carp qw/fatalsToBrowser/;
use DBI;
use strict;

my $cgi = new CGI;

my $user = 'username';
my $pass = 'password';
my $dsn = "DBI:mysql:database=mydatabase";
my $dbh = DBI->connect($dsn, $user, $pass);

### Check password 

my $check = 0;
my $username = $cgi->param('username');
my $password = $cgi->param('password');

if ( $username and $password ) {
  $check =  &check_password( $cgi->param('username'),  $cgi->param('password') );
}

#### Handle pages

if ( $check < 1 and $cgi->path_info and $cgi->path_info ne '/login' ) {
  print $cgi->redirect('/index.cgi/login');
  exit 0;
}

print $cgi->header, $cgi->start_html('TV Sites');
print '<body bgcolor="#FFFFFF">';

if ( $cgi->path_info eq '/login' ) {
  print $cgi->p("Bad login.") if $username or $password;
  print $cgi->start_form( -action=> '/index.cgi/dashboard' ), $cgi->textfield('username'),
        $cgi->password_field('password'), $cgi->submit, $cgi->end_form;

} elsif ( $cgi->path_info eq '/dashboard' ) {

  print "Welcome $username";

} else {
  print '[ <a href="/index.cgi/login">Admin</a> ]

<ul>
<li> <a href="http://noben.tv.furfolk.com/">http://noben.tv.furfolk.com/</a>
<li> <a href="http://wolf.tv.macrophile.com/">http://wolf.tv.macrophile.com/</a>
</ul>';
}

### Footer

print $cgi->p('Path:',$cgi->path_info);
for my $param ( $cgi->param ) {
  print $cgi->p($param,$cgi->param($param));
}
print '</body></html>';

### Subs

sub check_password {
  my $user = shift @_;
  my $pass = shift @_;
  my $sql = 'select count(*) from users where username=? and password=?';
  my $sth = $dbh->prepare($sql);
  my $ret = $sth->execute($user,$pass);
  return $sth->fetchrow_arrayref->[0];
}
