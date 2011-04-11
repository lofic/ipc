install
url --url http://10.0.1.248/distrib/fedora14-dvd-x86_64
repo --name="Fedora14"  --baseurl=http://10.0.1.248/distrib/fedora14-dvd-x86_64 --cost=100

lang fr_FR.UTF-8
keyboard fr-latin9

skipx

network --device eth0 --bootproto dhcp --noipv6 --hostname localhost

#rootpw  --iscrypted $6$TYw.D/ICpcRGirSG$16CanyeVrfMQMZr2BWHXt24JOdELxrnQvTMMqVDLyRojzNE5QIc6mGjq/rZrPiuRgivljNFg6FGbgUrFX0O/A1
rootpw  --iscrypted $6$jEeq2Jyj$tZprcQ6YAJoxZjfLKVDunoyxvg9TzuZyJwhcRDrGVC60BaspheAR9FRgVbVCDGnF1a5kwaCRBiYfNG0SL1U64/ 
firewall --service=ssh
authconfig --enableshadow --passalgo=sha512 --enablefingerprint

selinux --permissive
#selinux --enforcing

timezone --utc Europe/Paris
bootloader --location=mbr --driveorder=sda --append="crashkernel=auto rhgb quiet"

# Automatic reboot at the end of the installation
reboot

# The following is the partition information you requested
zerombr
clearpart --linux --drives=sda

#volgroup VolGroup --pesize=4096 pv.vXVB8D-NSX6-fkPk-4kgY-Ifaj-QzF4-rtkB20
#logvol / --fstype=ext4 --name=lv_root --vgname=VolGroup --grow --size=1024 --maxsize=51200
#logvol swap --name=lv_swap --vgname=VolGroup --grow --size=496 --maxsize=992
#part /boot --fstype=ext4 --size=500
#part pv.vXVB8D-NSX6-fkPk-4kgY-Ifaj-QzF4-rtkB20 --grow --size=1

part / --fstype ext4 --size=1000 --grow
part swap --size=128


%packages --nobase
@core
# Les choix de packages ci-dessous sont optionnels
%end

# Taches de post installation
%post
#--nochroot 

/sbin/chkconfig smartd off
echo "RUN_FIRSTBOOT=NO" > /etc/sysconfig/firstboot
cp -p /boot/grub/grub.conf /boot/grub/grub.conf.DIST

initfile=/etc/inittab

cp -f $xconf $xconf.ori 
cp -f $initfile $initfile.ori 

sed -i 's/^id:5:/id:3:/g' $initfile

/usr/sbin/adduser bob
/usr/sbin/usermod -p CXl5ww5.VOOy6 bob

ed /boot/grub/grub.conf <<EOF
g!hiddenmenu!s!!#hiddenmenu!gp
g! rhgb quiet!s!!!gp
g! quiet!s!!!g
wq
EOF

/sbin/chkconfig network on
%end
