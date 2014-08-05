# 2014.05.08 15:17:51 EDT
from openerp.osv import osv, fields
import urllib as u
import string
from datetime import date
from datetime import datetime

class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'

    """
    def _check_stock(self, cr, uid, ids, context=None):

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
                                raise osv.except_osv('Error','No hay stock disponible para el producto '+line.product_id.name)
				return False

	return True
    """

    def _check_validation(self, cr, uid, ids, context = None):
        obj = self.browse(cr, uid, ids[0], context=context)
        config_adddisc = 0
        config_credit_tolerance = 0
        config_disc_level1 = 0
        config_disc_level2 = 0
        config_disc_level3 = 0
        config_grupo_aprob1 = ''
        config_grupo_aprob2 = ''
        config_grupo_aprob3 = ''
        config_ids = self.pool.get('ir.config_parameter').search(cr, uid, [('key', 'like', 'SBA')])
        if config_ids:
            for config in self.pool.get('ir.config_parameter').browse(cr, uid, config_ids):
                if config.key == 'SBA_DESCUENTO_NIVEL1':
                    config_disc_level1 = float(config.value)
                if config.key == 'SBA_DESCUENTO_NIVEL2':
                    config_disc_level2 = float(config.value)
                if config.key == 'SBA_DESCUENTO_NIVEL3':
                    config_disc_level3 = float(config.value)
                if config.key == 'SBA_GRUPO_APROB_1':
                    config_grupo_aprob1 = config.value
                if config.key == 'SBA_GRUPO_APROB_2':
                    config_grupo_aprob2 = config.value
                if config.key == 'SBA_GRUPO_APROB_3':
                    config_grupo_aprob3 = config.value
                if config.key == 'SBA_GRUPO_VENTAS':
                    config_grupo_ventas = config.value
                if config.key == 'SBA_TOLERANCIA_CREDITO1':
                    config_credit_tolerance1 = float(config.value)
                if config.key == 'SBA_TOLERANCIA_CREDITO2':
                    config_credit_tolerance2 = float(config.value)
                if config.key == 'SBA_TOLERANCIA_CREDITO3':
                    config_credit_tolerance3 = float(config.value)

        user_groups = {}
        group_ventas_id = self.pool.get('res.groups').search(cr, uid, [('name', '=', config_grupo_ventas)])
        group_aprob1_id = self.pool.get('res.groups').search(cr, uid, [('name', '=', config_grupo_aprob1)])
        group_aprob2_id = self.pool.get('res.groups').search(cr, uid, [('name', '=', config_grupo_aprob2)])
        group_aprob3_id = self.pool.get('res.groups').search(cr, uid, [('name', '=', config_grupo_aprob3)])
        user_groups['grupo_ventas'] = group_ventas_id
        user_groups['group_aprob1'] = group_aprob1_id
        user_groups['group_aprob2'] = group_aprob2_id
        user_groups['group_aprob3'] = group_aprob3_id
        user_list_aprob1 = self.pool.get('res.groups').read(cr, uid, group_aprob1_id, ['users'])
        user_list_aprob2 = self.pool.get('res.groups').read(cr, uid, group_aprob2_id, ['users'])
        user_list_aprob3 = self.pool.get('res.groups').read(cr, uid, group_aprob3_id, ['users'])
        return_value = True
        if obj.state == 'manual' or obj.state == 'sent':
            if obj.add_disc < config_disc_level1:
                return_value = True
            elif obj.add_disc >= config_disc_level1 and obj.add_disc < config_disc_level2:
                return_flag_level1 = False
                return_flag_level2 = False
                for user_group in user_list_aprob1:
                    if uid in user_group['users']:
                        return_flag_level1 = True

                for user_group in user_list_aprob2:
                    if uid in user_group['users']:
                        return_flag_level2 = True

                return_value = return_flag_level1 or return_flag_level2
            elif obj.add_disc > config_disc_level2:
                return_flag_level2 = False
                for user_group in user_list_aprob2:
                    if uid in user_group['users']:
                        return_flag_level2 = True

                return_value = return_flag_level2
            if not return_value:
                return False
            if obj.partner_id.credit == 0:
                return True
            total_check_1 = obj.partner_id.credit_limit * (1 + config_credit_tolerance1 / 100) - (obj.amount_total + obj.partner_id.credit)
            total_check_2 = obj.partner_id.credit_limit * (1 + config_credit_tolerance2 / 100) - (obj.amount_total + obj.partner_id.credit)
            total_check_3 = obj.partner_id.credit_limit * (1 + config_credit_tolerance3 / 100) - (obj.amount_total + obj.partner_id.credit)
            if total_check_1 < 0 and total_check_2 > 0:
                return_flag_level1 = False
                return_flag_level2 = False
                for user_group in user_list_aprob1:
                    if uid in user_group['users']:
                        return_flag_level1 = True

                for user_group in user_list_aprob2:
                    if uid in user_group['users']:
                        return_flag_level2 = True

                return_value = return_flag_level1 or return_flag_level2
                if not return_value:
                    raise osv.except_osv('Error', 'El cliente supera su limite de credito por ' + str(total_check_1 * -1) + '$')
                    return False
                else:
                    return True
            if total_check_2 < 0 and total_check_3 > 0:
                return_flag_level1 = False
                return_flag_level2 = False
                for user_group in user_list_aprob2:
                    if uid in user_group['users']:
                        return_flag_level1 = True

                for user_group in user_list_aprob3:
                    if uid in user_group['users']:
                        return_flag_level2 = True

                return_value = return_flag_level1 or return_flag_level2
                if not return_value:
                    raise osv.except_osv('Error', 'El cliente supera su limite de credito por ' + str(total_check_1 * -1) + '$')
                    return False
                else:
                    return True
            if total_check_3 < 0:
                return_flag_level = False
                for user_group in user_list_aprob3:
                    if uid in user_group['users']:
                        return_flag_level = True

                if not return_flag_level:
                    raise osv.except_osv('Error', 'El cliente supera su limite de credito por ' + str(total_check_3 * -1) + '$')
                    return False
                else:
                    return True
        return True


    _constraints = [(_check_validation, '\n\nAcaba de otorgar un descuento superior al descuento que se le permite otorgar.\nPor favor, pida a su superior que autorice el pedido', ['add_disc']),
		    ]

sale_order()

# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2014.05.08 15:17:51 EDT
