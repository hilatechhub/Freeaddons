=====================================================
POS Stock Restriction - Block Out-of-Stock Sales
=====================================================

Odoo 19 Community - module ``hilatech_restrick_salespos``

Prevents the Point of Sale from selling storable products that are out of
stock, or a quantity greater than the real quantity on hand in the stock
location of the Point of Sale. A popup informs the cashier each time.

Features
========
* Adding an out-of-stock product is blocked (product click, barcode scan).
* The quantity of a line can never exceed the available stock (numpad,
  quantity popup, repeated clicks).
* Final check of the whole order when clicking *Payment* and when validating
  the payment.
* Stock read live from the server, in the source location of the PoS
  operation type, minus quantities sold in open sessions whose stock moves
  are not done yet, minus quantities in the open orders of the terminal.
* Only storable products are controlled. Decreasing, removing lines and
  refunds are always allowed.
* One option per Point of Sale (enabled by default).
* English and French.

Configuration
=============
Point of Sale > Configuration > Settings > Inventory > *Block Out-of-Stock Sales*.

Limitations
===========
* Offline: the last known stock is used; products with unknown stock are not blocked.
* Unpaid orders opened on other terminals are not counted (checked again at payment).

Credits
=======
Author: HILATECH SARL (Douala, Cameroon). License: LGPL-3.

Support: support@hilatech.co - Tel: +237 698 86 86 00
