# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError

class ProductCategorie(models.Model):
	_name = 'product.category'
	_inherit = 'product.category'
	type_categ = fields.Selection([('prestation','Prestation'),('autre','Autre')],string="Type")


class DetailsDepense(models.Model):
	_name = 'detail_depense'
	_description = 'Detail depense'
	motif = fields.Char(string = "Motif")
	montant = fields.Integer(string = "Montant")
	versement_quotidien_id = fields.Many2one('versement_quotidien',string = "Versement",ondelete='cascade')

class DetailsVente(models.Model):
	_name = 'detail_versement'
	_description = 'Detail versement'
	product_id = fields.Many2one('product.product',string = "Article")
	quantite = fields.Integer(string = "Quantité")
	total = fields.Integer(string = "Total",compute="_compute_total",store=True)
	prix_unitaire = fields.Integer(string = "Prix unitaire")
	versement_quotidien_id = fields.Many2one('versement_quotidien',string = "Versement",ondelete='cascade')
	#quantite_en_stock = fields.Integer(string = "Quantité en stock")
	boutique_id = fields.Many2one('pos.config',string="Boutique")
	date = fields.Date(string = "Date",default=fields.Date.context_today)
	@api.depends('quantite','prix_unitaire')
	def _compute_total(self):
		for record in self:
			record.total = record.quantite * record.prix_unitaire

class DetailsStock(models.Model):
	_name = 'detail_stock'
	_description = 'Detail stock'
	product_id = fields.Many2one('product.product',string = "Article")
	quantite_theorique = fields.Integer(string = "Quantité theorique",readonly=True)
	quantite_reelle = fields.Integer(string = "Quantité réelle")
	diff = fields.Integer(string = "Difference",default=0,compute = '_compute_diff',store=True)
	versement_quotidien_id = fields.Many2one('versement_quotidien',string = "Versement",ondelete='cascade')
	appro = fields.Integer(string = "Appro")
	rebut = fields.Integer(string = "Rebut")
	boutique_id = fields.Many2one('pos.config',string="Boutique")
	date = fields.Date(string = "Date",default=fields.Date.context_today)

	@api.model
	def create(self,data):
		boutique = self.env['pos.config'].search([('id','=',data['boutique_id'])],limit=1)
		if boutique:
			stock_quant_ids = self.env['stock.quant'].search([('product_id','=',data['product_id']),('location_id','=',boutique.picking_type_id.default_location_src_id.id)])
			data['quantite_theorique'] = sum(stock_quant_ids.mapped('quantity'))
		return super(DetailsStock,self).create(data)

	@api.depends('quantite_theorique','quantite_reelle')
	def _compute_diff(self):
		for record in self:
			record.diff = record.quantite_reelle - record.quantite_theorique

	"""@api.onchange('product_id')
	def onchange_quantite(self):
		if self.product_id:
			stock_quant_ids = self.env['stock.quant'].search([('product_id','=',self.product_id.id),('location_id','=',self.boutique_id.picking_type_id.default_location_src_id.id)])
			quantity = sum(stock_quant_ids.mapped('quantity'))
			self.quantite_theorique = quantity
			self.quantite_reelle = quantity"""

