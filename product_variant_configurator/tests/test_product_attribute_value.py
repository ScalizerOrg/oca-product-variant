from odoo.tests.common import TransactionCase


class TestProductAttributeValue(TransactionCase):
    def setUp(self):
        super().setUp()

        # Create a product template (the associated template)
        self.product_template = self.env["product.template"].create(
            {
                "name": "Test Product Template",
            }
        )

        # Create a product attribute
        self.product_attribute = self.env["product.attribute"].create(
            {
                "name": "Test Attribute",
            }
        )

    def test_create_attribute_value_linked_to_template(self):
        # Set the context to link the attribute value to the template
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

        # Check that the attribute value was created
        self.assertEqual(
            attribute_value.name,
            "Test Value",
            "The attribute value was not created correctly.",
        )
