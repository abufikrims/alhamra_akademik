import datetime
from odoo import models, fields, api, _

class jns_kegiatan_kalender(models.Model):
    _name = "jns_kegiatan_kalender"
    _description = 'Jenis Kegiatan Kalender Akademik'

    name = fields.Char(required=True, string="Name",  help="")
    deskripsi = fields.Text( string="Deskripsi",  help="")
    is_libur = fields.Boolean( string="Libur ?",  help="")

class kaldik_periode(models.Model):
    _name = "kaldik_periode"
    _description = 'Kalender Akademik Periode Bulanan'

    name = fields.Char( required=True, string="Kegiatan",  help="")
    tanggal = fields.Date( string="Tanggal Mulai",  help="")
    tanggal_akhir = fields.Date( string="Tanggal Selesai",  help="")
    tanggal_akhir_cal = fields.Date('Tanggal Akhir', readonly=True, compute='compute_day',  store=True)
 
    # @api.one
    # @api.depends('tanggal', 'tanggal_akhir')
    # def compute_day(self):
    #     if self.tanggal and self.tanggal_akhir:
    #         tanggal = fields.Datetime.from_string(self.tanggal)
    #         tanggal_akhir = fields.Datetime.from_string(self.tanggal_akhir)
    #         self.duration = abs((tanggal_akhir - tanggal).days) + 1

    @api.one
    @api.depends('tanggal_akhir')
    def compute_day(self):
        if self.tanggal_akhir:
            self.tanggal_akhir_cal = self.tanggal_akhir + datetime.timedelta(days=1)

    periode_id = fields.Many2one(comodel_name="account.period",  string="Periode",  help="")
    jns_kegiatan_id = fields.Many2one(comodel_name="jns_kegiatan_kalender",  string="Jenis kegiatan",  help="")
