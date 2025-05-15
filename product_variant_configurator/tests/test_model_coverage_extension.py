from odoo.tests.common import TransactionCase

class TestModelCoverageExtension(TransactionCase):
    def test_product_category_write_triggers_variant_creation(self):
        category = self.env['product.category'].create({'name': 'Test', 'no_create_variants': True})
        template = self.env['product.template'].create({
            'name': 'Template with Empty',
            'no_create_variants': 'empty',
            'categ_id': category.id
        })
        self.assertEqual(len(template.product_variant_ids), 1)
        category.write({'no_create_variants': False})
        self.assertTrue(len(template.product_variant_ids) > 1)

    def test_onchange_attribute_id_clears_values(self):
        attr = self.env['product.attribute'].create({'name': 'Test Attr'})
        value = self.env['product.attribute.value'].create({'name': 'Val', 'attribute_id': attr.id})
        line = self.env['product.template.attribute.line'].new({
            'attribute_id': attr.id,
            'value_ids': [(6, 0, [value.id])]
        })
        line._onchange_attribute_id_clean_value()
        self.assertFalse(line.value_ids)

    def test_create_value_links_to_existing_line(self):
        attr = self.env['product.attribute'].create({'name': 'Attr'})
        template = self.env['product.template'].create({'name': 'Product'})
        self.env['product.template.attribute.line'].create({
            'product_tmpl_id': template.id,
            'attribute_id': attr.id
        })
        value = self.env['product.attribute.value'].with_context(
            template_for_attribute_value=template.id
        ).create([{'name': 'Val1', 'attribute_id': attr.id}])
        self.assertIn(value, template.attribute_line_ids.value_ids)

    def test_compute_price_rule_with_template_and_uom_context(self):
        uom_unit = self.env.ref("uom.product_uom_unit")
        template = self.env['product.template'].create({
            'name': 'Priced Template',
            'list_price': 100.0,
            'uom_id': uom_unit.id,
            'uom_po_id': uom_unit.id
        })
        pricelist = self.env['product.pricelist'].create({'name': 'Test'})
        with self.env.cr.savepoint():
            pricelist = pricelist.with_context(uom=uom_unit.id)
            rules = pricelist._compute_price_rule(template, 1.0)
            self.assertIsInstance(rules, dict)

    def test_possible_value_ids_filtered_correctly(self):
        attr = self.env['product.attribute'].create({'name': 'Attr'})
        value1 = self.env['product.attribute.value'].create({'name': 'A', 'attribute_id': attr.id})
        template = self.env['product.template'].create({
            'name': 'Test Product',
            'attribute_line_ids': [(0, 0, {
                'attribute_id': attr.id,
                'value_ids': [(6, 0, [value1.id])]
            })]
        })
        conf_attr = self.env['product.configurator.attribute'].create({
            'product_tmpl_id': template.id,
            'attribute_id': attr.id,
            'owner_model': 'product.product',
            'owner_id': 1
        })
        self.assertIn(value1, conf_attr.possible_value_ids)