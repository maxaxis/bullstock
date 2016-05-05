# Database Structure #

```

  +-------------------+                              +-----------------+
  | Transactions      |                              | FinancialInfo   |
  +-------------------+                              +-----------------+
  | id                |                              | id              |
  | (FK) symbol_id    |                              | (FK) company_id |
  | (FK) portfolio_id |N                             | timestamp       |
  | type              |------------------+           | description     |
  | amount            |                  |           | data            |
  | value             |                  |           | type            |
  | trade_cost        |                  |           +-----------------+
  +-------------------+                  |                   |N
            |N                           |                   |
            |                            |                   |
            |1                           |1                  |1
+-----------------------+     +-------------------+     +---------+
| Portfolio             |     | Symbol            |     | Company |
+-----------------------+N   N+-------------------+N   1+---------+
| id                    |-----| id                |-----| id      |              
| name                  |     | (FK) company_id   |     | name    |
| transaction_costs     |     | (FK) portfolio_id |     +---------+
+-----------------------+     | name              |
                              | description       |
                              | datasource        |
                              +-------------------+
                                       1|
                                        |
                                       N|
                                +----------------+
                                | History        |
                                +----------------+
                                | id             |
                                | (FK) symbol_id |
                                | timestamp      |
                                | open           |
                                | close          | 
                                | high           |
                                | low            |
                                | close          |
                                | volume         |
                                | type           |
                                +----------------+

```

## Dictionary ##

  * Transactions
    * type - char - 'B': buy, 'S': sell
    * amount - int - Amount of symbol
    * value - real - symbol value
    * trade\_cost - real - cost of the trade
  * History
    * timestamp - datetime - Timestamp
    * open - real - Open value (price)
    * close - real - Close value (price)
    * high - real - Highest value (price)
    * low - real - Lowest value (price)
    * volume - int - Volume
    * type - char - 'q': quote, 'd': dividend
  * FinancialInfo (for fundamentalist analysis)
    * timestamp - datetime - Timestamp
    * description - str - Information description
    * data - str - the value of information
    * type - char - type of information 'r': real, 's': str, 'd': date, 't': time, ...