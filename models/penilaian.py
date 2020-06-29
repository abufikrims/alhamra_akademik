from odoo import api, fields, models, _


class score_list(models.Model):
    _name = 'score.list'

    name = fields.Char('Nomor', required=True, default='/')
    type = fields.Selection([('ws', 'Work Sheet (WS)'), ('uh', 'Daily Test (UH)'), ('uts', 'UTS'), ('uas', 'UAS')], string='Tipe', required=True, default='ws')
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True)
    user_id = fields.Many2one('res.users', 'Guru', required=True, default=lambda self: self.env.user)
    class_id = fields.Many2one('ruang.kelas', 'Ruang Kelas', required=True, domain="[('fiscalyear_id', '=', fiscalyear_id)]")
    subject_id = fields.Many2one('mata.pelajaran', 'Mata Pelajaran', required=True)
    date1 = fields.Date('Tanggal U1')
    date2 = fields.Date('Tanggal U2')
    date3 = fields.Date('Tanggal U3')
    date4 = fields.Date('Tanggal U4')
    date5 = fields.Date('Tanggal U5')
    score_line = fields.One2many('score.line', 'score_id', 'Tabel Nilai')
    uts_line = fields.One2many('uts.line', 'score_id', 'Nilai UTS')
    uas_line = fields.One2many('uas.line', 'score_id', 'Nilai UAS')
    semester = fields.Selection([('gasal', 'Semester Gasal'), ('genap', 'Semester Genap')], string='Semester', required=True, default='gasal')

    _sql_constraints = [('subject_uniq', 'unique(subject_id, type, semester, class_id, fiscalyear_id)', 'Data harus unik !')]


    @api.model
    def create(self, vals):
        if vals['type'] == 'ws':
            vals['name'] = self.env['ir.sequence'].next_by_code('score.list.ws')
        elif vals['type'] == 'uh':
            vals['name'] = self.env['ir.sequence'].next_by_code('score.list.uh')
        elif vals['type'] == 'uts':
            vals['name'] = self.env['ir.sequence'].next_by_code('score.list.uts')
        elif vals['type'] == 'uas':
            vals['name'] = self.env['ir.sequence'].next_by_code('score.list.uas')

        result = super(score_list, self).create(vals)
        return result

    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.user_id:
            self.update({'user_id': self.env.uid})

    @api.onchange('class_id', 'type')
    def onchange_class_id(self):
        if self.class_id:

            nilai = []
            for x in self.class_id.siswa_ids:
                nilai.append({'name': x.id})

            data = {'score_line': nilai}
            if self.type == 'uts':
                data = {'uts_line': nilai}
            elif self.type == 'uas':
                data = {'uas_line': nilai}

            self.update(data)

    @api.one
    def compute_score(self):
        if self.type in ('ws', 'uh'):
            n = 0
            r = self.score_line[0]

            if r.u1:
                n += 1
            if r.u2:
                n += 1
            if r.u3:
                n += 1
            if r.u4:
                n += 1
            if r.u5:
                n += 1

            for x in self.score_line:
                sum = x.u1 + x.u2 + x.u3 + x.u4 + x.u5
                x.write({'sum': sum, 'avg': sum/n})
        return True


class score_line(models.Model):
    _name = 'score.line'

    score_id = fields.Many2one('score.list', 'Daftar Nilai', required=True, ondelete='cascade')
    name = fields.Many2one('res.partner', 'Siswa', required=True, domain=[('student', '=', True)])
    u1 = fields.Integer('U1')
    u2 = fields.Integer('U2')
    u3 = fields.Integer('U3')
    u4 = fields.Integer('U4')
    u5 = fields.Integer('U5')
    sum = fields.Integer('Total', readonly=True)
    avg = fields.Integer('Rata-Rata', readonly=True)


class uts_line(models.Model):
    _name = 'uts.line'

    score_id = fields.Many2one('score.list', 'Daftar Nilai', required=True, ondelete='cascade')
    name = fields.Many2one('res.partner', 'Siswa', required=True, domain=[('student', '=', True)])
    nilai = fields.Integer('Nilai')


class uas_line(models.Model):
    _name = 'uas.line'

    score_id = fields.Many2one('score.list', 'Daftar Nilai', required=True, ondelete='cascade')
    name = fields.Many2one('res.partner', 'Siswa', required=True, domain=[('student', '=', True)])
    nilai = fields.Integer('Nilai')

class absen_penilaian(models.Model):
    _name = 'absen.penilaian'

    name = fields.Date('Tanggal', required=True, default=fields.Date.context_today)
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Tahun Ajaran', required=True)
    class_id = fields.Many2one('ruang.kelas', 'Ruang Kelas', required=True, domain="[('fiscalyear_id', '=', fiscalyear_id)]")
    subject_id = fields.Many2one('mata.pelajaran', 'Mata Pelajaran', required=True)
    semester = fields.Selection([('gasal', 'Semester Gasal'), ('genap', 'Semester Genap')], 'Semester', required=True)
    penilaian_line = fields.One2many('penilaian.line', 'penilaian_id', 'Valuation Lines')

    _sql_constraints = [('valuation_uniq', 'unique(semester, subject_id, name, class_id, fiscalyear_id)', 'Data harus unik !')]

    @api.onchange('class_id')
    def onchange_class_id(self):
        if self.class_id:

            nilai = []
            for x in self.class_id.siswa_ids:
                nilai.append({'name': x.id, 'kehadiran': 'hadir'})

            data = {'penilaian_line': nilai}
            self.update(data)


class penilaian_line(models.Model):
    _name = 'penilaian.line'

    penilaian_id = fields.Many2one('absen.penilaian', 'Penilaian Kehadiran', required=True, ondelete='cascade')
    name = fields.Many2one('res.partner', 'Siswa', required=True, domain=[('student', '=', True)])
    nis = fields.Char(string='NIS', related='name.nis')
    kehadiran = fields.Selection(string='Kehadiran', selection=[('hadir', 'Hadir'), ('sakit', 'Sakit'),  ('ijin', 'Ijin'),  ('alpa', 'Alpa'), ])
    
