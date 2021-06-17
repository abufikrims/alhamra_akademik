from odoo import api, fields, models, exceptions, _

class uang_saku(models.Model):
    _name = 'uang.saku'
    _description = 'Pencatatan uang saku siswa'

    name = fields.Char(string="No. Referensi",  help="", readonly=True, default='Auto')
    siswa_id = fields.Many2one(comodel_name="res.partner",  string="Siswa", required=True, domain=[('student', '=', True)], help="")
    tgl_transaksi = fields.Date(string='Tanggal', required=True, default=fields.Date.context_today)
    no_va_saku = fields.Char(string='VA Uang Saku', related='siswa_id.va_saku')
    waktu_transaksi = fields.Char(string='Waktu Transaksi')
    jns_transaksi = fields.Selection(string='Jenis Transaksi', selection=[('masuk', 'Uang Masuk'), ('keluar', 'Uang Keluar')], default='masuk')
    saldo_saku = fields.Float(string='Saldo Awal U.Saku')
     
    amount_in = fields.Float('Nominal Masuk')
    amount_out = fields.Float('Nominal Keluar')
    ref_transaksi = fields.Char('Ref Transaksi')
    state = fields.Selection(string='State', selection=[('draft', 'Draft'), ('confirmed', 'Konfirmasi'),], default='draft')
    import_id = fields.Char('Import ID', help='Mencatat user yg dikirim oleh aplikasi luar')
    validasi_id = fields.Many2one('res.users','Validasi Oleh', readonly=True)
    validasi_time = fields.Datetime(string='Validasi', readonly=True)
    keterangan = fields.Text(string='Keterangan')
    
    #nominal = fields.Float('Nominal', digits=dp.get_precision('Product Price'))

    @api.multi
    def action_confirm(self):
        self.write({'validasi_id': self.env.user.id,
            'validasi_time': fields.datetime.now()
        })
        return self.write({'state': 'confirmed'})

    def action_draft(self):
        return self.write({'state': 'draft'})
    
    
    @api.onchange('siswa_id')
    def _onchange_siswa_id(self):
        for rec in self:
            if rec.siswa_id:
                rec.saldo_saku = rec.siswa_id.saldo_uang_saku

    @api.constrains('amount_in','amount_out','jns_transaksi','saldo_saku')
    def _check_saldo(self):
        # #saldo = self.env['res.partner'].search(['partner_id','=',self.siswa_id]).saldo_uang_saku
        # context = self._context
        # active_ids = context.get('active_ids')
        # partner_siswa_id = self.env['res.partner'].browse(active_ids[0])
        # saldo_saku_sekarang = partner_siswa_id.saldo_uang_saku

        if self.amount_out<0 or self.amount_in<0:
                raise exceptions.ValidationError('ERROR ! Nominal Harus Positif')

        if self.jns_transaksi=='keluar':
            if self.amount_out>self.saldo_saku:
                raise exceptions.ValidationError('ERROR ! Saldo Pengambilan tidak bisa melebihi SALDO UANG SAKU')
        


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('uang.saku')
        vals['state'] = 'confirmed'
        return super(uang_saku, self).create(vals)