class Versement_quotidien(models.Model):
	_name = 'versement_quotidien'
	_description = 'versement quotidien'
	name = fields.Char(string = "référence")
	date = fields.Date(string = "Date",default=fields.Date.context_today,required = True)
	cosmetique_verse_par = fields.Many2one('hr.employee',string = "Versé par : ")#employee_id
	esthetique_verse_par = fields.Many2one('hr.employee',string = "Versé par")
	montant_a_verser = fields.Integer(string = "Montant à verser Cosmetique",compute='_compute_montant_a_verser',store=True)
	montant_verse = fields.Integer(string = "Montant versé Cosmetique")
	total_depense = fields.Integer(string = "Total dépense",compute='_compute_total_depense',store=True)
	boutique_id = fields.Many2one('pos.config',string="Boutique",required = True)
	ecart = fields.Integer(string = "Ecart cosmétique",compute="_compute_ecart",store=True)
	ecart_esthetique = fields.Integer(string = "Ecart esthétique",compute="_compute_ecart_esthetique",store=True)
	versement_banque = fields.Integer(string = "Versement banque")
	detail_versements = fields.One2many('detail_versement','versement_quotidien_id',string = "Détails")
	detail_stock = fields.One2many('detail_stock','versement_quotidien_id',string = "Détails stock")
	detail_depense = fields.One2many('detail_depense','versement_quotidien_id',string = "Détails dépense")
	observations = fields.Text(string = "Observations")
	montant_a_verse_esthetique = fields.Integer(string = "Montant à verser Esthétique")
	montant_verse_esthetique = fields.Integer(String = "Montant versé Esthétique")
	montant_total_a_verser = fields.Integer(string="Montant total à verser",compute="_compute_total_montant",store=True)
	montant_total_verse = fields.Integer(string="Montant total versé",compute="_compute_total_montant",store=True)
	total_ecart = fields.Integer(string="Total ecart")

	@api.model
	def create(self,data):
		data['name'] = "Versement du "+data['date']
		return super(Versement_quotidien,self).create(data)

	@api.depends('detail_depense.montant')
	def _compute_total_depense(self):
		for record in self:
			record.total_depense = sum(record.detail_depense.mapped('montant'))

	@api.depends('detail_versements.total','total_depense')
	def _compute_montant_a_verser(self):
		for record in self:
			if record.detail_versements:
				record.montant_a_verser = sum(record.detail_versements.mapped('total'))# - record.total_depense

	@api.depends('montant_verse','montant_a_verser')
	def _compute_ecart(self):
		self.ecart = self.montant_a_verser - self.montant_verse

	@api.depends('montant_verse_esthetique','montant_a_verse_esthetique')
	def _compute_ecart_esthetique(self):
		self.ecart_esthetique = self.montant_a_verse_esthetique - self.montant_verse_esthetique

	@api.depends('montant_verse_esthetique','montant_verse','montant_a_verser','montant_a_verse_esthetique','ecart','ecart_esthetique','total_depense')
	def _compute_total_montant(self):
		self.montant_total_verse = self.montant_verse + self.montant_verse_esthetique 
		self.montant_total_a_verser = self.montant_a_verse_esthetique + self.montant_a_verser - self.total_depense
		self.total_ecart = self.montant_total_a_verser - self.montant_total_verse#self.ecart + self.ecart_esthetique

	

	def mettre_a_jour_stock(self):
		if self.detail_stock:
			data = {'name':"Detail stock du "+str(self.name),'location_id':self.boutique_id.picking_type_id.default_location_src_id.id,'filter':'none'}
			inventory = self.env['stock.inventory'].search([('state','=','confirm')])
			if inventory:
				inventory.action_cancel_draft()#unlink()
				inventory.unlink()
			inventory = self.env['stock.inventory'].create(data)
			inventory.action_start()
			for line in self.detail_stock:
				inventaire_line = self.env['stock.inventory.line'].search([('inventory_id','=',inventory.id),('product_id','=',line.product_id.id)])
				inventaire_line.write({'product_qty':line.quantite_reelle})

			inventory.action_done()

	#calculer le montant à verser en fonction de session boutique
	@api.onchange('boutique_id','date')
	def calcul_montant_a_verser(self):
		#recuper les session à la date de la boutique
		montant = 0
		list_product = []
		liste = []
		liste1 = []
		liste_depenses = []
		if self.boutique_id and self.date:
			start_at = datetime.strptime(fields.Date.to_string(self.date) + ' ' + '00:00:00', '%Y-%m-%d %H:%M:%S')
			stop_at = datetime.strptime(fields.Date.to_string(self.date) + ' ' + '23:59:59', '%Y-%m-%d %H:%M:%S')			
			sessions_closed = self.env['pos.session'] \
						   .search([
						   		('config_id','=',self.boutique_id.id),
						   		('state','=','closed')
						   		])
			if sessions_closed:
				sessions = sessions_closed.filtered(lambda line: fields.Datetime.from_string(line.start_at) >= start_at and fields.Datetime.from_string(line.stop_at) <= stop_at)

				if not sessions:
					raise UserError(_("Aucune session du point de vente n'est ouverte à cette date"))
				else:
					for session in sessions:
						#**************Begin Depenses***************
						account_bank_statements = self.env['account.bank.statement'].search([('pos_session_id','=',session.id)])
						if account_bank_statements:
							for statement in account_bank_statements:
								account_bank_statement_lines = self.env['account.bank.statement.line'].search([('statement_id','=',statement.id),('amount','<',0)])
								if account_bank_statement_lines:
									for line in account_bank_statement_lines:
										liste_depenses.append((0,0,{'motif':line.name,'montant':abs(line.amount)}))

						#**************End Depenses*****************
						commandes = self.env['pos.order'].search([('session_id','=',session.id)])
						if commandes:
							montant += sum(commandes.mapped('amount_total'))
							#details$
							for commande in commandes:
								commande_lines = self.env['pos.order.line'].search([('order_id','=',commande.id)])
								if commande_lines:
									for line in commande_lines:
										if line.product_id not in list_product:
											list_product.append(line.product_id)
										liste.append({'product_id':line.product_id.id,'quantite':line.qty,'prix_unitaire':line.price_unit})
				#liste1 = []
				for product in list_product:
					dico1 = {'product_id':product.id,'quantite':0,'prix_unitaire':product.lst_price,'boutique_id':self.boutique_id.id,'date':self.date}
					for dico in liste:
						if dico['product_id'] == product.id:
							dico1['quantite'] += dico['quantite']
					liste1.append((0,0,dico1))
				#Quantite en stock
				all_product = self.env['product.product'].search([])
				liste = []
				for product in all_product:
					stock_quant_ids = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',self.boutique_id.picking_type_id.default_location_src_id.id)])
					if stock_quant_ids:
						qty = sum(stock_quant_ids.mapped('quantity'))
						liste.append((0,0,{'product_id':product.id,'quantite_theorique':qty,'quantite_reelle':qty,'boutique_id':self.boutique_id.id,'date':self.date}))


			#************Begin Esthetique******************************
			#objet = account.move
			factures_clients = self.env['account.move'].search([('invoice_date','=',self.date),('state','=','posted')])#paid
			#Liste users de la boutique en question
			list_users = []
			list_employes = self.env['hr.employee'].search([('boutique_id','=',self.boutique_id.id)])
			for employe in list_employes:
				if employe.user_id:
					list_users.append(employe.user_id)
			factures_clients_boutique = factures_clients.filtered(lambda line: line.user_id in list_users)
			somme_esthetique = sum(factures_clients_boutique.mapped('amount_untaxed'))
			self.montant_a_verse_esthetique = somme_esthetique
		#************End Esthetique********************************

			#self.montant_a_verser = montant
			self.detail_versements = liste1
			self.detail_stock = liste
			self.detail_depense = liste_depenses


