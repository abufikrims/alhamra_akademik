from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
import time
from odoo.exceptions import UserError

class generate_invoice(models.TransientModel):
    _name = "generate.invoice"

    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True)
    komponen_id = fields.Many2one('komponen.usaha', 'Komponen', required=True)
    period_from = fields.Many2one('account.period', 'Bulan Awal', required=True, domain="[('special', '=', False), ('fiscalyear_id', '=', fiscalyear_id)]")
    period_to = fields.Many2one('account.period', 'Bulan Akhir', required=True, domain="[('special', '=', False), ('fiscalyear_id', '=', fiscalyear_id)]")
    partner_ids = fields.Many2many('res.partner', 'partner_rel', 'siswa_id', 'partner_id', 'Students', required=True, domain="[('bebasbiaya', '=', False), ('fiscalyear_id', '=', fiscalyear_id)]")
    name = fields.Integer('Harga')

    @api.onchange('fiscalyear_id')
    def onchange_fiscalyear_id(self):
        if self.fiscalyear_id:
            self.update({'partner_ids': False, 'komponen_id': False})

    @api.onchange('komponen_id', 'name')
    def onchange_komponen_id(self):
        if self.komponen_id:
            harga = self.env['fiscalyear.harga'].search([('fiscalyear_id', '=', self.fiscalyear_id.id), ('name', '=', self.komponen_id.id)], limit=1)
            if not harga:
                return {
                    'value': {'partner_ids': False, 'komponen_id': False, 'name': 0},
                    'warning': {'title': 'Perhatian', 'message': 'Harga komponen belum di tentukan pada tahun ajaran'}
                }

            self.update({'name': harga.price_unit})

    @api.onchange('jemput')
    def onchange_jemput(self):
        if self.fiscalyear_id:
            return {'value': {'partner_ids': False}, 'domain': {'partner_ids': [('jemput', '=', self.jemput), ('fiscalyear_id', '=', self.fiscalyear_id.id)]}}

    @api.multi
    def create_invoice(self):
        if self.period_from.id > self.period_to.id:
            raise UserError(("Bulan Awal lebih besar daripada bulan akhir !"))
        elif not self.partner_ids:
            raise UserError(("Siswa belum di pilih !"))

        #obj_hadir = self.env['kehadiran.siswa']
        obj_period = self.env['account.period']
        obj_invoice = self.env['account.invoice']
        obj_invoice_line = self.env['account.invoice.line']

        produk = self.komponen_id.product_id
        journal_id = obj_invoice.default_get(['journal_id'])['journal_id']
        period_ids = obj_period.search([('id', '>=', self.period_from.id), ('id', '<=', self.period_to.id)])

        for period in period_ids:
            for x in self.partner_ids:
                disc_amount = 0; disc_persen = 0
                if x.harga_komponen:
                    disc = self.env['res.partner.harga'].search([('partner_id', '=', x.id), ('name', '=', self.komponen_id.id)])
                    print(disc)
                    if disc:
                        disc_amount = disc.disc_amount
                        disc_persen = disc.disc_persen

                qty = 1
                if self.komponen_id.type == 'makan':
                    hari = obj_hadir.search([('siswa_id', '=', x.id), ('catering', '=', True), ('tanggal', '>=', period.date_start), ('tanggal', '<=', period.date_end)])
                    qty = sum([h.name for h in hari])
                elif self.komponen_id.type == 'jemput':
                    hari = obj_hadir.search([('siswa_id', '=', x.id), ('jemputan', '=', True), ('tanggal', '>=', period.date_start), ('tanggal', '<=', period.date_end)])
                    qty = sum([h.name for h in hari])

                zid = obj_invoice.create({
                        'name': 'Generate Invoice',
                        'type': 'out_invoice',
                        'account_id': x.property_account_receivable_id.id,
                        'student': True,
                        'cicil': self.komponen_id.cicil,
                        'komponen_id': self.komponen_id.id,
                        'fiscalyear_id': self.fiscalyear_id.id,
                        'orangtua_id': x.orangtua_id.id,
                        'class_id': x.class_id.id,
                        'partner_id': x.id,
                        'partner_shipping_id': x.id,
                        'journal_id': journal_id,
                        'currency_id': self.env.user.company_id.currency_id.id,
                        'fiscal_position_id': x.property_account_position_id.id,
                        'date_invoice': period.date_start,
                        'company_id': self.env.user.company_id.id,
                        'period_id': period.id,
                        'user_id': self.env.uid or False
                    })

                obj_invoice_line.create({
                        'name': produk.partner_ref,
                        'product_id': produk.id or False,
                        'discount': disc_persen,
                        'discount_amount': disc_amount,
                        'invoice_id': zid.id,
                        'account_id': produk.property_account_income_id.id or produk.categ_id.property_account_income_categ_id.id,
                        'price_unit': self.name - disc_amount,
                        'quantity': qty,
                        'uom_id': produk.uom_id.id,
                })

        return True