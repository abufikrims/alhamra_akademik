from datetime import datetime
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class account_fiscalyear(models.Model):
    _inherit = 'account.fiscalyear'

    harga_komponen = fields.One2many('fiscalyear.harga', 'fiscalyear_id', 'Komponen Price')


class fiscalyear_harga(models.Model):
    _name = "fiscalyear.harga"

    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True, ondelete='cascade')
    name = fields.Many2one('komponen.usaha', 'Komponen', required=True)
    price_unit = fields.Float('Harga', digits=dp.get_precision('Product Price'))


class komponen_usaha(models.Model):
    _name = "komponen.usaha"

    name = fields.Char('Nama', required=True)
    type = fields.Selection((('gedung', 'Uang Gedung'), ('spp', 'SPP'), ('sekolah', 'Biaya Sekolah (Buku, Kegiatan, Seragam, dll)'),
                              ('ujian', 'Biaya Ujian'), ('ulang', 'Daftar Ulang'), ('pindah', 'Pindahan'), ('laundry','Laundry'),
                              ('ekskul', 'Ekstrakurikuler'), ('fkks', 'FKKS'), ('wisuda', 'Biaya Wisuda'),
                              ('makan', 'Catering'), ('jahit', 'Jasa Jahit'), ('seragam', 'Bahan Seragam'), ('other', 'Lain-Lain')), 'Tipe', required=True)
    tujuan = fields.Selection((('yayasan','Yayasan'), ('sekolah','Sekolah')), 'Tujuan', required=True)
    cicil = fields.Selection((('credit', 'Credit'), ('cash','Cash')), 'Payment', required=True, default='cash')
    active = fields.Boolean('Active', default=True)
    product_id = fields.Many2one('product.product', 'Produk', required=True)


# class res_partner(models.Model):
#     _inherit = 'res.partner'

#     bebasbiaya = fields.Boolean('Bebas Biaya')
#     harga_komponen = fields.One2many('res.partner.harga', 'partner_id', 'Harga Khusus')


class res_partner_harga(models.Model):
    _name = "res.partner.harga"

    partner_id = fields.Many2one('res.partner', 'Partner', required=True, ondelete='cascade', domain=[('student', '=', True)])
    name = fields.Many2one('komponen.usaha', 'Komponen', required=True)
    disc_amount = fields.Integer('Disc Amount')
    disc_persen = fields.Integer('Disc Percent')
    notes = fields.Char('Keterangan')


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends('invoice_line_ids')
    def _add_line(self):
        self.info_line = ', '.join([line.name for line in self.invoice_line_ids])

    student = fields.Boolean('Siswa')
    cicil = fields.Selection((('credit', 'Credit'), ('cash','Hard Cash')), 'Pembayaran', default='cash')
    orangtua_id = fields.Many2one('res.partner', 'Orang Tua', related='partner_id.orangtua_id', readonly=True, store=True)
    class_id = fields.Many2one('master.kelas', 'Ruang Kelas', related='partner_id.class_id', readonly=True, store=True)
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', related='partner_id.fiscalyear_id', readonly=True, store=True)
    komponen_id = fields.Many2one('komponen.usaha', 'Komponen', readonly=True, states={'draft': [('readonly', False)]})
    period_id = fields.Many2one('account.period', string='Force Period', copy=False, readonly=True, states={'draft': [('readonly', False)]})

    info_line = fields.Char(compute='_add_line', string='Invoice Line')

    _sql_constraints = [('invoice_uniq', 'unique(komponen_id, partner_id, period_id)', 'Invoice sudah pernah dibuat !')]

    @api.onchange('orangtua_id')
    def onchange_orangtua_id(self):
        if self.partner_id:
            data = {'orangtua_id': self.partner_id.orangtua_id.id, 'fiscalyear_id': self.partner_id.fiscalyear_id.id}
            self.update(data)

    @api.onchange('komponen_id')
    def onchange_komponen_id(self):
        if self.komponen_id:
            product = []; harga = {}
            for o in self.partner_id.fiscalyear_id.harga_komponen:
                harga[o.name.product_id.id] = o.price_unit

            i = self.komponen_id.product_id
            price = i.lst_price
            if harga.has_key(i.id):
                price = harga[i.id]
            product.append({
                            'name': i.partner_ref,
                            'product_id': i.id,
                            'uos_id': i.uom_id.id,
                            'price_unit': price,
                            'quantity': 1,
                            'account_id': i.categ_id.property_account_income_categ_id.id
            })

            self.update({'invoice_line_ids': product, 'cicil': self.komponen_id.cicil})

