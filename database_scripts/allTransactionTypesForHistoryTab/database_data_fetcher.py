import psycopg2
import json
from datetime import datetime, timedelta

def get_operations_from_db():
    connection = None
    try:
        # Подключаемся к базе данных
        connection = psycopg2.connect(
            user="postgres",
            password="postgres",
            host="localhost",
            port="5434",
            database="ibank"
        )
        cursor = connection.cursor()

        # Получаем все колонки из таблицы
        query_templates = """
        SELECT DISTINCT ON (txn_code) 
            id, operation_id, txn_code, txn_type, txn_status_internal, 
            txn_status_external, queue_step, is_under_processing, processing_id, 
            cbs_reference, msg_id, auth_stat, session_id, add_text, 
            account_debit_id, account_debit_no, account_debit_ccy, 
            account_debit_card_base_supp, account_credit_id, account_credit_no, 
            account_credit_ccy, account_credit_card_base_supp, amount_debit, 
            amount_debit_total, amount_credit, account_debit_branch_code, 
            account_credit_branch_code, counterparty, charge_account, exchange_rate, 
            cbs_load_first_status, cbs_load_first_status_timestamp, 
            cbs_load_second_status, cbs_load_second_status_timestamp, 
            cbs_rollback_status, cbs_rollback_timestamp, cbs_error_code, 
            cbs_err_desc, error_src, ipc_first_rollback_status, 
            ipc_first_rollback_timestamp, num_retries_reload, 
            num_retries_get_reference, backend_err_code, total_tax, total_charges, 
            branch_code, value_date, contract_status, service_provider_id, 
            oracle_replication_serial_ft, oracle_replication_serial_pc, created_at, 
            updated_at, confirmed_at, end_at, err_desc, customer_no_debit, 
            customer_no_credit, full_name_cyr_credit, full_name_lat_credit, 
            full_name_cyr_debit, full_name_lat_debit, cbs_reload_status, 
            cbs_reload_timestamp, ipc_credit_posting_status, 
            ipc_credit_posting_timestamp, ipc_credit_auth_row_number, 
            ipc_error_code, ipc_error_desc, exchange_rate_ccy, lcy_amount, 
            ipc_debit_posting_status, ipc_debit_posting_timestamp, 
            ipc_debit_auth_row_number, transaction_created, payment_purpose, 
            limit_date, data_version, account_debit_card_pan, 
            account_credit_card_pan, cbs_rollback_msg_id, ipc_debit_first_step_id, 
            ipc_debit_reload_first_step_status, 
            ipc_debit_reload_first_step_timestamp, 
            num_retries_ipc_debit_first_step_reload, 
            ipc_debit_reload_second_step_status, 
            ipc_debit_reload_second_step_timestamp, 
            num_retries_ipc_debit_second_step_reload, ipc_credit_first_step_id, 
            ipc_credit_reload_first_step_status, 
            ipc_credit_reload_first_step_timestamp, 
            num_retries_ipc_credit_first_step_reload, 
            ipc_credit_reload_second_step_status, 
            ipc_credit_reload_second_step_timestamp, 
            num_retries_ipc_credit_second_step_reload, knp, recipient_bank_bic, 
            recipient_name, deposit_id, clearing_recipient_acc_no, 
            charges_and_tax, prop_value, connector, connector_provider_id, 
            payment_code, pay_ref_1, pay_ref_2, sys_name, charges_lcy, 
            device_type, c_p_h, recipient_bank_swift, swift_recipient_acc_no, 
            swift_transfer_ccy, swift_correspondent_acc_no, swift_vo_code, 
            swift_inn, swift_kpp, swift_bin, swift_kbe, swift_knp, 
            swift_commission_type, swift_charges_main, swift_charges_extra, 
            swift_recipient_bank_branch, intermediary_bank_swift, 
            recipient_address, user_ref_no, charges_acc_id, charges_acc_no, 
            error_code, ipc_debit_error_code, ipc_credit_error_code, 
            execution_date, account_credit_prop_value, cbs_commission_reference, 
            account_credit_prop_type, ipc_credit_rollback_timestamp, 
            ipc_credit_rollback_status, ipc_debit_rollback_timestamp, 
            ipc_debit_rollback_status, ipk, iph, tax_code, region_code, 
            district_code, okmot_code, vehicle_number, additional_data, 
            exchange_deal_id, sp_status, sp_error_code, cbs_rollback_reference, 
            cbs_load_commission_status, cbs_load_commission_timestamp, 
            cbs_rollback_commission_status, num_retries_commission_reload, 
            num_retries_commission_get_reference, cbs_load_commission_msg_id, 
            cbs_load_commission_auth_stat, cbs_load_commission_status_timestamp, 
            cbs_rollback_commission_reference, cbs_rollback_commission_timestamp, 
            shop_order_id, deposit_type, term_of_deposit, deposit_rate, 
            their_ref_no, deposit_main_int_type, cbs_reload_commission_status, 
            cbs_rollback_commission_msg_id, cbs_reload_commission_timestamp, 
            cbs_rollback_commission_auth_stat, deposit_child_name, 
            contract_ref_no, account_commission_ccy, ipc_rollback_error_code, 
            maker_id, checker_1_id, checker_2_id, checker_1_status, 
            checker_2_status, checker_1_confirm_time, is_clearing_sent, 
            checker_2_confirm_time, cbs_load_commission_error_desc, 
            cbs_load_commission_error_code, template_id, is_salary, salary_type, 
            batch_table_id, swift_routing_no, column_134swift_knp, 
            money_transfer_type, batch_file_id, salary_dr_cr, cheque_number, 
            pay_ref_3, user_id, value_time
        FROM transactions 
        WHERE txn_status_internal = 'SUCCESS'
        ORDER BY txn_code, id DESC;
        """
        cursor.execute(query_templates)
        template_records = cursor.fetchall()

        # Получаем имена колонок
        column_names = [desc[0] for desc in cursor.description]

        # Преобразуем результаты в список словарей
        transactions_templates = []
        for record in template_records:
            transaction = {}
            for i, value in enumerate(record):
                # Конвертируем числовые значения в строки для JSON
                if isinstance(value, (int, float)):
                    transaction[column_names[i]] = str(value)
                # Обрабатываем NULL значения
                elif value is None:
                    transaction[column_names[i]] = ''
                # Обрабатываем datetime
                elif isinstance(value, datetime):
                    transaction[column_names[i]] = value.isoformat()
                else:
                    transaction[column_names[i]] = value
            transactions_templates.append(transaction)

        # Сохраняем в JSON файл
        with open('transaction_templates.json', 'w', encoding='utf-8') as f:
            json.dump(transactions_templates, f, ensure_ascii=False, indent=4)

        print(f"JSON файл успешно создан. Найдено {len(transactions_templates)} уникальных типов транзакций")
        return True

    except (Exception, psycopg2.Error) as error:
        print("Ошибка при работе с PostgreSQL:", error)
        return False

    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    get_operations_from_db()