class Prestation(models.Model):
	_name = 'prestation'
	_description = 'Prestation de service'
	_rec_name = 'product'
	#name = fields.Char(string="Prestation")
	product = fields.Many2one('product.product',string="Prestation",required=True)
	category = fields.Many2one('product.category',string="Type de prestation",domain="[('type_categ','=','prestation')]")
	category_name = fields.Char(related="category.name",string="Category name")
	#product_id = fields.Many2one('product.product',string="Produit")
	#type_prestation = fields.Many2one('type.prestation',string="Type de prestation",required=True)
	#type_prestation_name = fields.Char(related="type_prestation.name",string="")
	client = fields.Many2one('res.partner',required=True)
	#date_heure_debut = fields.Datetime(string="Date et heure de debut")
	#date_heure_fin = fields.Datetime(string="Date et heure de fin")
	fait_par = fields.Many2one('hr.employee',string="Fait par",required=True)
	enregistre_par = fields.Many2one('hr.employee',string="Enregistré par",required=True)
	#event_id = fields.Many2one('calendar.event',string="RV")
	#rv_id = fields.Many2one('rv.prestation',string="RV",ondelete="cascade")
	state = fields.Selection([('draft','Brouillon'),('facture','Facturé')],default="draft")
	#state = fields.Selection([('draft',"Brouillon"),('in_progress','En cours'),('done','Terminé')],default="draft")
	date = fields.Date(string = "Date",default=fields.Date.context_today)
	#date = fields.Date(string="Date",compute="_compute_date_heure",store=True)
	#heure_entree = fields.Char(string="Heure d'entrée",compute="_compute_date_heure",store=True)
	#heure_sortie = fields.Char(string="Heure de sortie",compute="_compute_date_heure",store=True)
	#duree = fields.Float(string="Durée(en heures)",compute="_compute_duree",store=True)
	nbre_seances = fields.Integer(string="Nombre de séances",default=1)
	maladies_a_signales = fields.Text(string="Maladie à signaler")
	remarques = fields.Text(string="Remarques ou commentaires")
	numero_convention = fields.Char(string="N° convention")
	date_convention = fields.Date(string = "Date de la convention",default=fields.Date.context_today)
	nombre_zones = fields.Integer(string = "Nombre de zones",default=1)
	forfait = fields.Integer(string = "FORFAIT")#,compute='_compute_forfait',store=True
	seances = fields.One2many('prestation.seance','prestation_id',string = "Séances")
	seance_count = fields.Integer(string="RV",compute="_compute_seance_count")
	boutique_id = fields.Many2one('pos.config',string="Lieu de travail")

	@api.model
	def default_get(self,default_fields):
		res = super(Prestation,self).default_get(default_fields)
		num = self.search_count([])
		if 'numero_convention' in default_fields:
			res.update({
						'numero_convention': num + 1,
				})
		if 'enregistre_par' in default_fields:
			current_employee = self.env['hr.employee'].search([('user_id','=',self.env.user.id)],limit=1)
			if current_employee:
				res.update({
						'enregistre_par':current_employee.id,
				})
				if current_employee.boutique_id:
					res.update({
						'boutique_id': current_employee.boutique_id.id,
						})
		return res

	def unlink(self):
		for record in self:
			if record.state == 'facture':
				raise UserError(_("Vous ne pouvez pas supprimer une prestation dèja facturée."))
		return super(Prestation,self).unlink()
	#@api.multi
	def _compute_seance_count(self):
		for prestation in self:
			prestation.seance_count = len(prestation.seances)


	@api.onchange('nombre_zones','product')
	def onchange_forfait(self):
		for record in self:
			if record.nombre_zones and record.product:
				record.forfait = record.nombre_zones * record.product.list_price

	@api.depends('nombre_zones','product')
	def _compute_forfait(self):
		for record in self:
			if record.nombre_zones and record.product:
				record.forfait = record.nombre_zones * record.product.list_price

	@api.onchange('nbre_seances')
	def onchange_nbre_seances(self):
		if self.nbre_seances > 1:
			#generer les seances
			liste = []
			for i in range(self.nbre_seances):
				liste.append((0,0,{'numero':i+1,'client':self.client.id}))
			self.seances = liste 



	#apres la prestation on cree le bon de commande puis la facture

	#@api.multi
	def action_print_convention(self):
		return self.env.ref('mya_shop.mya_report_convention_traitement').report_action(self)
		#return self.env['report'].get_action(self, 'mya_shop.report_convention_traitement')

	#@api.multi
	def return_action_to_open(self):
		self.ensure_one()
		xml_id = self.env.context.get('xml_id')
		if xml_id:
			res = self.env['ir.actions.act_window'].for_xml_id('mya_shop', xml_id)
			res.update(
				context=dict(self.env.context, default_prestation_id=self.id, group_by=False),
				domain=[('prestation_id', '=', self.id)]
				)
			return res
		return False
	#Controler le nombre de seances
	#def controle_nbre_seance()


