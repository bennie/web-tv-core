#!/usr/bin/perl

use CGI;
use CGI::Carp qw/fatalsToBrowser/;
use DBI;
use HTML::Template;
use LocalAuth;
use WWW::Twilio::API;
use strict;

my $cgi = new CGI;

my $user = $LocalAuth::TV_USER;
my $pass = $LocalAuth::TV_PASS;
my $dsn = "DBI:mysql:database=".$LocalAuth::TV_DB;
my $dbh = DBI->connect($dsn, $user, $pass);

my $default_player_image = 'http://tv.macrophile.com/resources/default-images/focus.jpg';

### Check password

my $check = 0;
my $username = $cgi->param('username');
my $password = $cgi->param('password');

if ( $username and $password ) {
  $check =  check_password( $cgi->param('username'),  $cgi->param('password') );
}

#### Handle pages

if ( $check < 1 and $cgi->path_info and $cgi->path_info ne '/login' ) {
  print $cgi->redirect('/index.cgi/login');
  exit 0;
}

### Common header

print $cgi->header, $cgi->start_html( -title=>'TV Sites', -style=>{'src'=>'/resources/sample.css'}, -head => '<!--[if lt IE 7]><script src="http://ie7-js.googlecode.com/svn/version/2.0(beta3)/IE7.js" type="text/javascript"></script><![endif]-->'."\n".'<!--[if lt IE 8]><script src="http://ie7-js.googlecode.com/svn/version/2.0(beta3)/IE8.js" type="text/javascript"></script><![endif]-->' );
print '<body bgcolor="#FFFFFF">
<div id="doc3" class="yui-t1">
   <div id="hd" role="banner"><h1>TV Sites</h1></div>
   <div id="bd" role="main">
	<div id="yui-main">
	<div class="yui-b"><div class="yui-g">
';

