bean-query -f=csv ../beans/alex.beancount '
SELECT account, sum(position) as total, year
WHERE account ~ "Income" and not account ~".*Unrealized" and year=2021
GROUP BY account, year
ORDER BY account DESC;
'