class Seance(models.Model):
	_name ='prestation.seance'
	_description = 'seances de prestation'
	#_inherit = 'rv.prestation'
	numero = fields.Integer(string = "Numéro")
	prestation_id = fields.Many2one('prestation',string = "Prestation")
	observations = fields.Text(string = "Observations")
	state = fields.Selection([('faite','Faite'),('a_faire','A faire')],string="Etat",default="a_faire")
	client = fields.Many2one('res.partner',string="Client",domain="[('customer','=',True)]" ,ondelete="cascade",required=True)
	date_heure = fields.Datetime(string="Date et heure ")
	date_rv = fields.Date(string="Date",compute="_compute_date_heure",store=True)
	heure_rv = fields.Char(string="Heure",compute="_compute_date_heure",store=True)

	#@api.one
	@api.depends('date_heure')
	def _compute_date_heure(self):
		for record in self:
			record.date_rv ,record.heure_rv = fields.Datetime.to_string(record.date_heure).split(' ')[0] ,fields.Datetime.to_string(record.date_heure).split(' ')[1]


	#@api.multi
	def seance_faite(self):
		for record in self:
			record.state = 'faite'

	def unlink(self):
		for record in self:
			if record.state == 'faite':
				raise UserError(_("Vous ne pouvez pas supprimer une seance dèja faite."))
		return super(Seance,self).unlink()


		

