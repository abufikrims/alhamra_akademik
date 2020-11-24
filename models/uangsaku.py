from odoo import api, fields, models, _

class uang_saku(models.Model):
    _name = 'uang.saku'
    _description = 'Pencatatan uang saku siswa'

    name = fields.Char(string="No. Referensi",  help="", readonly=True, default='Auto')
    siswa_id = fields.Many2one(comodel_name="res.partner",  string="Siswa", required=True, domain=[('student', '=', True)], help="")
    tgl_transaksi = fields.Date(string='Tanggal', required=True, default=fields.Date.context_today)
    no_va_saku = fields.Char(string='VA Uang Saku', related='siswa_id.va_saku')
    waktu_transaksi = fields.Char(string='Waktu Transaksi')
    amount_in = fields.Float('Nominal Masuk')
    amount_out = fields.Float('Nominal Keluar')
    ref_transaksi = fields.Char('Ref Transaksi')
    state = fields.Selection(string='State', selection=[('draft', 'Draft'), ('confirmed', 'Konfirmasi'),], default='draft')
    import_id = fields.Char('Import ID', help='Mencatat user yg dikirim oleh aplikasi luar')
    validasi_id = fields.Many2one('res.users','Validasi Oleh', readonly=True)
    validasi_time = fields.Datetime(string='Validasi', readonly=True)
    
    #nominal = fields.Float('Nominal', digits=dp.get_precision('Product Price'))

    @api.multi
    def action_confirm(self):
        self.write({'validasi_id': self.env.user.id,
            'validasi_time': fields.datetime.now()
        })
        return self.write({'state': 'confirmed'})

    def action_draft(self):
        return self.write({'state': 'draft'})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('uang.saku')
        return super(uang_saku, self).create(vals)