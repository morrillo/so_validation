from openerp.osv import osv,fields
from datetime import date
from datetime import datetime
import string

class sale_stockout(osv.osv):
	_name = "sale.stockout"
	_description = "Modelo con los productos que tuvieron stockout durante la confirmacion del pedido"

	_columns = {
		'date': fields.date('Fecha'),
		'product_id': fields.many2one('product.product','Producto'),
		'sale_id': fields.many2one('sale.order','Pedido'),
		'qty': fields.integer('Cantidad'),
		}

sale_stockout()

"""
class sale_order(osv.osv):
	_name = "sale.order"
	_inherit = "sale.order"

        def _check_stock(self, cr, uid, ids, context=None):
        # def write(self, cr, uid, ids, vals, context=None):

            obj = self.browse(cr, uid, ids[0], context=context)
	    sale_stockout_obj = self.pool.get('sale.stockout')
	    if obj.state == 'manual' or obj.state == 'sent':
		for line in obj.order_line:
			if line.product_id.qty_available < line.product_uom_qty :
				stock_out_id = sale_stockout_obj.search(cr,uid,[('sale_id','=',obj.id),('product_id','=',line.product_id.id)])
				if not stock_out_id:
					vals_stock_out = {
						'date': str(date.today()),
						'product_id': line.product_id.id,
						'sale_id': obj.id,
						'qty': line.product_uom_qty,
						}
					cr.execute("begin")
					cr.execute("insert into sale_stockout(date,product_id,sale_id,qty) values ('%s',%i,%i,%i)" \
						%(str(date.today()),line.product_id.id,obj.id,line.product_uom_qty))
					cr.execute("commit")
					# return_id = sale_stockout_obj.create(cr,uid,vals_stock_out)
                                # raise osv.except_osv('Error','No hay stock disponible para el producto '+line.product_id.name)
				return False

	    # return super(sale_order, self).write(cr, uid, ids, vals, context=context)
	    return True


        _constraints = [
		(_check_stock, 'No hay stock disponible',['state'])
		]

sale_order()

"""