class Partner(models.Model):
	_name = 'res.partner'
	_inherit = 'res.partner'

	#rv_ids = fields.One2many('rv.prestation','client',string="RV")
	#rv_count = fields.Integer(string="RV",compute="_compute_rv_count")
	age = fields.Integer(string = "AGE")
	

	#@api.multi
	def return_action_to_open(self):
		self.ensure_one()
		xml_id = self.env.context.get('xml_id')
		if xml_id:
			res = self.env['ir.actions.act_window'].for_xml_id('mya_shop', xml_id)
			res.update(
				context=dict(self.env.context, default_client=self.id, group_by=False),
				domain=[('client', '=', self.id)]
				)
			return res
		return False



class AccountInvoice(models.Model):
	_name = 'account.move'
	_inherit = 'account.move'
	prestation_id = fields.Many2one('prestation')

	@api.onchange('prestation_id')
	def onchange_prestation_id(self):
		if not self.prestation_id:
			return 
		partner = self.prestation_id.client
		#self.prestation_id.write({'state':'facture'})
		self.partner_id = partner.id
		invoice_lines = []
		invoice_lines.append((0,0,{
					'name': self.prestation_id.product.name,
					'product_id':self.prestation_id.product.id,
					'account_id':self.journal_id.default_debit_account_id.id,
					#'product_uom':self.prestation_id.product.uom_id,
					'quantity':1.0,
					'price_unit':self.prestation_id.product.lst_price,
			}))	
		self.invoice_line_ids = invoice_lines

	@api.model
	def create(self,data):
		if 'prestation_id' in data:
			prestation = self.env['prestation'].browse(data['prestation_id'])
			if prestation:
				prestation.write({'state':'facture'})
		return super(AccountInvoice,self).create(data)



class SaleOrder(models.Model):
	_name = 'sale.order'
	_inherit = 'sale.order'
	prestation_id = fields.Many2one('prestation')
	


	@api.onchange('prestation_id')
	def onchange_prestation_id(self):
		if not self.prestation_id:
			return
		partner = self.prestation_id.client 
		self.partner_id = partner.id
		order_lines = []

		order_lines.append((0,0,{
					'name': self.prestation_id.product.name,
					'product_id':self.prestation_id.product.id,
					'product_uom':self.prestation_id.product.uom_id,
					'product_uom_qty':1.0,
					'price_unit':self.prestation_id.product.lst_price,
			}))
		self.order_line = order_lines
#stock.location
#pos.config

class hrEmploye(models.Model):
	_name = 'hr.employee'
	_inherit = 'hr.employee'

	boutique_id = fields.Many2one('pos.config',string="Lieu de travail")

class stockPicking(models.Model):
	_name = 'stock.picking'
	_inherit = 'stock.picking'
	demande_appro_id = fields.Many2one('demande.appro',string="Demande appro")

class stockInventory(models.Model):
	_name = 'stock.inventory'
	_inherit = 'stock.inventory'

	demande_appro_id = fields.Many2one('demande.appro',string="Demande appro")
	#versement_quotidien_id = fields.Many2one('versement_quotidien',string = "Versement quotidien")
#Demande d'approvisionnement

class StockInventoryLine(models.Model):
	_name = 'stock.inventory.line'
	_inherit = 'stock.inventory.line'


