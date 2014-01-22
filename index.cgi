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

  print $cgi->start_form(-action=>'/index.cgi/chat'),
        $cgi->hidden('username',$username),
        $cgi->hidden('password',$password),
        $cgi->submit('Chat Settings'),
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
    my $template = HTML::Template->new( scalarref => \$tmpl, option => 'value', die_on_bad_params => 0 );    
    $template->param('screen' => &screen() );
    $template->param('chat' => '<?php $chat->printChat(); ?>' );

    open OUTPUT, '>', $output or die "Can't open file: $output";
    print OUTPUT &index_header();    
    print OUTPUT $template->output;
    close OUTPUT;
    
    $tmpl = &get_page($username,'index');
    
    `if [ -d $path/jwplayer ]; then rm -rf $path/jwplayer; fi`;
    `cp -r /var/www/html/web-tv-core/resources/jwplayer $path`; 
    `if [ -d $path/chat ]; then rm -rf $path/chat; fi`;
    `cp -r /var/www/html/web-tv-core/resources/chat $path`;
    `if [ ! -d $path/uploads ]; then mkdir $path/uploads; fi`;
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

sub get_param {
  my $user  = shift @_;
  my $param = shift @_;
  my $sth = $dbh->prepare('select value from params where username=? and param=?');
  my $ret = $sth->execute($user,$param);
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

sub set_param {
  my $user  = shift @_;
  my $param = shift @_;
  my $value = shift @_;
  return undef unless defined $user and defined $param and defined $value;
  my $sth = $dbh->prepare('select count(*) from params where username=? and param=?');
  my $ret = $sth->execute($user,$param);
  my $count = $sth->fetchrow_arrayref->[0];
  
  if ( $count > 0 ) {
    $sth = $dbh->prepare('update params set value=? where username=? and param=?');
    return $sth->execute($value,$user,$param);
  } else {
    $sth = $dbh->prepare('insert into params (username,param,value) values (?,?,?)');
    return $sth->execute($user,$param,$value);
  }
}

### Big things

sub index_header {
  #set_param($username,'chat_title',"Chat");
  #set_param($username,'chat_channel',"pumapaw");

  my $chat_title   = get_param($username,'chat_title');
  my $chat_channel = get_param($username,'chat_channel');

  return '<?php

require_once dirname(__FILE__)."/chat/src/phpfreechat.class.php";

$params = array();

$params["serverid"] = md5(__FILE__); // calculate a unique id for this chat

$params["title"] = "'.$chat_title.'"; // Chat title
$params["channels"] = array("'.$chat_channel.'"); // Default channel to join
$params["frozen_channels"] = array("'.$chat_channel.'"); // Only one channel allowed

$params["theme"] = "wolf"; // Custom style
$params["height"] = "430px"; // Height. No width setting sadly
$params["displaytabclosebutton"] = false; // Get rid of the tab, wish this worked
$params["displaytabimage"] = false; // Get rid of the tab, wish this worked
$params["display_pfc_logo"] = false; // Remove the logo for phofreechat.net

$params["admins"] = array( "OtherAdmin" => "nopassword", "Wolf" => "nopassword" ); // Admin info
$params["nick"] = ""; // Force people to chose a nickname

$params["shownotice"] = 5; // Show kicks and renicks
$params["showsmileys"] = false; // Hide the smiley box at first
$params["showwhosonline"] = false; // hide the user box at first

$params["skip_proxies"] = array("censor"); // We don\'t mind naughty words.

$params["nickname_colorlist"] = array(
  "#000000", "#3636B2", "#2A8C2A", "#C33B3B", "#C73232",
  "#80267F", "#66361F", "#D9A641", "#3DCC3D", "#1A5555",
  "#2F8C74", "#4545E6", "#B037B0"
);

$chat = new phpFreeChat($params);

?>';
}

sub screen {
  #set_param($username,'rtmp_url',"rtmp://tv.pumapaw.com/oflaDemo/cougrtv");
  set_param($username,'player_url',"http://tv.pumapaw.com/uploads/traci.jpg");

  my $playerid = 'player_'.$username;

  my $player_url = get_param($username,'player_url');
  my $rtmp_url   = get_param($username,'rtmp_url');
  
  return '<script type=\'text/javascript\' src=\'/jwplayer/jwplayer.js\'></script>
<div id="'.$playerid.'">
  <h1>You need the Adobe Flash Player for this demo, download it by clicking the image below.</h1>
  <p><a href="http://www.adobe.com/go/getflashplayer"><img src="http://www.adobe.com/images/shared/download_buttons/get_flash_player.gif" alt="Get Adobe Flash player" /></a></p>
</div>
<script type=\'text/javascript\'>
  jwplayer("'.$playerid.'").setup({
    file: "'.$rtmp_url.'",
    width: "640",
    height: "360",
    primary: "flash",
    image: "'.$player_url.'",
    autostart: "true",
  });

  var timer=10000;
  jwplayer().onIdle(function() {
  	t=setTimeout("jwplayer().play()",10000);
  });

</script>';
}
