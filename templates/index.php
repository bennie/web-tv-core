<?php

require_once dirname(__FILE__)."/chat/src/phpfreechat.class.php";

$params = array();

$params["serverid"] = md5(__FILE__); // calculate a unique id for this chat

$params["title"] = "Wolf's Chat"; // Chat title
$params["channels"] = array("wolfchat"); // Default channel to join
$params["frozen_channels"] = array( "wolfchat" ); // Only one channel allowed

$params["theme"] = "wolf"; // Custom style
$params["height"] = "430px"; // Height. No width setting sadly
$params["displaytabclosebutton"] = false; // Get rid of the tab, wish this worked
$params["displaytabimage"] = false; // Get rid of the tab, wish this worked
$params["display_pfc_logo"] = false; // Remove the logo for phofreechat.net

$params["admins"] = array( 'OtherAdmin' => 'nopassword', 'Wolf' => 'nopassword' ); // Admin info
$params["nick"] = ""; // Force people to chose a nickname

$params["shownotice"] = 5; // Show kicks and renicks
$params["showsmileys"] = false; // Hide the smiley box at first
$params["showwhosonline"] = false; // hide the user box at first

$params['skip_proxies'] = array('censor'); // We don't mind naughty words.

$params['nickname_colorlist'] = array(
  '#000000', '#3636B2', '#2A8C2A', '#C33B3B', '#C73232',
  '#80267F', '#66361F', '#D9A641', '#3DCC3D', '#1A5555',
  '#2F8C74', '#4545E6', '#B037B0'
);

$chat = new phpFreeChat($params);

?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en"><head>
  <title>Wolf TV - Art and Chat with Wolf Kidd</title>
<head><body bgcolor="#666699"><center>
<table width=1040>
<tr><td colspan=5 align=center><img src="logo.jpg" /></td></tr>
<tr><td colspan=5 align=center><b>If you cannot see the video, turn off all ad-blockers and refresh the screen.<br>If you see the error message "Error loading stream: ID not found on server", that means the stream is not running currently.</b></td></tr>
<tr valign="center"><td width=640 colspan=4>

<script type='text/javascript' src='/jwplayer/jwplayer.js'></script>
<div id='player_8040'>
  <h1>You need the Adobe Flash Player for this demo, download it by clicking the image below.</h1>
  <p><a href="http://www.adobe.com/go/getflashplayer"><img src="http://www.adobe.com/images/shared/download_buttons/get_flash_player.gif" alt="Get Adobe Flash player" /></a></p>
</div>
<script type='text/javascript'>
  jwplayer('player_8040').setup({
    file: "rtmp://wolf.tv.macrophile.com/oflaDemo/wolftv",
    width: "640",
    height: "360",
    primary: "flash",
    image: "http://wolf.tv.macrophile.com/player.jpg",
    autostart: "true",
  });

  var timer=10000;
  jwplayer().onIdle(function() {
  	t=setTimeout("jwplayer().play()",10000);
  });

</script>

</td><td width=400 rowspan=2>

  <?php $chat->printChat(); ?>

</td></tr>
<tr valign=center>
<td align=center><a href="https://twitter.com/wolf_kidd" class="twitter-follow-button" data-show-count="false" data-size="large">Follow @wolf_kidd</a>
<script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src="//platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script></td>
<td><a href="https://twitter.com/share" class="twitter-share-button" data-url="http://wolf.tv.macrophile.com/" data-text="Join me watching Wolf Kidd stream!" data-via="wolf_kidd" data-size="large" data-count="none">Tweet</a>
<script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src="//platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");</script></td>
<td align=center><a href="http://www.macrophile.com/"><img src="http://www.macrophile.com/images/linkbutton.gif" border=0 /></a></td><td align=center><form action="https://www.paypal.com/cgi-bin/webscr" method="post">

<input type="hidden" name="cmd" value="_s-xclick">

<input type="hidden" name="hosted_button_id" value="KF475Y4QN9P3E">

<input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_buynowCC_LG.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">

<img alt="" border="0" src="https://www.paypalobjects.com/en_US/i/scr/pixel.gif" width="1" height="1">

</form></td]
<td align=center>&nbsp;</td>
<td align=center>&nbsp;</td>
<td align=center>&nbsp;</td>
</tr>
</table></center>
<center>
<table width=1040>
<tr>
<td>
<b>FAQ/Rules</b><br>
1) The napkin/paper-towel is to keep the pencil from smudging.<br>
2) Ask before posting links - If you don't ask, you will be warned. If you don't heed the warning, you will be banned.<br>
3) Certain subjects are inappropriate for the chat: Religion, Operating Systems (religion), Politics (religion), and cel-phones (religion).<br>
4) Keep role-play mild/light - I actually find it amusing/entertaining, please try and keep it to that.<br>
5) Do not spam the chat - if you feel the need to have an involved discussion with someone, please take it elsewhere.<br>
6) I am easy to annoy, but hard to push - if I warn you, I'm serious; the second warning-shot will probably be center-of-mass (ban).<br>
</td>
</tr>
</table></center>
</body></html>