### DASHBOARD	
if ( $cgi->path_info eq '/dashboard' ) {
  print "Welcome $username";

  print $cgi->start_form(-action=>'/index.cgi/sms'),
        $cgi->hidden('username',$username),
        $cgi->hidden('password',$password),
        $cgi->submit('Send SMS Message'),
        $cgi->end_form;

  print $cgi->br;

  print $cgi->start_form( -action=> '/index.cgi/edit' ),
        $cgi->hidden('username',$username),
        $cgi->hidden('password',$password),
        $cgi->submit('Edit Template'),
        $cgi->end_form;

  print $cgi->start_form(-action=>'/index.cgi/params'),
        $cgi->hidden('username',$username),
        $cgi->hidden('password',$password),
        $cgi->submit('Tweak Params'),
        $cgi->end_form;

  print $cgi->start_form(-action=>'/index.cgi/uploads'),
        $cgi->hidden('username',$username),
        $cgi->hidden('password',$password),
        $cgi->submit('Upload Files'),
        $cgi->end_form;

  print $cgi->br;

  print $cgi->start_form(-action=>'/index.cgi/password'),
        $cgi->hidden('username',$username),
        $cgi->hidden('password',$password),
        $cgi->submit('Change your password'),
        $cgi->end_form;

### EDIT
} elsif ( $cgi->path_info eq '/edit' ) {
  print "Edit your page template";

  if ( $cgi->param('template') ) {
    my $ret = update_page($username,'index',$cgi->param('template'));
    print $cgi->p("DB Update returned: $ret");
    write_pages($username);
  }

  my $tmpl = get_page($username,'index');

  print $cgi->start_form( -action=> '/index.cgi/edit' ),
        $cgi->hidden('username',$username),
        $cgi->hidden('password',$password),
        $cgi->textarea(-cols=>80,-rows=>20,-name=>'template',-value=>$tmpl),
        $cgi->br, $cgi->submit('Save'),
        $cgi->end_form, $cgi->br,
        $cgi->code('&lt;tmpl_var name="CHAT"&gt; - This is the template tag for where the chat screen will be.'), $cgi->br,
        $cgi->code('&lt;tmpl_var name="SCREEN"&gt; - This is the template tag for where the video player will be.'), $cgi->br,
        $cgi->br,
        $cgi->code('&lt;tmpl_var name="TITLE"&gt; - The title of your streaming site as you configured in params:',get_param('title')), $cgi->br,
        $cgi->code('&lt;tmpl_var name="USERNAME"&gt; - Your login username here:',$username), $cgi->br,
        $cgi->code('&lt;tmpl_var name="UC_USERNAME"&gt; - A first-letter-upper-cased version of your username:',ucfirst($username));

### LOGIN
} elsif ( $cgi->path_info eq '/login' ) {
  print $cgi->p("Bad login.") if $username or $password;
  print $cgi->start_form( -action=> '/index.cgi/dashboard' ),
          $cgi->b('User: '), $cgi->textfield('username'), $cgi->br,
          $cgi->b('Pass: '), $cgi->password_field('password'), $cgi->br,
          $cgi->submit, $cgi->end_form;

### PASSWORD
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
      my $ret = update_password($username,$cgi->param('check_password'));
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

### PARAMS
} elsif ( $cgi->path_info eq '/params' ) {
  print $cgi->h3("Parameters to tweak:");

  my %params = (
    title           => 'Title of the overall livestream window',
    chat_title      => 'The title of the overall chat window.',
    chat_channel    => 'The title of the chat channel. The chat is configured to lock to this channel.',
    chat_height     => 'The height of the chat box in pixels.',
    chat_admin_user => 'Chat admin user, this chat nickname can control the chat.',
    chat_admin_pass => 'Chat admin password to take control of the channel.',
    player_height   => 'The height of the player window in pixels.',
    player_width    => 'The width of the player window in pixels.',
    player_url      => 'The URL of the default background image for the player.',
    priv_user       => 'User for the private site.',
    priv_pass       => 'Password for the private site.',
    rtmp_url        => 'The RTMP URL the player is configured to read from.'
  );

  my @order = qw/title chat_title chat_channel chat_height 
                 chat_admin_user chat_admin_pass 
                 priv_user priv_pass 
                 player_width player_height player_url rtmp_url/;

  my $made_changes = 0;
  for my $param_name (@order) {
    my $submitted_value = $cgi->param($param_name);
    next unless defined $submitted_value;
    my $check = get_param($param_name);
    next if $check eq $submitted_value;
    my $ret = set_param($username,$param_name,$submitted_value);
    print $cgi->p("Setting '$param_name' to '$submitted_value' returned $ret");
    $made_changes++;
  }

  write_pages() if $made_changes;

  print $cgi->start_form(-action=>'/index.cgi/params'),
        $cgi->hidden('username',$username),
        $cgi->hidden('password',$password),
        $cgi->start_table;

  for my $param ( @order ) {
    my $value = get_param($param);

    print $cgi->Tr(
            $cgi->td($cgi->b($param)),
            $cgi->td($cgi->textfield(-size=>60,-maxlength=>255,-name=>$param,-value=>$value)),
            $cgi->td($params{$param})
          );
  }

  print $cgi->end_table, $cgi->submit('Update values'), $cgi->end_form;

### SMS
} elsif ( $cgi->path_info eq '/sms' ) {

  if ( $cgi->param('message') ) {
    print $cgi->h3("Sending SMS messages:");

    my $message = $cgi->param('message');
    print $cgi->blockquote($message),
          $cgi->p("Sending messages...");

    my %db = get_sms_list();
    for my $number ( keys %db ) {
      my $ret = send_message($number,$cgi->param('message'));
      print $cgi->p($number,'...',$ret->{message},'('.$ret->{code}.')');
    }

  } else {
    print $cgi->h3("Send an SMS message:");
    my $site  = get_site($username);
    my $title = get_param('title');

    print $cgi->start_form(-action=>'/index.cgi/sms'),
          $cgi->hidden('username',$username),
          $cgi->hidden('password',$password),
          $cgi->textarea(
            -name => 'message', -rows => 5, -columns=> 50,
            -default => "http://$site/ - $title is now Online!"
          ),
          $cgi->br,
          $cgi->submit,
          $cgi->end_form;
      my %db = get_sms_list();
      print $cgi->p('The current list:');
      for my $number ( keys %db ) {
  	    print $number, "\t", $db{$number}, $cgi->br, "\n";
      }
  }

### UPLOADS
} elsif ( $cgi->path_info eq '/uploads' ) {

  my $dir = get_directory($username);
  #print "Actual working directory: $dir";

  # Handle deletes
  if ( $cgi->param('delete_file') ) {
    my $file_to_delete = $dir . '/uploads/' . $cgi->param('delete_file');
    print $cgi->p("Deleting $file_to_delete");
    unlink($file_to_delete);
  }

  # Handle uploads
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

  print $cgi->h3("Your uploaded files:");
  my @files = get_files($dir);

  print $cgi->start_table;
  for my $file (@files) {
    print $cgi->Tr(
            $cgi->td('http://'.get_site($username).'/uploads/'.$file),
            $cgi->td($cgi->start_form(-action=>'/index.cgi/uploads'),$cgi->hidden('username',$username),$cgi->hidden('password',$password),$cgi->hidden('delete_file',$file),$cgi->submit('Delete'),$cgi->end_form)
          );
  }
  print $cgi->Tr($cgi->td("(no files uploaded)")) unless scalar(@files);
  print $cgi->end_table;

  print $cgi->br;

  print $cgi->h3("Add a file:");

  print $cgi->start_multipart_form( -action=> '/index.cgi/uploads' ),
        $cgi->hidden('username',$username),
        $cgi->hidden('password',$password),
        $cgi->filefield(-name=>'uploaded_file',-default=>'starting value',-size=>50,-maxlength=>80),
        $cgi->submit('Save'),
        $cgi->end_form;


### Default: List sites
} else {
  print $cgi->ul( map {$cgi->li($cgi->a({-href=>'http://'.$_.'/'},'http://'.$_.'/'))} list_sites() );
}

