#!/usr/bin/perl

use CGI;
use CGI::Carp qw/fatalsToBrowser/;
use DBI;
use HTML::Template;
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
  print $cgi->start_form( -action=> '/index.cgi/edit' ),
        $cgi->hidden('username',$username),
        $cgi->hidden('password',$password),
        $cgi->submit('Edit Template'),
        $cgi->end_form;

} elsif ( $cgi->path_info eq '/edit' ) {
  print "Welcome $username - Edit your page template";
  
  my $tmpl = &get_page($username,'index');

  if ( $cgi->param('template') ) {
    my $ret = &update_page($username,'index',$cgi->param('template'));
    print $cgi->p("DB Update returned: $ret");
    my $path = &get_directory($username);
    my $output = $path .'/index.php';       
    print $cgi->p("Writing $output");
    open OUTPUT, '>', $output or die "Can't open file: $output";
    print OUTPUT $tmpl;
    close OUTPUT;
    $tmpl = &get_page($username,'index');
  }
  
  print $cgi->start_form( -action=> '/index.cgi/edit' ),
        $cgi->hidden('username',$username),
        $cgi->hidden('password',$password),
        $cgi->textarea(-cols=>80,-rows=>20,-name=>'template',-value=>$tmpl),
        $cgi->submit('Save'),
        $cgi->end_form;

} else {
  print '[ <a href="/index.cgi/login">Admin</a> ]';
  print $cgi->ul( map {$cgi->li($cgi->a({-href=>'http://'.$_.'/'},'http://'.$_.'/'))} &list_sites() );

}

### Footer

print $cgi->p('Path:',$cgi->path_info);
for my $param ( $cgi->param ) {
  #print $cgi->p($param,$cgi->param($param));
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

sub get_directory {
  my $sth = $dbh->prepare('select directory from users where username=?');
  my $ret = $sth->execute(@_);
  return $sth->fetchrow_arrayref->[0];
}

sub get_page {
  my $user = shift @_;
  my $page = shift @_;
  my $sth = $dbh->prepare('select page from page where username=? and pagename=?');
  my $ret = $sth->execute($user,$page);
  return $sth->fetchrow_arrayref->[0];
}

sub list_sites {
  my $sth = $dbh->prepare('select site from users order by site');
  my $ret = $sth->execute();
  my @out;
  while ( my $ref = $sth->fetchrow_arrayref ) {
    push @out, $ref->[0];
  }
  return @out;
}

sub update_page {
  my $sth = $dbh->prepare('update page set page=? where username=? and pagename=?');
  return $sth->execute($_[2],$_[0],$_[1]);
}
