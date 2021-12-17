from odoo import _,api,fields,models,http
from odoo.http import request
from odoo.addons.web.controllers.main import Home, db_monodb, ensure_db, set_cookie_and_redirect, login_and_redirect
from odoo.exceptions import AccessError, UserError, AccessDenied
import odoo
from datetime import datetime

class ResUsers(models.Model):
	_inherit = 'res.users'

	payment_done = fields.Boolean(string='Payment Done', default=False)
	expire_in_days = fields.Integer("Expire User after account creation in days", default=5)


class Home(Home):

	@http.route('/web/login', type='http', auth="none")
	def web_login(self, redirect=None, **kw):
		ensure_db()
		request.params['login_success'] = False
		if request.httprequest.method == 'GET' and redirect and request.session.uid:
			return http.redirect_with_hash(redirect)
		if not request.uid:
			request.uid = odoo.SUPERUSER_ID
		values = request.params.copy()
		try:
			values['databases'] = http.db_list()
		except odoo.exceptions.AccessDenied:
			values['databases'] = None
		if request.httprequest.method == 'POST':
			user_id = request.env['res.users'].sudo().search([('login','=',request.params['login'])])
			# conf_id = request.env['res.config.settings'].sudo().search([])
			# print("kkkkkkkkkkkkkkkkkkkkkkkkkk",request.params['login'],user_id,(datetime.now() - user_id.create_date).days)
			old_uid = request.uid
			try:
				if user_id and (datetime.now() - user_id.create_date).days >= user_id.expire_in_days and user_id.id != 2 and user_id.payment_done == False:
					request.params['login_success'] = False
					values['error'] = _("Login credentials expired!")
				else:
					uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
					request.params['login_success'] = True
					return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
			except odoo.exceptions.AccessDenied as e:
				request.uid = old_uid
				if e.args == odoo.exceptions.AccessDenied().args:
					values['error'] = _("Wrong login/password")
				else:
					values['error'] = e.args[0]
		else:
			if 'error' in request.params and request.params.get('error') == 'access':
				values['error'] = _('Only employee can access this database. Please contact the administrator.')
		if 'login' not in values and request.session.get('auth_login'):
			values['login'] = request.session.get('auth_login')
		if not odoo.tools.config['list_db']:
			values['disable_database_manager'] = True
		response = request.render('web.login', values)
		response.headers['X-Frame-Options'] = 'DENY'
		return response