class ApproLines(models.Model):
	_name='appro.lines'
	_description = 'Appro lines'
	product_id = fields.Many2one('product.product',string="Désignation",domain="[('type','=','product')]")
	quantite = fields.Integer(string="Quantité",default=0)
	demande_appro_id = fields.Many2one('demande.appro',string="Demande")
	stock_initial = fields.Integer(string='Stock initial',default=0,compute='compute_stock_initial',store=True)
	stock_final = fields.Integer(string='Stock final',compute='_compute_stock_final',store=True)

	
	

	@api.depends('product_id')
	def compute_stock_initial(self):
		for record in self:
			if record.product_id and record.demande_appro_id:
				#*********************New*************************
				stock_quant_ids = self.env['stock.quant'].search([('product_id','=',record.product_id.id),('location_id','=',record.demande_appro_id.location_id.id)])
				#record.stock_initial = sum(stock_quant_ids.mapped('qty'))
				record.stock_initial = sum(stock_quant_ids.mapped('quantity'))#sum(stock_quant_ids.mapped('inventory_quantity'))
			#*********************New*************************
	@api.depends('quantite','stock_initial')
	def _compute_stock_final(self):
		for record in self:
			record.stock_final = record.stock_initial + record.quantite


class StockPicking(models.Model):
	_name = 'stock.picking'
	_inherit = 'stock.picking'

	demande_appro_id = fields.Many2one('demande.appro',string="Demande appro")




class DemandeAppro(models.Model):#object stock.picking 
	_name = 'demande.appro'
	_description = 'Demande appro'
	_rec_name = 'numero_demande'

	numero_demande = fields.Char(string="N°")
	date_demande = fields.Date(default=fields.Date.context_today)
	demandeur = fields.Many2one('hr.employee',string="Demandeur",readonly=True)
	valide_par = fields.Many2one('hr.employee',string="Validé par")
	date_validation = fields.Date(string="Date de validation")
	#stock_picking_id = fields.Many2one('stock.picking',string="Transfert")
	location_id = fields.Many2one('stock.location',string="Emplacement")
	location_grand_stock = fields.Many2one('stock.location',string="Grand stock")
	appro_line_ids = fields.One2many('appro.lines','demande_appro_id',string="Approvisionnements")
	state = fields.Selection([('draft',"Brouillon"),('confirme','Confirmé'),('valide','Validé'),('annule','annulé')],default='draft',string="Etat")



	@api.model
	def create(self,data):
		data['numero_demande'] = self.env['ir.sequence'].next_by_code('demande.appro')
		#delete
		return super(DemandeAppro,self).create(data)

		#create stock.picking 
		#calcul stock initial stock.inventory

	#@api.multi
	def unlink(self):
		for record in self:
			if record.state == 'valide':
				raise UserError(_("Vous ne pouvez pas supprimer une demande d'approvisionnement dèja validée."))
		return super(DemandeAppro,self).unlink()



	#@api.multi
	def valider(self):
		for record in self:
			self.state = 'valide'
			self.date_validation = fields.Date.context_today(record)
			current_employee = self.env['hr.employee'].search([('user_id','=',self.env.user.id)],limit=1)
			if current_employee:
				self.valide_par = current_employee.id
			#Transfert
			if record.appro_line_ids:
				location_dest_id = record.location_id

				#liste = []
				#type de preparation
				#********************************
				warehouse = self.env['stock.warehouse'].search([])
				if warehouse:
					picking_type = self.env['stock.picking.type']\
									   .search([
									   	('code','=','internal'),
									   	('default_location_src_id','=',record.location_grand_stock.id),
									   	('default_location_dest_id','=',location_dest_id.id)],limit = 1)
					if picking_type:
						obj = self.env['stock.picking'].create({'picking_type_id':picking_type.id,'location_id':record.location_grand_stock.id,'location_dest_id':location_dest_id.id,'demande_appro_id':record.id})
						appro_lines = []
						#if appro_line_ids:
						for line in record.appro_line_ids:
							appro_lines.append((0,0,{
									'product_id':line.product_id.id,
									'product_uom_qty':line.quantite,
									'product_uom':line.product_id.uom_id.id,
									'location_id':record.location_grand_stock.id,
									'location_dest_id':location_dest_id.id,
									'name':'TEST',
									'state':'draft',	
							}))
						obj.write({'move_ids_without_package':appro_lines})
						#marquer à faire
						obj.action_confirm()
						#Verifier la disponibilite
						obj.action_assign()
						#Valider
						obj.button_validate()
						#obj.do_new_transfer()
						#marquer à faire : action_confirm
						#valider : do_new_transfer
						#self.move_lines = appro_lines
						#for appro_line in record.appro_line_ids:

					
			#stock.picking


	#@api.multi
	def send_mail_information(self):
		template = self.env.ref('mya_shop.email_template_demande_appro')
		self.env['mail.template'].browse(template.id).send_mail(self.id)
		#forcer l'envoi
		mails = self.env['mail.mail'].search([('state','=','outgoing')])
		if mails:
			for courriel in mails:
				courriel.send()


	#@api.multi
	def annuler(self):
		for record in self:
			self.state = 'annule'

	#@api.multi
	def confirmer(self):
		for record in self:
			self.state='confirme'
			#send mail for notificate
			self.send_mail_information()


	#@api.multi
	def action_print_demande_appro(self):
		return self.env.ref('mya_shop.mya_report_demande_appro').report_action(self)
		#return self.env['report'].get_action(self, 'mya_shop.report_demande_appro')


	@api.model
	def default_get(self,default_fields):
		res = super(DemandeAppro,self).default_get(default_fields)
		current_employee = self.env['hr.employee'] \
							   .search(
							   	[('user_id','=',self.env.user.id)],limit=1)
		if 'demandeur' in default_fields and current_employee:
			res.update({
					'demandeur' : current_employee.id,
				})
		if current_employee.boutique_id:
			res.update({'location_id':current_employee.boutique_id.picking_type_id.default_location_src_id.id})

		dest_loc = self.env['stock.location'].search([('complete_name','like','WH/Stock')],limit=1)
		if 'location_grand_stock' in default_fields and dest_loc:
			res.update({
					'location_grand_stock' : dest_loc.id
				})
		return res

	@api.onchange('demandeur')
	def onchange_demandeur(self):
		if self.demandeur.boutique_id:
			self.location_id = self.demandeur.boutique_id.picking_type_id.default_location_src_id.id
		

