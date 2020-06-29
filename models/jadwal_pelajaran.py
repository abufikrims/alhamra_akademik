from odoo import api, fields, models

class jadwal_kelas(models.Model):
    _name = 'jadwal.kelas'
    _description = 'Jadwal Pelajaran per Kelas'

    name = fields.Many2one('ruang.kelas', 'Rombel', required=True)
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True)
    lembaga = fields.Selection([('SMP','SMP'),('SMA','SMA')], string='Lembaga', related='name.lembaga')
    # matpel_ids = fields.Many2many('mata.pelajaran', 'siswa_rel', 'siswa_id', 'partner_id', 'Siswa', domain=[('student', '=', True)])
    jadwal_detail_ids = fields.One2many(comodel_name='jadwal.detail',  inverse_name='jadwal_kelas_id',  string='Jadwal Pelajaran',  help='Jadwal Pelajaran')
    
class jadwal_pelajaran_detail(models.Model):
    _name = 'jadwal.detail'
    _description = 'Detail Jadwal Pelajaran per hari'
    _rec_name = 'jadwal_kelas_id'

    sequence = fields.Integer(string='Urutan')
    jadwal_kelas_id = fields.Many2one(comodel_name='jadwal.kelas', string='Jadwal Kelas')
    hari = fields.Selection(string='Hari', selection=[('ahad', 'Ahad'), ('senin', 'Senin'), ('selasa', 'Selasa'), ('rabu', 'Rabu'), ('kamis', 'Kamis'), ('jumat', 'Jum at'), ('sabtu', 'Sabtu'),], required=True)
    matpel_id = fields.Many2one(comodel_name="mata.pelajaran",  string="Matpel",  help="")
    jam_ke = fields.Integer(string='Jam Ke')
    lembaga = fields.Selection([('SMP','SMP'),('SMA','SMA')], string='Lembaga', related='jadwal_kelas_id.lembaga')
    guru = fields.Many2one('hr.employee', 'Guru/Ustadz Pengajar', required=True, domain="[('lembaga', '=', lembaga)]")
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', related='jadwal_kelas_id.fiscalyear_id')
  
    # @api.multi
    # def name_get(self):
    #     res = []
    #     for rec in self:
    #         res.append((rec.id, '%s - %s / %s' % (rec.jadwal_kelas_id, rec.hari, rec.jam_ke)))
    #     return res