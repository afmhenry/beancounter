bean-query -f=csv beans/alex.beancount "select account where not account ~'.*Unrealized.*' and not account ~'.*Equity.*' and not account ~'.*Assets.*' and not account ~'.*Pnl.*' and not account ~'.*Tax.*' group by account"
