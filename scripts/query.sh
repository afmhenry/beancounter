bean-query -f=csv ../beans/alex.beancount "SELECT account, month, year, sum(position) as total where account ~ 'Expenses' group by month, year, account "
