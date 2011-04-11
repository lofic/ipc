# Kickstart Install with Xfree and Gnome 
install
url --url http://10.0.1.248/distrib/centos55-dvd

lang en_US.UTF-8
langsupport --default en_US.UTF-8 en_US.UTF-8 fr_FR.UTF-8
keyboard fr-latin1

mouse
#xconfig --card "vesa" --resolution 1024x768 --depth 24 --startxonboot --defaultdesktop gnome
skipx

network --device eth0 --bootproto dhcp --hostname localhost

rootpw --iscrypted $1$eTKikdTT$uuIDFroxC4SFsG2NbmgD.. 

#firewall --enabled --port=http:tcp --port=ssh:tcp
firewall --disabled

#selinux --enforcing
selinux --disabled
#selinux --permissive

authconfig --enableshadow --enablemd5

timezone --utc Europe/Paris

#bootloader --location=mbr
bootloader --location=mbr --md5pass=$1$o6DEC6qI$ZbQTrca3hFWv1g5dbab6J0

# Automatic reboot at the end of the installation
reboot

# Erase bad signatures disk
zerombr yes

# Partitionnement
clearpart --all
part / --fstype ext3 --size=1000 
part swap --size=128 
part /usr --fstype ext3 --size=3000 
part /var --fstype ext3 --size=2000 
part /tmp --fstype ext3 --size=1000
part /home --fstype ext3 --size=5000
#part /home --fstype ext3 --size=2 --grow 

# Paquetages pour le systeme
%packages
@ text-internet
@ gnome-desktop
@ dialup
@ base-x
@ graphical-internet
kernel
grub
e2fsprogs

# Taches de post installation
%post 
#--nochroot

/sbin/chkconfig smartd off
echo "RUN_FIRSTBOOT=NO" > /etc/sysconfig/firstboot
cp -p /boot/grub/grub.conf /boot/grub/grub.conf.DIST

xconf=/etc/X11/xorg.conf
initfile=/etc/inittab

echo 'Louis was here' > /etc/test

cp -f $xconf $xconf.ori
cp -f $initfile $initfile.ori

sed -i 's/^id:5:/id:3:/g' $initfile

cat<<EOF>>/etc/rc.local
/bin/sed -i 's/\"us\"/\"fr\"/g' /etc/X11/xorg.conf 
EOF

#/bin/sed -i 's/vesa/i810/g' $xconf
#/bin/sed 's/800x600/1280x1024/g' $xconf
#/bin/sed 's/^.*HorizSync.*$/HorizSync 31.5 - 67/g' $xconf
#/bin/sed 's/^.*VertRefresh.*$/VertRefresh 50 - 75/g' $xconf

/usr/sbin/adduser bob
/usr/sbin/usermod -p CXl5ww5.VOOy6 bob

ed /boot/grub/grub.conf <<EOF
g!hiddenmenu!s!!#hiddenmenu!gp
g! rhgb quiet!s!!!gp
g! quiet!s!!!g
wq
EOF

