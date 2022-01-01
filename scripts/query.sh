bean-query ../beans/alex.beancount '
select
  account, sum(cost(position)) as total
where
  account ~ "Expenses.*" and not account ~".*Tax.*"  and year=2021
group by account
order by total DESC'

bean-query ../beans/alex.beancount '
select
  sum(cost(position)) as total, month, year
where
  account ~ "Expenses:Consumption.*" and not account ~".*Tax.*"  and year=2021
group by year, month
order by year, month DESC'

bean-query ../beans/alex.beancount '
select
  sum(cost(position)) as total, month, year
where
  account ~ "Expenses:Consumption.*" and not account ~".*Tax.*"  and year=2021
group by
  month, year
order by
  year, month DESC'