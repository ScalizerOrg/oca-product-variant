# Copyright 2016 ACSONE SA/NV
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestProductConfiguratorAttribute(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ENVIRONMENTS
        cls.product_attribute = cls.env["product.attribute"]
        cls.product_attribute_value = cls.env["product.attribute.value"]
        cls.product_template_attribute_value = cls.env[
            "product.template.attribute.value"
        ]
        cls.product_configuration_attribute = cls.env["product.configurator.attribute"]
        cls.product_template = cls.env["product.template"].with_context(
            check_variant_creation=True
        )

        # Instances: product attribute
        cls.attribute1 = cls.product_attribute.create({"name": "Test Attribute 1"})

        # Instances: product attribute value
        cls.value1 = cls.product_attribute_value.create(
            {"name": "Value 1", "attribute_id": cls.attribute1.id}
        )
        cls.value2 = cls.product_attribute_value.create(
            {"name": "Value 2", "attribute_id": cls.attribute1.id}
        )

        # Instances: product template
        cls.product_template1 = cls.product_template.create(
            {
                "name": "Product template 1",
                "no_create_variants": "no",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attribute1.id,
                            "value_ids": [(6, 0, [cls.value1.id, cls.value2.id])],
                        },
                    )
                ],
            }
        )

    def test_product_configurator_attribute(self):
        template_value_1 = self.product_template_attribute_value.search(
            [
                ("product_tmpl_id", "=", self.product_template1.id),
                ("product_attribute_value_id", "=", self.value1.id),
            ],
            limit=1,
        )
        template_value_1.write({"price_extra": 100.00})

        conf_attr = self.product_configuration_attribute.create(
            {
                "product_tmpl_id": self.product_template1.id,
                "attribute_id": self.attribute1.id,
                "value_id": self.value1.id,
                "owner_model": "product.product",
                "owner_id": 1,
            }
        )

        self.assertEqual(conf_attr.price_extra, 100.00)
        self.assertEqual(conf_attr.possible_value_ids, self.attribute1.value_ids)

        product = self.product_template1.product_variant_id
        product.product_attribute_ids = conf_attr
        self.assertEqual(product.price_extra, 100.0)

    def test_possible_value_ids_filtered_correctly(self):
        attr = self.product_attribute.create({"name": "Attr"})
        value1 = self.product_attribute_value.create(
            {"name": "A", "attribute_id": attr.id}
        )
        template = self.product_template.create(
            {
                "name": "Test Product",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {"attribute_id": attr.id, "value_ids": [(6, 0, [value1.id])]},
                    )
                ],
            }
        )
        conf_attr = self.product_configuration_attribute.create(
            {
                "product_tmpl_id": template.id,
                "attribute_id": attr.id,
                "owner_model": "product.product",
                "owner_id": 1,
            }
        )
        self.assertIn(value1, conf_attr.possible_value_ids)

    def test_configurator_attribute_price_extra(self):
        template = self.product_template.create(
            {
                "name": "Price Test Template",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.attribute1.id,
                            "value_ids": [(6, 0, [self.value1.id])],
                        },
                    )
                ],
            }
        )

        ptav = self.product_template_attribute_value.search(
            [
                ("product_tmpl_id", "=", template.id),
                ("product_attribute_value_id", "=", self.value1.id),
            ]
        )
        ptav.price_extra = 50.0

        conf_attr = self.product_configuration_attribute.create(
            {
                "product_tmpl_id": template.id,
                "attribute_id": self.attribute1.id,
                "value_id": self.value1.id,
                "owner_model": "product.product",
                "owner_id": 1,
            }
        )

        self.assertEqual(conf_attr.price_extra, 50.0)


class TestTargetedProductCoverage(TransactionCase):
    """Targeted tests for product_product.py uncovered lines"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.attribute = cls.env["product.attribute"].create({"name": "Test Attr"})
        cls.value = cls.env["product.attribute.value"].create(
            {"name": "Test Value", "attribute_id": cls.attribute.id}
        )

    def test_build_attributes_domain_dict_format_scenario(self):
        template = self.env["product.template"].create(
            {
                "name": "Domain Test Template",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.attribute.id,
                            "value_ids": [(6, 0, [self.value.id])],
                        },
                    )
                ],
            }
        )

        dict_attrs = [{"attribute_id": self.attribute.id, "value_id": self.value.id}]
        domain, cont = self.env["product.product"]._build_attributes_domain(
            template, dict_attrs
        )
        self.assertIn(("product_tmpl_id", "=", template.id), domain)
        self.assertEqual(cont, 1)

        dict_attrs_no_value = [{"attribute_id": self.attribute.id, "value_id": False}]
        domain, cont = self.env["product.product"]._build_attributes_domain(
            template, dict_attrs_no_value
        )
        self.assertEqual(cont, 0)

    def test_check_duplicity_disabled_conditions_scenario(self):
        template = self.env["product.template"].create(
            {
                "name": "Duplicate Check Template",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.attribute.id,
                            "value_ids": [(6, 0, [self.value.id])],
                        },
                    )
                ],
            }
        )
        product = self.env["product.product"].create(
            {"name": "Duplicate Check Product", "product_tmpl_id": template.id}
        )

        with patch("odoo.tools.config", {"test_enable": False}):
            product._check_duplicity()
        product.with_context(test_check_duplicity=False)._check_duplicity()

    def test_configuration_validity_creating_variants_scenario(self):
        template = self.env["product.template"].create(
            {
                "name": "Validity Template",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.attribute.id,
                            "value_ids": [(6, 0, [self.value.id])],
                            "required": True,
                        },
                    )
                ],
            }
        )
        product = (
            self.env["product.product"]
            .with_context(creating_variants=True)
            .create({"name": "Validity Product", "product_tmpl_id": template.id})
        )
        product._check_configuration_validity()

    def test_product_name_get_newid_scenario(self):
        product = self.env["product.product"].new({"name": "Virtual Product"})
        result = product.name_get()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1], "Virtual Product")

    def test_product_create_attribute_conversion_scenario(self):
        template = self.env["product.template"].create(
            {
                "name": "Creation Template",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.attribute.id,
                            "value_ids": [(6, 0, [self.value.id])],
                        },
                    )
                ],
            }
        )
        product = self.env["product.product"].create(
            {
                "name": "Creation Product",
                "product_tmpl_id": template.id,
                "product_attribute_ids": [
                    (
                        0,
                        0,
                        {
                            "product_tmpl_id": template.id,
                            "attribute_id": self.attribute.id,
                            "value_id": self.value.id,
                            "owner_model": "product.product",
                        },
                    )
                ],
            }
        )
        self.assertTrue(product.product_template_attribute_value_ids)
