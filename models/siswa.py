import re
from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.osv.expression import get_unaccent_wrapper

class master_kelas(models.Model):
    _name = 'master.kelas'
    _description = 'Master Kelas'

    name = fields.Char('Nama', required=True)
    lembaga = fields.Selection([('SMP','SMP'),('SMA','SMA')], string='Lembaga', required=True, default='SMP')
    grade = fields.Selection([('a', 'A'), ('b', 'B'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12')], string='Grade', required=True)

class mata_pelajaran(models.Model):
    _name = 'mata.pelajaran'
    _description = 'Mata Pelajaran'

    urut = fields.Integer('No. Urut', required=True)
    name = fields.Char('Nama', required=True)
    kode = fields.Char(string='Kode Matpel')
    jenjang = fields.Selection([('SMP','SMP'),('SMA','SMA')], string='Jenjang Pendidikan', default='SMP')
    kategori = fields.Selection(selection=[('akademik','Akademik'),('diniyyah','Diniyyah'),('tahfizh','Tahfizh'),('ekstrakurikuler','Ekstrakurikuler'),('lainnya','Lainnya')],  string="Kategori Matpel",  help="")

    @api.model
    def create(self, vals):
        vals['urut'] = self.env['ir.sequence'].next_by_code('mata.pelajaran')
        return super(mata_pelajaran, self).create(vals)    

class ruang_kelas(models.Model):
    _name = 'ruang.kelas'
    _description = 'Ruang Kelas'

    name = fields.Many2one('master.kelas', 'Rombel', required=True)
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True)
    lembaga = fields.Selection([('SMP','SMP'),('SMA','SMA')], string='Lembaga', related='name.lembaga')
    siswa_ids = fields.Many2many('res.partner', 'siswa_rel', 'siswa_id', 'partner_id', 'Siswa', domain=[('student', '=', True)])
    wali_kelas = fields.Many2one('hr.employee', 'Wali Kelas', required=True, domain="[('lembaga', '=', lembaga)]")

    data_file = fields.Binary('Import File')

    _sql_constraints = [('name_uniq', 'unique(name, fiscalyear_id)', 'Kelas & Tahun Ajaran harus unik !')]

    @api.one
    def update_class(self):
        obj_invoice = self.env['account.invoice']

        iid = obj_invoice.search([('partner_id', 'in', [i.id for i in self.siswa_ids])])
        if iid:
            iid.write({'class_id': self.name.id})

        for x in self.siswa_ids:
            x.write({'class_id': self.name.id})
        return True


    @api.multi
    def import_siswa(self):
        pass


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    nip = fields.Char('NIP')
    lembaga = fields.Selection([('SMP','SMP'),('SMA','SMA')], string='Lembaga', default='SMP')



class res_partner(models.Model):
    _inherit = 'res.partner'

    nis = fields.Char('NIS')
    nisn = fields.Char('NISN')
    virtual_account = fields.Char('Virtual Account')
    va_saku = fields.Char(string="No VA Uang Saku")
    propinsi = fields.Char(string="Propinsi")
    

    lembaga = fields.Selection([('SMP','SMP'),('SMA','SMA')], string='Lembaga', related='class_id.lembaga')
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran')
    class_id = fields.Many2one('master.kelas', 'Ruang Kelas', readonly=True)

    panggilan = fields.Char('Nama Panggilan')
    student = fields.Boolean('Status Siswa')
    parent = fields.Boolean('Status Orang Tua')
    guru = fields.Boolean('Status Guru')

    darah = fields.Selection([('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O'), ('-', '-')], 'Gol Darah', default='A')
    birth = fields.Date('Tanggal')
    place = fields.Char('Tempat')

    kelamin = fields.Selection([('Laki', 'Laki-Laki'), ('Perempuan', 'Perempuan')], 'Jenis Kelamin', default='Laki')
    agama = fields.Selection([('islam', 'Islam'), ('katolik', 'Katolik'), ('protestan', 'Protestan'), ('hindu', 'Hindu'), ('budha', 'Budha')], 'Agama', default='islam')
    warga = fields.Selection([('wni', 'WNI'), ('turunan', 'WNI Keturunan')], 'Kebangsaan', default='wni')

    kandung = fields.Integer('Jumlah Saudara Kandung')
    tiri = fields.Integer('Jumlah Saudara Tiri')
    angkat = fields.Integer('Jumlah Saudara Angkat')

    bahasa = fields.Char('Bahasa di rumah', default='Indonesia')
    tinggal_dengan = fields.Char(string="Tinggal Dengan", help="")

    ayah = fields.Char('Nama Ayah')
    ayah_tmp_lahir = fields.Char( string="Tempat Lahir Ayah",  help="")
    ayah_tgl_lahir = fields.Date( string="Tanggal Lahir Ayah",  help="")
    ayah_warganegara = fields.Char( string="Kewarganegaraan Ayah",  help="")
    ayah_telp = fields.Char( string="No Telepon/HP Ayah",  help="")
    ayah_email = fields.Char( string="Email Ayah",  help="")
    ayah_pekerjaan = fields.Char( string="Pekerjaan Ayah",  help="")
    ayah_alamat_kantor = fields.Text( string="Alamat Kantor Ayah",  help="")
    ayah_penghasilan = fields.Integer( string="Penghasilan Ayah/bln",  help="")
    ayah_pendidikan = fields.Selection(selection=[('SD','SD'),('SMP','SMP Sederajat'),('SMA','SMA Sederajat'),('Diploma','Diploma'),('S1','Sarjana S1'),('S2','Magister S2'),('S3','Doktoral S3')],  string="Pendidikan Ayah",  help="")
    ayah_agama = fields.Selection([('islam', 'Islam'), ('katolik', 'Katolik'), ('protestan', 'Protestan'), ('hindu', 'Hindu'), ('budha', 'Budha')], 'Agama Ayah', default='islam')

    ibu = fields.Char('Nama Ibu')
    ibu_tmp_lahir = fields.Char( string="Tempat Lahir Ibu",  help="")
    ibu_tgl_lahir = fields.Date( string="Tanggal Lahir Ibu",  help="")
    ibu_warganegara = fields.Char( string="Kewarganegaraan Ibu",  help="")
    ibu_telp = fields.Char( string="No Telepon/HP Ibu",  help="")
    ibu_email = fields.Char( string="Email Ibu",  help="")
    ibu_pekerjaan = fields.Char( string="Pekerjaan Ibu",  help="")
    ibu_alamat_kantor = fields.Text( string="Alamat Kantor Ibu",  help="")
    ibu_penghasilan = fields.Integer( string="Penghasilan Ibu/bln",  help="")
    ibu_pendidikan = fields.Selection(selection=[('SD','SD'),('SMP','SMP Sederajat'),('SMA','SMA Sederajat'),('Diploma','Diploma'),('S1','Sarjana S1'),('S2','Magister S2'),('S3','Doktoral S3')],  string="Pendidikan Ibu",  help="")
    ibu_agama = fields.Selection([('islam', 'Islam'), ('katolik', 'Katolik'), ('protestan', 'Protestan'), ('hindu', 'Hindu'), ('budha', 'Budha')], 'Agama Ibu', default='islam')
 
    wali = fields.Char('Nama Wali')
    wali_tmp_lahir = fields.Char( string="Tempat Lahir Wali",  help="")
    wali_tgl_lahir = fields.Date( string="Tanggal lahir Wali",  help="")
    wali_warganegara = fields.Char( string="Kewarganegaraan Wali ",  help="")
    wali_telp = fields.Char( string="No Telepon/WA Wali",  help="")
    wali_email = fields.Char( string="Email Wali",  help="")
    wali_pekerjaan = fields.Char( string="Pekerjaan Wali",  help="")
    wali_alamat_kantor = fields.Text( string="Alamat Kantor Wali",  help="")
    wali_penghasilan = fields.Integer( string="Penghasilan Wali/bln",  help="")
    wali_pendidikan = fields.Selection(selection=[('SD','SD'),('SMP','SMP Sederajat'),('SMA','SMA Sederajat'),('Diploma','Diploma'),('S1','Sarjana S1'),('S2','Magister S2'),('S3','Doktoral S3')],  string="Pendidikan Wali",  help="")
    wali_agama = fields.Selection([('islam', 'Islam'), ('katolik', 'Katolik'), ('protestan', 'Protestan'), ('hindu', 'Hindu'), ('budha', 'Budha')], 'Agama Wali', default='islam')
    relasi = fields.Char('Hubungan Wali')
 
    orangtua_id = fields.Many2one('res.partner', 'Orang Tua', domain=[('parent', '=', True)])

    anak_line = fields.One2many('res.partner', 'orangtua_id', 'Siswa', readonly=True)

    tgl_daftar = fields.Date( string="Tanggal Pendaftaran",  help="Tanggal Pendaftaran")
    no_daftar = fields.Char( string="Nomor Pendaftaran",  help="No Pendaftaran")
    program_daftar = fields.Selection(selection=[('Reguler','Reguler 10-30 juz 6 th'),('Tahfidz','Tahfidz 30 Juz 3 thn')],  string="Program daftar", default='Reguler', help="")
    nik = fields.Char( string="NIK",  help="Nomor Induk Keluarga")
    cita_cita = fields.Char( string="Cita cita",  help="")
    hobi = fields.Char( string="Hobi",  help="")
    
    tinggi_badan = fields.Float( string="Tinggi Badan (cm)", digits=(6,2),  help="")
    berat_badan = fields.Float( string="Berat Badan (kg)", digits=(6,2),  help="")

    rt_rw = fields.Char( string="RT / RW",  help="")
    # tinggal_dengan = fields.Char(string="Tinggal Dengan", help="")

    sakit_tbc_pernah = fields.Boolean( string="Pernah TBC",  help="")
    sakit_tbc_ket = fields.Char( string="Sakit TBC",  help="")
    sakit_asma_pernah = fields.Boolean( string="Pernah ASMA",  help="")
    sakit_asma_ket = fields.Char( string="Sakit ASMA",  help="")
    sakit_hepatitisb_pernah = fields.Boolean( string="Pernah Hepatitis B",  help="")
    sakit_hepatitisb_ket = fields.Char( string="Sakit Hepatitis B",  help="")
    sakit_cacar_pernah = fields.Boolean( string="Pernah CACAR",  help="")
    sakit_cacar_ket = fields.Char( string="Sakit CACAR",  help="")
    sakit_lain_pernah = fields.Boolean( string="Pernah Sakit Berat Lainnya",  help="")
    sakit_lain_ket = fields.Char( string="Sakit Berat Lainnya",  help="")

    sekolah_asal = fields.Char( string="Sekolah asal",  help="")
    alamat_sekolah_asal = fields.Text( string="Alamat sekolah asal",  help="")
    kepsek_sekolah_asal = fields.Char( string="Nama Kepala Sekolah",  help="")
    telp_sekolah_asal = fields.Char( string="Telp sekolah asal",  help="")
    status_sekolah_asal = fields.Selection(selection=[('Negeri','Negeri'),('Swasta','Swasta')],  string="Status sekolah asal",  help="")
    prestasi_di_sekolah = fields.Text( string="Prestasi di sekolah",  help="")
    raport_4sd_1 = fields.Float( string="Raport 4 SD Smt 1",  help="")
    raport_4sd_2 = fields.Float( string="Raport 4 SD Smt 2",  help="")
    raport_5sd_1 = fields.Float( string="Raport 5 SD Smt 1",  help="")
    raport_5sd_2 = fields.Float( string="Raport 5 SD Smt 2",  help="")
    raport_6sd_1 = fields.Float( string="Raport 6 SD Smt 1",  help="")
    baca_quran = fields.Selection(selection=[('Belum Bisa','Belum Bisa'),('Kurang Lancar','Kurang Lancar'),('Lancar','Lancar'),('Tartil','Tartil')],  string="Baca quran",  help="")
    institusi_tahfidz = fields.Char( string="Institusi Tahfidz Sebelumnya",  help="")
    hafalan_sejak_kelas = fields.Char( string="Hafalan Sejak Kelas",  help="")
    motivasi_menghafal = fields.Text( string="Motivasi Menghafal",  help="")
    pilihan_tahfidz = fields.Selection(selection=[('1 Tahun','1 Tahun'),('2 Tahun','2 Tahun')],  string="Pilihan tahfidz",  help="")

    # Tambahan field pada modul TataUsaha
    bebasbiaya = fields.Boolean('Bebas Biaya')
    harga_komponen = fields.One2many('res.partner.harga', 'partner_id', 'Harga Khusus')


    @api.onchange('student')
    def onchange_student(self):
        if self.student:
            self.update({'student': self.student, 'customer': self.student, 'parent': not self.student})

    @api.onchange('parent')
    def onchange_parent(self):
        if self.parent:
            self.update({'student': not self.parent, 'customer': not self.parent, 'parent': self.parent})

    @api.multi
    def _get_saldo_saku(self):
        saldo_saku = self.env['uang.saku'].search([('siswa_id','=',self.id),('state','not in',['draft','cancel'])])
        self.saldo_uang_saku = sum((item.amount_in - item.amount_out) for item in saldo_saku)

    saldo_uang_saku = fields.Float('Saldo Uang Saku', compute='_get_saldo_saku') 

    def open_uang_saku(self):
        return {
            'name'  : _('Uang Saku'),
            'domain' : [('siswa_id','=',self.id)],
            'view_type' : 'form',
            'res_model' : 'uang.saku',
            'view_id' : False,
            'view_mode': 'tree,form',
            'type':'ir.actions.act_window'
        }

    @api.multi
    def _get_saldo_tagihan(self):
        saldo_invoice = self.env['account.invoice'].search([('partner_id','=',self.id),('state','=','open')])
        self.saldo_tagihan = sum(item.residual_signed for item in saldo_invoice)

    saldo_tagihan = fields.Float('Saldo Tagihan', compute='_get_saldo_tagihan')

    def open_tagihan(self):
        return {
            'name'  : _('Tagihan'),
            'domain' : [('partner_id','=',self.id)],
            'view_type' : 'form',
            'res_model' : 'account.invoice',
            'view_id' : False,
            'view_mode': 'tree,form',
            'type':'ir.actions.act_window'
        }

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('nis',operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()