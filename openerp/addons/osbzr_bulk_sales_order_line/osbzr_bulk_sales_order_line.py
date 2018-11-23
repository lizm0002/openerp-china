# -*- coding: utf-8-*- 

from openerp.osv import osv,fields

class osbzr_bulk_sales_order_line(osv.osv_memory):
    _name = 'osbzr.bulk.sales.order.line'
    _columns = {
        'product_ids':fields.many2many('product.product',string=u'需新增的产品'),
        'quantity':fields.integer(u'每行数量'),
                }
    def add_lines(self,cr,uid,ids,context=None):
        obj_line = self.pool.get('sale.order.line')
        order = self.pool.get('sale.order').browse(cr, uid, context.get('active_ids', False))[0]
        bulk = self.browse(cr,uid,ids[0],context)
        for product in bulk.product_ids:
            new_line = {
                    'order_id':order.id,
                    'name':product.name,
                    'product_id':product.id,
                    'product_uom_qty':bulk.quantity,
                    'product_uom':product.uom_id.id,
                 }
            vals = obj_line.product_id_change(cr, uid, ids,order.pricelist_id.id, product.id, bulk.quantity, product.uom_id.id, 
                                bulk.quantity, product.uom_id.id, False, order.partner_id.id, 
                                False, True, order.date_order, False, order.fiscal_position.id, False, context)
            new_line = dict(vals['value'],**new_line)   # 合并两个dict
            obj_line.create(cr,uid,new_line,context=context)
        return {'type': 'ir.actions.act_window_close'}