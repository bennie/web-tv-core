#!/usr/bin/perl

use CGI;
use strict;

my $cgi = new CGI;

print $cgi->header, $cgi->start_html('TV Sites');
print '<body bgcolor="#FFFFFF">';

if ( $cgi->path_info eq '/login' ) {
  print $cgi->start_form, $cgi->textfield('username'),
        $cgi->password_field('password'), $cgi->submit, $cgi->end_form;

} else {
  print '[ <a href="/index.cgi/login">Admin</a> ]

<ul>
<li> <a href="http://noben.tv.furfolk.com/">http://noben.tv.furfolk.com/</a>
<li> <a href="http://wolf.tv.macrophile.com/">http://wolf.tv.macrophile.com/</a>
</ul>';
}

print "Path: ", $cgi->path_info;
for my $param ( $cgi->param ) {
  print $cgi->p($param,$cgi->param($param));
}
print '</body></html>';
