# -*- coding: utf-8 -*-

from odoo import models, fields, api

class remiseglobale(models.Model):
    _inherit = 'sale.order'
    Remise = fields.Monetary( default='0', string='Remise', )
    RemiseCalculated = fields.Monetary(compute='_calcul_remise')

    @api.depends('Remise')
    def _calcul_remise(self):
        self.RemiseCalculated = -1 * Remise

    """
    Calcule le Total de la commande.
    _compute_amount_total() est une fonction de Odoo qu'on override, ici.
    """
    @api.depends('amount', 'amount_rounding', 'RemiseCalculated')
    def _compute_amount_total(self):
        for tax_line in self:
            tax_line.amount_total = tax_line.amount + tax_line.amount_rounding + tax_line.RemiseCalculated