#!/bin/sh
while [ $# -gt 1 ]
do
key="$1"
case $key in
    --theme)
    THEME_ZIP="$2"
    shift # past argument
    ;;
    *)
    # unknown option
    ;;
esac
shift # past argument or value
done

pwd
ls -l
echo "theme path is $THEME_ZIP"

apt-get update && apt-get install zip -y
echo "install unzip.."

unzip $THEME_ZIP -d wp-content/themes
echo "extract theme.."

sed -i -e 's/\(define( '\''WP_DEFAULT_THEME'\'', \).*\();\)/\1 '\''agama'\'' \2/g' wp-includes/default-constants.php
echo "set as default theme.."