class DemandeRetraitProduit(models.Model):
	_name = 'demande.retrait_produit'
	_description = "Demande de retrait d'un produit dans un stock"

	date = fields.Date(string="Date",default=fields.Date.context_today)
	demandeur = fields.Many2one('hr.employee',string = "Demandeur")
	boutique_id = fields.Many2one('pos.config',string="Boutique",required = True)
	demande_lines = fields.One2many('demande.retrait_produit_line','demande_retrait_produit_id',string="produits à retirer")
	state = fields.Selection([('draft','Brouillon'),('valide','Validé')],default="draft",string="Etat")
	motif = fields.Text(string = "Motif")

	@api.model
	def default_get(self,default_fields):
		res = super(DemandeRetraitProduit,self).default_get(default_fields)
		current_employee = self.env['hr.employee'] \
							   .search(
							   	[('user_id','=',self.env.user.id)],limit=1)
		if 'demandeur' in default_fields and current_employee:
			res.update({
						'demandeur': current_employee.id,
				})

		return res

	def unlink(self):
		for record in self:
			if record.state == 'valide':
				raise UserError(_("Vous ne pouvez pas supprimer une demande de retrait de produit dèja validée."))
		return super(DemandeRetraitProduit,self).unlink()

	@api.onchange('demandeur')
	def onchange_demandeur(self):
		if self.demandeur.boutique_id:
			self.boutique_id = self.demandeur.boutique_id.id

	#@api.multi
	def valider(self):
		for record in self:
			if not record.demande_lines:
				raise UserError(_("Veuillez sélectionner au moins un produit à retirer."))
			for line in record.demande_lines:
				scrap = self.env['stock.scrap'].create({'product_id':line.product_id.id,'scrap_qty':line.quantite,'location_id':record.boutique_id.picking_type_id.default_location_src_id.id,'product_uom_id':line.product_id.uom_id.id})
				scrap.action_validate()
			record.state = 'valide'


class DemandeRetraitProduitLine(models.Model):
	_name = 'demande.retrait_produit_line'
	_description = 'Ligne de demande de retrait'
	demande_retrait_produit_id = fields.Many2one('demande.retrait_produit',string = "Demande retrait")
	product_id = fields.Many2one('product.product',string = "Produit",domain="[('type','=','product')]",required=True)
	quantite = fields.Integer(string = "Quantité",default=1)