### Footer

print '
</div>
</div>
	</div>
	<div class="yui-b"><center>
      '.( $username ? "[ $username ]".$cgi->br.$cgi->br.$cgi->start_form(-action=>'/index.cgi/dashboard').$cgi->hidden('username',$username).$cgi->hidden('password',$password).$cgi->submit('Back to Dashboard').$cgi->end_form : '[ <a href="/index.cgi/login">LOGIN</a> ]').'
      <div id="side"><p>&nbsp;</p></div>
	</center></div>
	
	</div>
   <div id="ft" role="contentinfo">';

print $cgi->p('Path:',$cgi->path_info);
for my $param ( $cgi->param ) {
  #print $cgi->p($param,$cgi->param($param));
}

print '</div>
</div>

</body></html>';

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
  my $ref = $sth->fetchrow_arrayref;
  return $ref ? $ref->[0] : undef;
}

sub get_param {
  my $param = shift @_;
  my $value = undef;

  my $sth = $dbh->prepare('select value from params where username=? and param=?');
  my $ret = $sth->execute($username,$param);
  my $ref = $sth->fetchrow_arrayref;
  $value = $ref->[0] if $ref;

  unless ( $value ) { # Populate defaults if they aren't in the DB
    $value = ucfirst($username.' TV') if $param eq 'title';
    $value = 'Chat'                   if $param eq 'chat_title';
    $value = ucfirst($username)       if $param eq 'chat_channel';
    $value = 430                      if $param eq 'chat_height';
    $value = 'admin'                  if $param eq 'chat_admin_user';
    $value = 'Passw0rd1'              if $param eq 'chat_admin_pass';
    $value = 360                      if $param eq 'player_height';
    $value = 640                      if $param eq 'player_width';
    $value = $default_player_image    if $param eq 'player_url';
    $value = 'rtmp://tv.macrophile.com/oflaDemo/'.$username.'tv' if $param eq 'rtmp_url';
    set_param($username,$param,$value) if $value;
  }

  return $value;
}

sub get_site {
  my $sth = $dbh->prepare('select site from users where username=?');
  my $ret = $sth->execute(@_);
  return $sth->fetchrow_arrayref->[0];
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

sub send_message {
  my $number  = shift @_;
  my $message = shift @_;

  our $twilio;
  $twilio = WWW::Twilio::API->new(
                      AccountSid => $LocalAuth::TWILIO_SID,
                      AuthToken  => $LocalAuth::TWILIO_AUTH
                    ) unless defined $twilio;

  return $twilio->POST( 'SMS/Messages',
    From => $LocalAuth::TWILIO_PHONE,
    To => $number,
    Body => $message
  );
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

sub write_pages {
  my $path = get_directory($username);

  my $index_page     = $path .'/index.php';
  my $chat_page      = $path .'/chat.php';
  my $subscribe_page = $path .'/subscribe.cgi';

  my $priv_page      = $path .'/priv/index.php';
  my $priv_hta       = $path .'/priv/.htaccess';
  my $priv_htp       = $path .'/priv/htpasswd';

  print $cgi->p("Writing $index_page");

  my $tmpl = get_page($username,'index');

  my $template = HTML::Template->new( scalarref => \$tmpl, die_on_bad_params => 0 );
  $template->param('screen' => screen() );
  $template->param('chat' => '<?php $chat->printChat(); ?> [ <a href="#" onClick="window.open(\'/chat.php\', \'_blank\', \'height=600,width=450,toolbar=no,scrollbars=no,menubar=no\');document.getElementById(\'pfc_container\').innerHTML = \'&nbsp;\';">Pop Out Chat Window</a> ]' );

  $template->param('title' => get_param('title') );
  $template->param('uc_username' => ucfirst($username) );
  $template->param('username' => $username );

  open  INDEX, '>', $index_page or die "Can't open file: $index_page";
  print INDEX index_header();
  print INDEX $template->output;
  close INDEX;

  print $cgi->p("Writing $chat_page");

  unlink($chat_page) if -f $chat_page;

  open  CHAT, '>', $chat_page or die "Can't open file: $chat_page";
  print CHAT index_header();
  print CHAT '<html><body><?php $chat->printChat(); ?></body></html>';
  close CHAT;

  print $cgi->p("Writing $subscribe_page");
  unlink($subscribe_page) if -f $subscribe_page;

  $template = HTML::Template->new( filename => '/var/www/html/web-tv-core/templates/subscribe.cgi', die_on_bad_params => 0 );
  $template->param('title' => get_param('title') );
  $template->param('uc_username' => ucfirst($username) );
  $template->param('username' => $username );

  open  SUBSCRIBE, '>', $subscribe_page or die "Can't open file: $subscribe_page";
  print SUBSCRIBE $template->output;
  close SUBSCRIBE;

  `if [ ! -d $path/priv ]; then mkdir $path/priv; fi`;

  print $cgi->p("Writing $priv_hta");

  unlink($priv_hta) if -f $priv_hta;

  $template = HTML::Template->new( filename => '/var/www/html/web-tv-core/templates/htaccess', die_on_bad_params => 0 );
  $template->param('title' => ucfirst($username) .'\'s Private Stream Site' );
  $template->param('htpasswd' => $priv_htp );

  open  PRIV_HTA, '>', $priv_hta or die "Can't open file: $priv_hta";
  print PRIV_HTA $template->output;
  close PRIV_HTA;

  print $cgi->p("Writing $priv_htp");

  unlink($priv_htp) if -f $priv_htp;

  my $user = get_param('priv_user');
  my $pass = get_param('priv_pass');
  `htpasswd -bc $priv_htp $user $pass`;

  `if [ -d $path/jwplayer ]; then rm -rf $path/jwplayer; fi`;
  `cp -r /var/www/html/web-tv-core/resources/jwplayer $path`;

  `if [ -d $path/chat ]; then rm -rf $path/chat; fi`;
  `cp -r /var/www/html/web-tv-core/resources/chat $path`;

  `if [ ! -d $path/uploads ]; then mkdir $path/uploads; fi`;

  `chmod 0755 $index_page $subscribe_page`;
}

### Big page blocks

sub index_header {
  my $title           = get_param('title');
  my $chat_title      = get_param('chat_title');
  my $chat_channel    = get_param('chat_channel');
  my $chat_height     = get_param('chat_height');
  my $chat_admin_user = get_param('chat_admin_user');
  my $chat_admin_pass = get_param('chat_admin_pass');

  return '<?php

require_once dirname(__FILE__)."/chat/src/phpfreechat.class.php";

$params = array();

#$params["serverid"] = md5(__FILE__); // calculate a unique id for this chat
$params["serverid"] = "53d2a6a5a253c626d21ca125ab6e81fd";

$params["title"] = "'.$chat_title.'"; // Chat title
$params["channels"] = array("'.$chat_channel.'"); // Default channel to join
$params["frozen_channels"] = array("'.$chat_channel.'"); // Only one channel allowed

$params["theme"] = "wolf"; // Custom style
$params["height"] = "'.$chat_height.'px"; // Height. No width setting sadly
$params["displaytabclosebutton"] = false; // Get rid of the tab, wish this worked
$params["displaytabimage"] = false; // Get rid of the tab, wish this worked
$params["display_pfc_logo"] = false; // Remove the logo for phofreechat.net

$params["admins"] = array( "OtherAdmin" => "nopassword", "'.$chat_admin_user.'" => "'.$chat_admin_pass.'" ); // Admin info
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
  my $playerid = 'player_'.$username;

  my $player_height = get_param('player_height');
  my $player_width  = get_param('player_width');
  my $player_url    = get_param('player_url');
  my $rtmp_url      = get_param('rtmp_url');

  # Return the screen layout
  return '<script type=\'text/javascript\' src=\'/jwplayer/jwplayer.js\'></script>
<div id="'.$playerid.'">
  <h1>You need the Adobe Flash Player for this demo, download it by clicking the image below.</h1>
  <p><a href="http://www.adobe.com/go/getflashplayer"><img src="http://www.adobe.com/images/shared/download_buttons/get_flash_player.gif" alt="Get Adobe Flash player" /></a></p>
</div>
<script type=\'text/javascript\'>
  jwplayer("'.$playerid.'").setup({
    file: "'.$rtmp_url.'",
    width: "'.$player_width.'",
    height: "'.$player_height.'",
    primary: "flash",
    image: "'.$player_url.'",
    autostart: "true",
  });

  var timer=10000;
  jwplayer().onIdle(function() {
  	t=setTimeout("jwplayer().play()",10000);
  });

</script>

[ <a href="#" onClick="
  document.getElementById(\''.$playerid.'\').innerHTML = \'&nbsp;\';
  jwplayer(\''.$playerid.'\').setup({
    file: \''.$rtmp_url.'\',
    width: \''.$player_width.'\',
    height: \''.$player_height.'\',
    primary: \'flash\',
    image: \''.$player_url.'\',
    autostart: \'true\',
  });

  var timer=10000;
  jwplayer().onIdle(function() {
  	t=setTimeout(\'jwplayer().play()\',10000);
  });">'.$player_width.'x'.$player_height.'</a> |

<a href="#" onClick="
  document.getElementById(\''.$playerid.'\').innerHTML = \'&nbsp;\';
  jwplayer(\''.$playerid.'\').setup({
    file: \''.$rtmp_url.'\',
    width: \'800\',
    height: \'600\',
    primary: \'flash\',
    image: \''.$player_url.'\',
    autostart: \'true\',
  });

  var timer=10000;
  jwplayer().onIdle(function() {
  	t=setTimeout(\'jwplayer().play()\',10000);
  });">800x600</a> |

<a href="#" onClick="
  document.getElementById(\''.$playerid.'\').innerHTML = \'&nbsp;\';
  jwplayer(\''.$playerid.'\').setup({
    file: \''.$rtmp_url.'\',
    width: \'1024\',
    height: \'768\',
    primary: \'flash\',
    image: \''.$player_url.'\',
    autostart: \'true\',
  });

  var timer=10000;
  jwplayer().onIdle(function() {
  	t=setTimeout(\'jwplayer().play()\',10000);
  });">1024x768</a> ]

';
}
