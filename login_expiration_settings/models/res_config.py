from odoo import fields, api, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    expire_in_days = fields.Integer("Expire User after account cretion in days", default=5, config_parameter="login_expiration_settings.expire_in_days")

    # @api.constrains('block_attempts', 'login_cooldown_after')
    # def check_block_attempts(self):
    #     for rec in self:
    #         if rec.block_attempts > 0:
    #             if rec.login_cooldown_after > rec.block_attempts:
    #                 raise UserError(_("'Block User After Login Failures' can't be less than 'Maximum Login Failures to Lockout Account'"))
