#!/bin/bash
if ! [ $(getent group crontab) ]; then
	groupadd crontab
fi
