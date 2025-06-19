from odoo.tests.common import TransactionCase


class TestProductAttributeValue(TransactionCase):
    def setUp(self):
        super().setUp()

        # Create a product template (the associated template)
        self.product_template = self.env["product.template"].create(
            {"name": "Test Product Template"}
        )

        # Create a product attribute
        self.product_attribute = self.env["product.attribute"].create(
            {"name": "Test Attribute"}
        )

        # Create a sample attribute value for later use
        self.value1 = self.env["product.attribute.value"].create(
            {"name": "Initial Value", "attribute_id": self.product_attribute.id}
        )

    def test_create_attribute_value_linked_to_template(self):
        attribute_value = (
            self.env["product.attribute.value"]
            .with_context(template_for_attribute_value=self.product_template.id)
            .create(
                [
                    {
                        "name": "Test Value",
                        "attribute_id": self.product_attribute.id,
                    }
                ]
            )
        )

        self.assertEqual(
            attribute_value.name,
            "Test Value",
            "The attribute value was not created correctly.",
        )

    def test_name_search_limit_reached_scenario(self):
        for i in range(10):
            self.env["product.template"].create(
                {"name": f"Limit Test Template {i:02d}"}
            )

        results = self.env["product.template"].name_search("Limit Test", limit=3)
        self.assertLessEqual(len(results), 3)

        all_results = self.env["product.template"].name_search("Limit Test")
        self.assertGreaterEqual(len(all_results), 3)

    def test_template_create_variant_edge_cases_scenario(self):
        template = self.env["product.template"].create(
            {"name": "Edge Case Template", "no_create_variants": "no"}
        )

        result = template._create_variant_ids()
        self.assertTrue(result)

    def test_template_write_variant_creation_scenario(self):
        template = (
            self.env["product.template"]
            .with_context(check_variant_creation=True)
            .create(
                {
                    "name": "Write Test Template",
                    "no_create_variants": "yes",
                }
            )
        )

        initial_count = len(template.product_variant_ids)

        template.write({"no_create_variants": "no"})

        final_count = len(template.product_variant_ids)
        self.assertGreaterEqual(final_count, initial_count)

    def test_onchange_attribute_id_clears_values(self):
        attr = self.env["product.attribute"].create({"name": "Test Attr"})
        value = self.env["product.attribute.value"].create(
            {"name": "Val", "attribute_id": attr.id}
        )
        line = self.env["product.template.attribute.line"].new(
            {"attribute_id": attr.id, "value_ids": [(6, 0, [value.id])]}
        )

        self.assertTrue(line.value_ids)

        line._onchange_attribute_id_clean_value()
        self.assertFalse(line.value_ids)

    def test_create_value_links_to_existing_line(self):
        template = self.env["product.template"].create({"name": "Product"})

        line = self.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": template.id,
                "attribute_id": self.product_attribute.id,
                "value_ids": [(6, 0, [self.value1.id])],
            }
        )

        value = (
            self.env["product.attribute.value"]
            .with_context(template_for_attribute_value=template.id)
            .create([{"name": "New Value", "attribute_id": self.product_attribute.id}])
        )
        self.assertIn(value, line.value_ids)
