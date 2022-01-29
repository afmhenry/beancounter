bean-query -f=csv ../beans/alex.beancount "SELECT month, account, sum(position) group by month, parent(account), account"
