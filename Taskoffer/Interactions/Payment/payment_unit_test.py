import pytest
from Interactions.Payment.payment_schema import WalletSchema
from Interactions.Payment.payment_service import *

# ===================================================================
# =============== FILL WALLET TESTS =========================
# ==================================================================


# Успешное пополнение кошелька
def test_fill_wallet_success(db, client_user, client_wallet):

    data = WalletSchema(amount=15000)

    result = fill_wallet(data=data, user_id=client_user.id, db=db)

    assert result['status'] == "success"
    assert result['balance'] == 35000


# Ошибка что кошелек не найден
def test_fill_wallet_not_found_fail(db, client_user, client_wallet):

    data = WalletSchema(amount=15000)

    db.delete(client_wallet)
    db.commit()

    with pytest.raises(HTTPException) as exc:
        fill_wallet(data=data, user_id=client_user.id, db=db)

    assert exc.value.status_code == 404



# ==================================================================
# =============== WITHDRAW WALLET TESTS =======================
# ==================================================================

# Успешное снятие с кошелька
def test_withdraw_wallet_success(db, client_user, client_wallet):

    data = WalletSchema(amount=10000)

    result = withdraw_wallet(data=data, user_id=client_user.id, db=db)

    assert result['status'] == "success"
    assert result['balance'] == 10000


# Ошибка что кошелек не найден
def test_withdraw_wallet_not_found_fail(db, client_user, client_wallet):

    data = WalletSchema(amount=15000)

    db.delete(client_wallet)
    db.commit()

    with pytest.raises(HTTPException) as exc:
        withdraw_wallet(data=data, user_id=client_user.id, db=db)

    assert exc.value.status_code == 404
    assert client_wallet.balance == 20000


# Ошибка что недостаточно средств
def test_withdraw_wallet_not_found_fail(db, client_user, client_wallet):

    data = WalletSchema(amount=35000)

    with pytest.raises(HTTPException) as exc:
        withdraw_wallet(data=data, user_id=client_user.id, db=db)

    assert exc.value.status_code == 400
    assert client_wallet.balance == 20000


# =========================================================================
# ===================== PROCESS_JOB_PAYMENT TESTS ========================
# ============================================================================

# Успешная заморозка средств при создании работы
def test_process_job_payment_start_job_success(db, job, client_user, deal, client_wallet):
    action = DealPaymentAction.START_JOB
    
    result = process_job_payment(action=action, amount=job.price, db=db, client_id=client_user.id, deal_id=deal.id)

    assert result['message'] == "ok"


# Успешное завершение работы и оплата работнику
def test_process_job_payment_complete_success(db, job, deal, worker_user, worker_wallet):
    action = DealPaymentAction.COMPLETE_DEAL
    
    result = process_job_payment(
        action=action, 
        amount=job.price,
        db=db, 
        deal_id=deal.id, 
        worker_id=worker_user.id
    )

    assert result['message'] == "ok"
    assert worker_wallet.balance == job.price

# Успешная отмена сделки
def test_process_job_payment_cancel_deal_success(db, client_user, client_wallet, job, deal):
    action = DealPaymentAction.DEAL_CANCEL

    result = process_job_payment(action=action, amount=job.price, db=db, client_id=client_user.id, deal_id=deal.id)
    
    assert result['message'] == "ok"
    assert client_wallet.balance == 35000

# Успешная отмена работы
def test_process_job_payment_cancel_job_success(db, client_user, client_wallet, job, deal):
    action = DealPaymentAction.JOB_CANCEL

    result = process_job_payment(action=action, amount=job.price, db=db, client_id=client_user.id, deal_id=deal.id)
    
    assert result['message'] == "ok"
    assert client_wallet.balance == 35000


# Ошибка что недостаточно средств для создания работы
def test_proccess_job_payment_not_enough_balance_fail(db, client_user, client_wallet):
    action = DealPaymentAction.START_JOB

    with pytest.raises(HTTPException) as exc:
        process_job_payment(action=action, amount=50000, client_id=client_user.id, db=db)

    assert exc.value.status_code == 400

