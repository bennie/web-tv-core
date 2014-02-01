#!/usr/bin/perl

use CGI;
use Data::Dumper;
use DB_File;
use WWW::Twilio::API;
use strict;

my $cgi = new CGI;
my $twilio;

tie my %db, 'DB_File', 'subscribers.db'
  or die "Cannot create DB file: $!\n";

if ( $cgi->param('message') ) {
  my $message = $cgi->param('message');
  print $cgi->header, 
        $cgi->start_html('Admin'), 
        $cgi->blockquote($message),
        $cgi->p("Sending messages...");

  for my $number ( keys %db ) {
    my $ret = &send_message($number,$cgi->param('message'));
    print $cgi->p($number,'...',$ret->{message},'('.$ret->{code}.')');
  }
        
  print $cgi->end_html;
} else {
  print $cgi->header, 
        $cgi->start_html('Admin'),
        $cgi->start_form(),
        $cgi->textarea(
          -name => 'message', -rows => 5, -columns=> 50,
          -default => "http://wolf.tv.macrophile.com/ - Wolf TV is now Online!"
        ),
        $cgi->br,
        $cgi->submit,
        $cgi->end_form; 

    print $cgi->p('The current list:');        
	for my $number ( keys %db ) {
	  print $number, "\t", $db{$number}, $cgi->br, "\n";
    }        
    print $cgi->end_html;
}

### Subroutines

sub send_message {
  my $number  = shift @_;
  my $message = shift @_;

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
