from odoo import api, fields, models, _


class pendidikan_guru(models.Model):
    _name = 'edu.employee'
    _description = 'Riwayat Pendidikan Guru'

    name = fields.Char(string='Nama Institusi')
    jenjang = fields.Selection(string='Jenjang', selection=[('sd', 'SD/MI'), ('smp', 'SMP/MTS'),('sma', 'SMA/MA'),('diploma', 'D1/D2/D3'),('sarjana', 'D4/S1'),('pasca', 'S2/S3'),('lainnya', 'Lainnya/Non Formal')])
    fakultas = fields.Char(string='Fakultas/Jurusan')
    gelar = fields.Char(string='Gelar')
    karya_ilmiah = fields.Char(string='Skripsi/Tesis/Disertasi')
    lulus = fields.Date(string='Lulus')
    employee_id = fields.Many2one(comodel_name="hr.employee",  string="Guru/Karyawan",  help="")
    
class guru(models.Model):
    _inherit = 'hr.employee'
    pendidikan_guru_ids = fields.One2many(comodel_name="edu.employee",  inverse_name="employee_id",  string="Riwayat Pendidikan",  help="")