class manifest_pembayaran(models.Model):
    _name = "manifest.pembayaran"

    name = fields.Char('Reference', readonly=True, default='/')
    user_id = fields.Many2one('res.users', 'Operator', readonly=True, required=True, default=lambda self: self.env.user, copy=False)
    date = fields.Date('Tanggal', readonly=True, required=True, states={'draft': [('readonly', False)]}, default=fields.Date.context_today)
    siswa_id = fields.Many2one('res.partner', 'Siswa', domain=[('student', '=', True)], readonly=True, states={'draft': [('readonly', False)]})
    orangtua_id = fields.Many2one('res.partner', 'Orang Tua', domain=[('parent', '=', True)], readonly=True, states={'draft': [('readonly', False)]})
    tagihan_ids = fields.Many2many('account.invoice', 'tagihan_rel', 'manifest_id', 'tagihan_id', 'Invoice',
                                   domain=[('type', '=', 'out_invoice')], readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection(compute='compute_state', selection=[('draft', 'Draft'), ('paid', 'Paid')], string='Status', default='draft', store=True)
    currency_id = fields.Many2one("res.currency", string="Currency", compute='_compute_currency_id')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('manifest.pembayaran') or '/'
        result = super(manifest_pembayaran, self).create(vals)
        return result

    @api.multi
    def unlink(self):
        for o in self:
            if o.state == 'paid':
                raise UserError(('Manifest pembayaran tidak bisa dihapus pada status PAID !'))
        return super(manifest_pembayaran, self).unlink()

    @api.onchange('orangtua_id', 'siswa_id')
    def onchange_orangtua_siswa(self):
        value = {}
        domain_tagihan = [('state', '=', 'open'), ('type', '=', 'out_invoice')]
        if self.siswa_id:
            value = {'orangtua_id': self.siswa_id.orangtua_id.id}
            domain_tagihan.append(('partner_id', '=', self.siswa_id.id))
        if self.orangtua_id:
            # value = {'orangtua_id': self.siswa_id.orangtua_id.id}
            domain_tagihan.append(('orangtua_id', '=', self.orangtua_id.id))
        return {'domain': {'tagihan_ids': domain_tagihan}, 'value': value}

    @api.depends('tagihan_ids.amount_total')
    def _amount_all(self):
        for o in self:
            total = 0
            for i in o.tagihan_ids:
                total += i.amount_total
            o.update({
                'amount_total': total,
            })

    @api.multi
    def _compute_currency_id(self):
        try:
            main_company = self.sudo().env.ref('base.main_company')
        except ValueError:
            main_company = self.env['res.company'].sudo().search([], limit=1, order="id")
        for template in self:
            template.currency_id = main_company.currency_id.id

    @api.depends('tagihan_ids.state')
    def compute_state(self):
        for payment in self:
            if len(set([i.state for i in payment.tagihan_ids if i.state == 'paid'])) == 1:
                payment.state = 'paid'
            else:
                payment.state = 'draft'

    @api.multi
    def proses_pembayaran(self):
        for i in self.tagihan_ids:
            if i.state == 'draft':
                raise UserError(('Invoice status draft harus di validate terlebih dahulu'))
                # i.action_invoice_open()
            elif i.state == 'paid':
                raise UserError(('Invoice yang sudah paid tidak bisa diproses'))

        return {
            'name': _('Manifest Pembayaaran'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.register.payments',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_ids': [x.id for x in self.tagihan_ids],
                'active_model': 'account.invoice',
            }
        }


    @api.multi
    def print_manifest(self):
        return self.env.ref('alhamra_akademik.action_report_manifest').report_action(self)


class account_invoice_line_inherit(models.Model):
    _inherit = 'account.invoice.line'
    
    discount_amount = fields.Float(string='Discount Amount')

# class account_invoice_inherit(models.Model):
#     _inherit = 'account.invoice'

#     name = fields.Char(string='Name')

