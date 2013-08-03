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

  print $cgi->start_form(-action=>'/index.cgi/password'),
        $cgi->hidden('username',$username),
        $cgi->hidden('password',$password),
        $cgi->submit('Change your password'),
        $cgi->end_form;

  print $cgi->start_form(-action=>'/index.cgi/uploads'),
        $cgi->hidden('username',$username),
        $cgi->hidden('password',$password),
        $cgi->submit('Upload Files'),
        $cgi->end_form;

} elsif ( $cgi->path_info eq '/password' ) {
  print "Welcome $username - Change your password";
  print $cgi->start_form(-action=>'/index.cgi/password'),
        $cgi->hidden('username',$username),
        $cgi->hidden('password',$password);

  if ( $cgi->param('old_password') ) {
    my $error;
    $error .= $cgi->p('Your "old password" did not match.') unless $cgi->param('old_password') eq $password;
    $error .= $cgi->p('Your new passwords did not match.') unless length($cgi->param('new_password')) and $cgi->param('new_password') eq $cgi->param('check_password');

    if ( $error ) {    
      print 
          $cgi->p("ERROR:",$error),
          $cgi->p('Old Password',$cgi->param('old_password')),
          $cgi->p('New Password',$cgi->param('new_password')),
          $cgi->p('Confirm New Password',$cgi->param('check_password')),
          $cgi->submit('Set password');
    } else {
      my $ret = &update_password($username,$cgi->param('check_password'));
      print "Updating password returned ", $ret, ". ",$cgi->param('check_password'),
            $cgi->hidden('username',$username),
            $cgi->hidden('password',$cgi->param('check_password')),
            $cgi->submit('Back');
    }
  } else {
    print 
        $cgi->p('Old Password',$cgi->password_field('old_password')),
        $cgi->p('New Password',$cgi->password_field('new_password')),
        $cgi->p('Confirm New Password',$cgi->password_field('check_password')),
        $cgi->submit('Set password');
  }
  print $cgi->end_form;

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

} elsif ( $cgi->path_info eq '/uploads' ) {
  print "Welcome $username - Edit your page template";

  my $dir = &get_directory($username);
  print $dir;

  if ( $cgi->param('uploaded_file') ) {
    my $filename = $cgi->param('uploaded_file');
    my $handle   = $cgi->upload('uploaded_file');
    print $cgi->p("Saving uploaded file: $filename");
    if ( defined $handle ) {
      open (OUTFILE,'>',$dir.'/uploads/'.$filename);
      print $cgi->p("Writing to: ",$dir.'/uploads/'.$filename);
      my $buffer;
      while ( my $bytesread = read $handle, $buffer, 1024 ) {
        print OUTFILE $buffer;
      }
    }
  }

  my @files = &get_files($dir);
  print $cgi->p(@files);

  print $cgi->start_multipart_form( -action=> '/index.cgi/uploads' ),
        $cgi->hidden('username',$username),
        $cgi->hidden('password',$password),
        $cgi->filefield(-name=>'uploaded_file',-default=>'starting value',-size=>50,-maxlength=>80),
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

sub get_files {
  my $dir = shift @_;
  return () unless $dir;
  $dir .= '/uploads';
  opendir INDIR, $dir;
  my @files = grep !/^\.\.?$/, readdir INDIR;
  closedir INDIR;
  return @files;
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

sub update_password {
  my $sth = $dbh->prepare('update users set password=? where username=?');
  return $sth->execute($_[1],$_[0]);
}
