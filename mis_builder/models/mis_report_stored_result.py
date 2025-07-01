from odoo import fields, models

class MisReportStoredResult(models.Model):
    _name = 'mis.report.stored.result'
    _description = 'MIS Report Stored Result'

    report_instance_id = fields.Many2one(
        comodel_name='mis.report.instance',
        string='Report Instance',
        ondelete='cascade',
        required=True,
        index=True,
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User',
        ondelete='cascade',
        required=True,
        index=True,
    )
    report_key = fields.Char(
        string='Report Key',
        required=True,
        index=True,
    )
    computation_result = fields.Text(
        string='Computation Result',
        required=True,
    )
    last_computed = fields.Datetime()
