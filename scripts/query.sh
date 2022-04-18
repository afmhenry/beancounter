bean-query -f=csv ../beans/alex.beancount "select sum(position) where account ~'.*Assets.*' and (year=2022 or year=2021)"
