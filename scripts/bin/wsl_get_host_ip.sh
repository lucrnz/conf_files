#!/bin/sh
case "$(uname -r)" in
  *"WSL2"*) ip route show | grep -i default | awk '{ print $3}' ;;
  *) echo "Not running in WSL" ;;
esac

