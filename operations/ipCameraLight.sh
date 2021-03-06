#!/bin/bash
source ~/super-secret-password-file

die () {
    echo >&2 "$@"
    exit 1
}

[ "$#" -eq 1 ] || die "USAGE: ipCameraLight.sh <cmd> where cmd = ON or OFF"

if [ $1 == 'ON' ]
then
  echo 'Switching ON IR Lamps'
  curl 'http://192.168.1.222/decoder_control.cgi?command=95' -u $INDOOR_FOSCAM_USERNAME:$INDOOR_FOSCAM_PASSWORD > /dev/null 2>&1 || true
  curl "http://192.168.1.221:88/cgi-bin/CGIProxy.fcgi?cmd=setInfraLedConfig&mode=0&usr=$OUTDOOR_FOSCAM_USERNAME&pwd=$OUTDOOR_FOSCAM_PASSWORD" || true
fi

if [ $1 == 'OFF' ]
then
  echo 'Switching OFF IR Lamps'
  curl 'http://192.168.1.222/decoder_control.cgi?command=94' -u $INDOOR_FOSCAM_USERNAME:$INDOOR_FOSCAM_PASSWORD || true
  curl "http://192.168.1.221:88/cgi-bin/CGIProxy.fcgi?cmd=setInfraLedConfig&mode=1&usr=$OUTDOOR_FOSCAM_USERNAME&pwd=$OUTDOOR_FOSCAM_PASSWORD" || true
  curl "http://192.168.1.221:88/cgi-bin/CGIProxy.fcgi?cmd=closeInfraLed&usr=$OUTDOOR_FOSCAM_USERNAME&pwd=$OUTDOOR_FOSCAM_PASSWORD" || true
fi
