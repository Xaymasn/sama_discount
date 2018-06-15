# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

# Modification du modèle de devis
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.depends('order_line.price_total')
    def _amount_all(self):
        # Calcul des totaux du devis
        for order in self:
            amount_untaxed = amount_tax = amount_discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                amount_discount += (line.product_uom_qty * line.price_unit * line.discount)/100
                
            amount_discount_negative = (-1)*amount_discount

            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_discount': order.pricelist_id.currency_id.round(amount_discount),
                'amount_discount_negative': order.pricelist_id.currency_id.round(amount_discount_negative),
                'amount_total': amount_untaxed + amount_tax,
                'amount_without_discount': amount_untaxed + amount_discount,
            })
    # Le type de remise
    discount_type = fields.Selection(
            [('percent', 'Pourcentage'), ('amount', 'Montant fixe')], 
            string='Type de remise',
            readonly=True,
            states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, default='percent'
        )
    # Le taux de remise
    discount_rate = fields.Float('Remise', digits=dp.get_precision('Account'), readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    # Montant sans taxe
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    # Montant total des taxes
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    # Montant Total
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    # Montant de la remise
    amount_discount = fields.Monetary(string='Remise', store=True, readonly=True, compute='_amount_all', digits=dp.get_precision('Account'), track_visibility='always')
    # Montant négatif de la remise (juste utilisé à des fins d'affichage)
    amount_discount_negative = fields.Monetary(string='Remise', store=True, readonly=True, compute='_amount_all', digits=dp.get_precision('Account'), track_visibility='always')
    # Montant sans rabais (coût initial avant rabais)
    amount_without_discount = fields.Monetary(string='Montant initial', store=True, readonly=True, compute='_amount_all', digits=dp.get_precision('Account'), track_visibility='always')
    
    # Si un des champs définis est mis à jour, on met à jour le taux de rabais
    @api.onchange('discount_type', 'discount_rate', 'order_line')
    def supply_rate(self):
        for order in self:
            # Si le type de remise est en pourcentage, on applique ce taux sur toutes les lignes
            if order.discount_type == 'percent':
                for line in order.order_line:
                    line.discount = order.discount_rate
            # Sinon, on utilise le montant de la valeu
            else:
                total = discount = 0.0
                for line in order.order_line:
                    total += round((line.product_uom_qty * line.price_unit))
                # Ici on calcule la valeur en % (pourcent) du montant fixe de la remise. Parceque Odoo utilise des valeurs en % pour calculer les remises
                if order.discount_rate != 0:
                    discount = (order.discount_rate / total) * 100
                else:
                    discount = order.discount_rate
                for line in order.order_line:
                    line.discount = discount

    @api.multi
    def _prepare_invoice(self,):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'discount_type': self.discount_type,
            'discount_rate': self.discount_rate
        })
        return invoice_vals

    
    @api.multi
    def button_dummy(self):
        self.supply_rate()
        return True     

# Modification du modèle de Taxes
class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.multi
    def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None):
        if len(self) == 0:
            company_id = self.env.user.company_id
        else:
            company_id = self[0].company_id
        if not currency:
            currency = company_id.currency_id
        taxes = []
        prec = currency.decimal_places
        round_tax = False if company_id.tax_calculation_rounding_method == 'round_globally' else True
        round_total = True
        if 'round' in self.env.context:
            round_tax = bool(self.env.context['round'])
            round_total = bool(self.env.context['round'])

        if not round_tax:
            prec += 5
        # total_excluded = total_included = base = round(price_unit * quantity, prec)
        total_excluded = total_included = base = (price_unit * quantity)

        for tax in self.sorted(key=lambda r: r.sequence):
            if tax.amount_type == 'group':
                ret = tax.children_tax_ids.compute_all(price_unit, currency, quantity, product, partner)
                total_excluded = ret['total_excluded']
                base = ret['base']
                total_included = ret['total_included']
                tax_amount = total_included - total_excluded
                taxes += ret['taxes']
                continue

            tax_amount = tax._compute_amount(base, price_unit, quantity, product, partner)
            if not round_tax:
                tax_amount = round(tax_amount, prec)
            else:
                tax_amount = currency.round(tax_amount)

            if tax.price_include:
                total_excluded -= tax_amount
                base -= tax_amount
            else:
                total_included += tax_amount
            
            tax_base = base
            
            if tax.include_base_amount:
                base += tax_amount

            taxes.append({
                'id': tax.id,
                'name': tax.with_context(**{'lang': partner.lang} if partner else {}).name,
                'amount': tax_amount,
                'sequence': tax.sequence,
                'account_id': tax.account_id.id,
                'refund_account_id': tax.refund_account_id.id,
                'analytic': tax.analytic,
                'base': tax_base,
            })
        return {
            'taxes': sorted(taxes, key=lambda k: k['sequence']),
            'total_excluded': total_excluded,
            'total_included': total_included,
            'base': base,
    }

    # Modification du modèle des "Lignes de commandes"
    class SaleOrderLine(models.Model):
        _inherit = "sale.order.line"

        discount = fields.Float(string='Discount (%)', digits=(16, 20), default=0.0)