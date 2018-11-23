# -*- coding: utf-8 -*-
from openerp.osv import fields
from openerp.osv import osv
from openerp import models, SUPERUSER_ID
from openerp.tools.translate import _

class account_move_line(osv.osv):
    _inherit = "account.move.line"
    '''
        反核销操作后去修改res.partner的最后核销时间
    '''
    def _remove_move_reconcile(self, cr, uid, move_ids=None, opening_reconciliation=False, context=None):
        super(account_move_line, self)._remove_move_reconcile(cr, uid, move_ids=move_ids,
                                                                    opening_reconciliation=opening_reconciliation,
                                                                    context=None)
        for account_move_line_objs in self.browse(cr, uid, move_ids, context=context):
            obj_res_partner = self.pool.get('res.partner')
            obj_res_partner.mark_last_reconciliation_date_when_unreconciled(cr, uid, account_move_line_objs.partner_id.id, context=None)
        return True

    '''
        修正获取待核销的partner列表,不能按照最后的核销时间去判断,因为可能会先核销最近的account_move_line记录,
        导致之前的account_move_line不能被查询出来
    '''
    def list_partners_to_reconcile(self, cr, uid, context=None, filter_domain=False):
        line_ids = []
        if filter_domain:
            line_ids = self.search(cr, uid, filter_domain, context=context)
        where_clause = filter_domain and "AND l.id = ANY(%s)" or ""
        cr.execute(
            """SELECT partner_id FROM (
               SELECT l.partner_id, p.last_reconciliation_date, SUM(l.debit) AS debit, SUM(l.credit) AS credit, MAX(l.create_date) AS max_date
               FROM account_move_line l
               RIGHT JOIN account_account a ON (a.id = l.account_id)
               RIGHT JOIN res_partner p ON (l.partner_id = p.id)
                   WHERE a.reconcile IS TRUE
                   AND l.reconcile_id IS NULL
                   AND l.state <> 'draft'
                   %s
                   GROUP BY l.partner_id, p.last_reconciliation_date
               ) AS s
               WHERE debit > 0 AND credit > 0
               ORDER BY last_reconciliation_date"""
            % where_clause, (line_ids,))
        ids = [x[0] for x in cr.fetchall()]
        if not ids:
            return []

        # To apply the ir_rules
        partner_obj = self.pool.get('res.partner')
        ids = partner_obj.search(cr, uid, [('id', 'in', ids)], context=context)
        return partner_obj.name_get(cr, uid, ids, context=context)

class res_partner(osv.osv):
    _inherit = 'res.partner'
    '''
        标记反核销操作后,res.partner的最后核销时间
    '''
    def mark_last_reconciliation_date_when_unreconciled(self, cr, uid, partner_id, context=None):
        cr.execute("""
                UPDATE res_partner SET last_reconciliation_date = TEMP .last_reconciliation_date FROM
                  (
                    SELECT MAX(write_date) AS last_reconciliation_date
                        FROM account_move_line
                        WHERE reconcile_id IS NOT NULL AND partner_id = %s
                  ) AS TEMP
                WHERE ID = %s
               """, (partner_id,partner_id))
        return True