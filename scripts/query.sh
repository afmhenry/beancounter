bean-query -f=csv ../beans/alex.beancount "select sum(position) as total, date where account ~'.*Expense.*' and not account ~'.*Tax.*' and (month=12 or month=11 or month=10) group by date"
