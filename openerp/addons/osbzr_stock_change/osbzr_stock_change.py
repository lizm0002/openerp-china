# -*- coding: utf-8-*- 

from openerp import models
from openerp.osv import osv, fields

class stock_change(osv.osv):
    _name = "stock.change"
    _description = u"形态转换单"
    _order = "create_date DESC"

    _columns = {
        'name': fields.char(u'转换单号', select=True, states={'done': [('readonly', True)]}, copy=False),
        'change_date': fields.datetime(u'换货日期', help=u'转换完成的日期', readonly=True, states={'draft': [('readonly', False)]}),
        'move_in_lines': fields.one2many('stock.move', 'change_id', u'入库移动', required=True, readonly=True, states={'draft': [('readonly', False)]}, copy=True),
        'move_out_lines': fields.one2many('stock.move', 'raw_material_change_id', u'出库移动', required=True, readonly=True, states={'draft': [('readonly', False)]}, copy=True),
        'partner_id': fields.many2one('res.partner', u'业务伙伴', domain="[('is_company', '=', True)]", readonly=True, states={'draft': [('readonly', False)]}),
        'location_id': fields.many2one('stock.location', required=True, string=u'库存库位', readonly=True, states={'draft': [('readonly', False)]}),
        'location_dest_id': fields.many2one('stock.location', required=True, string=u'对方库位', readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', u'草稿'),
            ('submit', u'待审批'),
            ('done', u'完成'),
            ], u'状态', readonly=True, copy=False, help=u'形态转换单的状态',select=True),
        'out_amt': fields.float(u'出库计划成本', readonly=True, copy=False),
        'in_amt': fields.float(u'入库计划成本', readonly=True, copy=False),
        'account_move_id': fields.many2one('account.move', u'会计凭证'),
        'amount':fields.float(u'换货金额合计'),
    }
    _defaults = {
        'name': lambda obj, cr, uid, context: '/',
        'state': 'draft',
        'change_date': lambda cr,uid,ids,context: fields.datetime.now(),
        'location_id': lambda self,cr,uid,context: self.pool.get('ir.model.data').xmlid_to_res_id(cr, uid, 'stock.stock_location_stock')
    }

    def create(self, cr, uid, vals, context=None):
        context = context or {}
        if ('name' not in vals) or (vals.get('name') in ('/', False)):
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'stock.change', context=context) or '/'
        return super(stock_change, self).create(cr, uid, vals, context=context)

    def action_submit(self, cr, uid, ids, context=None):
        '''  提交转换单，检查出库行中产品的可用性，如果可用，状态由草稿变为待审批    '''
        assert(len(ids) == 1), 'This option should only be used for a single id at a time'
        move_obj = self.pool.get("stock.move")

        change = self.browse(cr, uid, ids, context=context)
        ''' 如果出库行或入库行为空，则给出警告 '''
        if not change.move_out_lines or not change.move_in_lines:
            raise osv.except_osv(u'警告！', u'请输入出库详情或入库详情！')
        move_out_ids = [x.id for x in change.move_out_lines]
        move_in_ids = [x.id for x in change.move_in_lines]
        ''' 先判断入库或出库行中产品数量是否<=0，如果是则给出警告。在判断产品可用性之前，先将入库和出库行中的状态修改为确认。'''
        in_amt = 0  #入库产品成本总额 = 入库行中产品的成本价 * 数量之和
        out_amt = 0 #出库产品成本总额 = 出库行中产品的成本价 * 数量之和
        for line in change.move_in_lines:
            if line.product_uom_qty <= 0:
                raise osv.except_osv(u'警告！', u'入库详情中的产品数量不能小于或等于0！')
            in_amt += line.product_uom_qty * line.product_id.standard_price
        move_obj.write(cr, uid, move_in_ids, {'state': 'confirmed'}, context=context)
        for line in change.move_out_lines:
            if line.product_uom_qty <= 0:
                raise osv.except_osv(u'警告！', u'出库详情中的产品数量不能小于或等于0！')
            out_amt += line.product_uom_qty * line.product_id.standard_price
        move_obj.write(cr, uid, move_out_ids, {'state': 'confirmed'}, context=context)
        ''' 如果出库行中的产品可用，将出库行中的状态修改为可用 '''
        move_obj.action_assign(cr, uid, move_out_ids, context=context)

        ''' 当出库行中产品数量不足时给出警告 '''
        for line in change.move_out_lines:
            if line.product_id.type == 'service':   # 不判断服务类型产品是否可用
                continue
            if line.state != 'assigned':
                raise osv.except_osv(u'警告！', u'出库数量超过仓库中可用库存！')
        self.write(cr, uid, ids, {
                                  'state': 'submit',
                                  'in_amt': in_amt,
                                  'out_amt': out_amt,
                                  }, context=context)
        return True

    def action_approve(self, cr, uid, ids, context=None):
        '''  点击审批按钮，状态由待审批变为已审批，产品数量也做相应增减    '''
        assert(len(ids) == 1), 'This option should only be used for a single id at a time'
        move_obj = self.pool.get("stock.move")

        change = self.browse(cr, uid, ids, context=context)
        move_in_ids = [x.id for x in change.move_in_lines]
        move_out_ids = [x.id for x in change.move_out_lines]

        ''' 出库行 '''
        out_amt = 0 #出库产品的总金额
        move_obj.action_done(cr, uid, move_out_ids, context=context)
        for line in change.move_out_lines:
            inventory_value = 0.0
            out_qty = 0
            # 计算附加成本行的成本总金额
            if line.product_id.type == 'service':
                inventory_value = line.product_id.standard_price * line.product_uom_qty
                out_qty = line.product_uom_qty
            # 计算库存类型产品的成本总金额
            for move_quants in line.quant_ids:
                inventory_value += move_quants.cost * move_quants.qty
                out_qty += move_quants.qty

            line.write({'price_unit': inventory_value * 1.0 / out_qty})
            out_amt += inventory_value

        ''' 入库行 '''
        in_amt = change.in_amt  #入库产品的总金额
        
        for line in change.move_in_lines:
            ''' 根据产生的出库 quants 来分摊入库产品的单价，填充到入库行的单价中 '''
            line.write({'price_unit': line.product_id.standard_price * out_amt / in_amt})
        move_obj.action_done(cr, uid, move_in_ids, context=context)
        self.write(cr, uid, ids, {'amount':out_amt,'state': 'done'}, context=context)
        return True

    def action_refuse(self, cr, uid, ids, context=None):
        '''  点击拒绝按钮，状态由待审批变为草稿   '''
        assert(len(ids) == 1), 'This option should only be used for a single id at a time'
        self.write(cr, uid, ids, {
                                  'state': 'draft',
                                  'in_amt': 0.0,
                                  'out_amt': 0.0,
                                  }, context=context)
        return True

    def action_move_create(self, cr, uid, ids, context=None):
        '''  点击记账按钮，状态由已审批变为完成，生成会计凭证    '''
        assert(len(ids) == 1), 'This option should only be used for a single id at a time'
        account_move_obj = self.pool.get("account.move")

        change = self.browse(cr, uid, ids, context=context)
        move_lines = []
        last_cat = None
        ''' 转换单的出库行产生的会计凭证明细 '''
        for line in change.move_out_lines:
            last_cat = line.product_id.categ_id
            move_lines.append({
                               'name': line.product_id.name,
                               'partner_id': change.partner_id.id,
                               'account_id': last_cat.property_stock_valuation_account_id.id,
                               'debit':0.00,
                               'credit': line.product_uom_qty * line.price_unit,
                               })

        ''' 转换单的入库行产生的会计凭证明细 '''
        for line in change.move_in_lines:
            last_cat = line.product_id.categ_id
            move_lines.append({
                               'name': line.product_id.name,
                               'partner_id': change.partner_id.id,
                               'account_id': last_cat.property_stock_valuation_account_id.id,
                               'debit': line.product_uom_qty * line.price_unit, #分摊成本
                               'credit':0.00,
                               })
        account_move_id = account_move_obj.create(cr, uid, {
                                          'ref': change.name,
                                          'journal_id': last_cat.property_stock_journal.id,
                                          'line_id': [(0,0,line_val) for line_val in move_lines]
                                          })

        self.write(cr, uid, ids, {'state': 'done', 'account_move_id': account_move_id}, context=context)
        return True

class stock_move(osv.osv):
    _inherit = 'stock.move'

    _columns = {
        'change_id': fields.many2one('stock.change', u'目的产品的转换单', select=True, copy=False),
        'raw_material_change_id': fields.many2one('stock.change', u'原产品的转换单', select=True),
    }

