#!/usr/bin/perl
print "Waiting for screensaver"."\n";
my $blanked = 0;
open (IN, "xscreensaver-command -watch |");
while (<IN>) {
	if (m/^(BLANK|LOCK)/){
		if (!$blanked) {
			system("python3", "/home/pi/wateringsys/backlight.py", "off") == 0 or die "Python script returned error $?";
			$blanked = 1;
		}
	} elsif (m/^UNBLANK/) {
		 system("python3", "/home/pi/wateringsys/backlight.py", "on") == 0 or die "Python script returned error $?";
		$blanked = 0;
	}
}
