#!/usr/bin/env zsh

echo "Hello"

aps=(172.16.1.11 172.16.1.12 172.16.1.13)

for ap in "$aps[@]"; do
	echo $ap
	scp -i .ssh/keyberos-openssh netadmin@"$ap":running-config "$ap-running-config-$(date '+%Y%m%d_%H%M%S')"
done
