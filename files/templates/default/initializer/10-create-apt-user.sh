#!/bin/bash
if ! id "_apt" > /dev/null 2>&1; then
	useradd -r -M --system _apt
fi
