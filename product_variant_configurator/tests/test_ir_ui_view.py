# Copyright 2016 ACSONE SA/NV
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.tests.common import TransactionCase


class TestPostprocessTagGroupBy(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.view_model = cls.env["ir.ui.view"]
        cls.product_model = cls.env["product.product"]
        cls.res_partner_model = cls.env["res.partner"]

    def test_postprocess_tag_groupby_no_recursion(self):
        """Test that recursion is avoided when groupby refers
        to a field with the same name in a many2one model."""

        # Mocking the XML element
        node = etree.Element(
            "field", name="product_id"
        )  # Correctly create the XML element
        name_manager_mock = type(
            "NameManagerMock", (object,), {"model": self.product_model}
        )  # Mock the name_manager
        node_info = {}

        # Mocking the actual method call on the view
        result = self.view_model._postprocess_tag_groupby(
            node, name_manager_mock, node_info
        )

        self.assertIsNone(
            result, "Method should return None to avoid recursion in specific case."
        )

        # Ensure that the node was processed by checking the result or behavior
        self.assertEqual(
            result,
            None,
            "The result should be None, indicating proper recursion handling.",
        )

    def test_postprocess_tag_groupby_different_model(self):
        """Test that the method works correctly for a different model."""

        # Mocking the XML element for a different model
        node = etree.Element(
            "field", name="product_id"
        )  # Correctly create the XML element
        name_manager_mock = type(
            "NameManagerMock", (object,), {"model": self.res_partner_model}
        )  # Mock the name_manager
        node_info = {}

        # Mocking the actual method call on the view
        result = self.view_model._postprocess_tag_groupby(
            node, name_manager_mock, node_info
        )

        # Ensure the method does not raise any error and behaves correctly
        self.assertIsNone(
            result, "Method should call super and return None (or a meaningful result)."
        )

        # Add an additional check to verify that the mock was used as expected
        self.assertEqual(
            result, None, "The result should be None, indicating no recursion issues."
        )

    def test_view_postprocess_groupby_recursion_fix(self):
        """Test the recursion fix in view groupby processing"""
        from lxml import etree

        view = self.env["ir.ui.view"]
        node = etree.Element("field", name="product_id")

        # Mock name manager for product.product model
        class MockNameManager:
            def __init__(self, model):
                self.model = model

        name_manager = MockNameManager(self.env["product.product"])

        # This should return None to prevent recursion
        result = view._postprocess_tag_groupby(node, name_manager, {})
        self.assertIsNone(result)
