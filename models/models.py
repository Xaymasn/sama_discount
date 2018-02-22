# -*- coding: utf-8 -*-

from odoo import models, fields, api

class remiseglobale(models.Model):
    _inherit = 'sale.order'
    Remise = fields.Monetary( default='0', string='Remise Globale', )
    RemiseCalculated = fields.Monetary(compute='_calcul_remise')

    """
    On fait en sorte que la remise soit une valeur négative
    """
    @api.depends('Remise')
    def _calcul_remise(self):
        if Remise > 0:
            self.RemiseCalculated = -1 * Remise
        else :
            self.RemiseCalculated = Remise

    """
    Calcule les Sous-Totaux de la commande.
    _compute_amount() est une fonction de Odoo qu'on override, ici.
    On a juste modifié la ligne 'self.amount_untaxed' en ajoutant + 'RemiseCalculated' à la fin. 
    Tout le reste est du code Odoo
    """
    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type', 'RemiseCalculated')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids) + RemiseCalculated
        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign