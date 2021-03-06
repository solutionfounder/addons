from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, vals):
        if "purchase_line_id" not in vals:  # Prevent recursion
            self.add_purchase_order_line_from_stock_move()
        res = super(StockMove, self).write(vals)
        return res

    @api.multi
    def add_purchase_order_line_from_stock_move(self):
        stock_move_to_add = self.filtered(
            lambda m: m.state == "done" and not m.purchase_line_id
        )
        for stock_move in stock_move_to_add:
            if not stock_move.picking_id.purchase_id:
                raise ValidationError(
                    _("At least one of the original products must be received")
                )
            stock_move.purchase_line_id = self.env[
                "purchase.order.line"
            ].create(
                {
                    "name": stock_move.name,
                    "product_id": stock_move.product_id.id,
                    "product_qty": stock_move.product_qty,
                    "qty_received": stock_move.product_qty,
                    "qty_invoiced": stock_move.product_qty,
                    "price_unit": stock_move.product_id.list_price,
                    "product_uom": stock_move.product_uom.id,
                    "order_id": stock_move.picking_id.purchase_id.id,
                    "date_planned": stock_move.date,
                }
            )
