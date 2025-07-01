import json
from time import sleep

from odoo.tests.common import TransactionCase


class TestMisReportStoredResultIntegration(TransactionCase):

    def setUp(self):
        super(TestMisReportStoredResultIntegration, self).setUp()
        partner_model_id = self.env.ref("base.model_res_partner").id
        partner_create_date_field_id = self.env.ref(
            "base.field_res_partner_create_date"
        ).id
        partner_debit_field_id = self.env.ref("account.field_res_partner_debit").id
        self.report = self.env["mis.report"].create(
            dict(
                name="test report",
                subkpi_ids=[
                    (0, 0, dict(name="sk1", description="subkpi 1", sequence=1)),
                    (0, 0, dict(name="sk2", description="subkpi 2", sequence=2)),
                ],
                query_ids=[
                    (
                        0,
                        0,
                        dict(
                            name="partner",
                            model_id=partner_model_id,
                            field_ids=[(4, partner_debit_field_id, None)],
                            date_field=partner_create_date_field_id,
                            aggregate="sum",
                        ),
                    )
                ],
            )
        )
        self.report_instance = self.env["mis.report.instance"].create(
            {
                "name": "Test Stored Result Report",
                "report_id": self.report.id,
            }
        )
        self.Result = self.env["mis.report.stored.result"]

    def test_01_compute_stores_result(self):
        """
        Verifica que la primera llamada a compute() crea una entrada en mis.report.stored.result.
        """
        self.report_instance.compute()
        stored_entry = self.Result.search(
            [("report_instance_id", "=", self.report_instance.id)]
        )
        self.assertEqual(len(stored_entry), 1)
        self.assertTrue(stored_entry.computation_result)

    def test_02_compute_uses_stored_result(self):
        """
        Verifica que una segunda llamada usa el stored_result
        """
        self.report_instance.compute()
        stored_result = self.Result.search(
            [("report_instance_id", "=", self.report_instance.id)]
        )
        modified_result = {"data": "test"}
        stored_result.computation_result = json.dumps(modified_result)
        result = self.report_instance.compute()
        self.assertEqual(result, modified_result)

    def test_03_bypass_stored_result_update(self):
        """
        Verifica que bypass_stored_result=True fuerza un recálculo y actualiza last_computed.
        Esto significa que se generó un nuevo recalculo del resultado.
        """
        self.report_instance.compute()
        stored_result = self.Result.search(
            [("report_instance_id", "=", self.report_instance.id)]
        )
        original_last_computed = stored_result.last_computed
        self.report_instance.with_context(bypass_stored_result=True).compute()
        self.assertNotEqual(stored_result.last_computed, original_last_computed)

    def test_04_check_no_duplicate(self):
        """
        Verifica que los recálculos actualizan el stored_result en lugar de crear duplicados.
        """
        self.Result.search(
            [("report_instance_id", "=", self.report_instance.id)]
        ).unlink()
        self.report_instance.compute()
        self.report_instance.with_context(bypass_stored_result=True).compute()
        record_count = self.Result.search_count(
            [("report_instance_id", "=", self.report_instance.id)]
        )
        self.assertEqual(record_count, 1)
